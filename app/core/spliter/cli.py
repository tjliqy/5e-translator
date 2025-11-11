import os
import json
from logger_config import logger
from config import ORIGIN_5ETOOLS_DATA_DIR, SPLITED_5ETOOLS_DATA_DIR, COMBINE_INFO_DATA_DIR, COMBINED_5ETOOLS_DATA_DIR

from .funcs import SPLIT_FUNCS
# 根据来源（Source）放入不同的目录，并生成不同的文件
def split_origin_files(
        origin_5etoos_data_dir: str = ORIGIN_5ETOOLS_DATA_DIR,
        splited_data_dir: str = SPLITED_5ETOOLS_DATA_DIR,
        combine_info_dir: str = COMBINE_INFO_DATA_DIR,
    ) -> (list):
    # 检查目录是否存在
    if not os.path.exists(origin_5etoos_data_dir):
        logger.error(f"5etools data dir {origin_5etoos_data_dir} not exists")
        return []
    
    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(splited_data_dir):
        os.makedirs(splited_data_dir)
    # 检查合并信息目录是否存在，不存在则创建
    if not os.path.exists(combine_info_dir):
        os.makedirs(combine_info_dir)
    # 遍历目录下所有文件
    for root, dirs, files in os.walk(origin_5etoos_data_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 检查是否为json文件
            if not file_name.endswith(".json"):
                continue
            # 读取json文件内容
            for split_func in SPLIT_FUNCS:
                if file_name.startswith(split_func["prefix"]):
                    with open(file_path, "r") as f:
                        try:
                            origin_json = json.load(f)
                        except json.JSONDecodeError:
                            logger.error(f"5etools json file {file_path} decode error")
                            continue
                        # 计算来源Source
                        source = file_name[len(split_func["prefix"]):]
                        if source.endswith(".json"):
                            source = source[:-5]
                        # 调用split_func函数进行拆分
                        document_bean_list, combine_info = split_func["split_func"](origin_json, source, **split_func["args"])
                        # 检查拆分后的json列表是否为空
                        logger.info(f"5etools json 文件 {file_path} 切分出 {len(document_bean_list)} 个文档")
                        if not document_bean_list:
                            continue
                        # 遍历拆分后的json列表，每个json写入新文件
                        for split_json in document_bean_list:
                            # 检查相对路径是否存在，不存在则创建
                            split_file_path = os.path.join(splited_data_dir, split_json.path)
                            split_dir = os.path.dirname(split_file_path)
                            if not os.path.exists(split_dir):
                                os.makedirs(split_dir)
                            with open(split_file_path, "w") as f:
                                json.dump(split_json.__dict__(), f, ensure_ascii=False, indent=4)
                        
                        # 检查合并信息是否为空
                        if not combine_info:
                            continue
                        # 写入合并信息文件
                        # 计算合并信息文件路径
                        rel_file_path = os.path.join(os.path.relpath(root, origin_5etoos_data_dir), file_name)
                        combine_info_file_path = os.path.join(combine_info_dir, rel_file_path)
                        combine_dir = os.path.dirname(combine_info_file_path)
                        if not os.path.exists(combine_dir):
                            os.makedirs(combine_dir)
                        with open(combine_info_file_path, "w") as f:
                            json.dump(combine_info, f, ensure_ascii=False, indent=4)
                else:
                    continue
                

def combine_splited_files(
        splited_data_dir: str = SPLITED_5ETOOLS_DATA_DIR,
        combine_info_dir: str = COMBINE_INFO_DATA_DIR,
        combined_data_dir: str = COMBINED_5ETOOLS_DATA_DIR,
    ) -> (list):
    # 检查目录是否存在
    if not os.path.exists(splited_data_dir):
        logger.error(f"5etools splited data dir {splited_data_dir} not exists")
        return []
    # 检查合并信息目录是否存在
    if not os.path.exists(combine_info_dir):
        logger.error(f"5etools combine info dir {combine_info_dir} not exists")
        return []
    
    for root, dirs, files in os.walk(combine_info_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 检查是否为json文件
            if not file_name.endswith(".json"):
                continue
            # 读取json文件内容
            for split_func in SPLIT_FUNCS:
                if file_name.startswith(split_func["prefix"]):
                    
                    with open(file_path, "r") as f:
                        try:
                            combine_info = json.load(f)
                        except json.JSONDecodeError:
                            logger.error(f"5etools combine info file {file_path} decode error")
                            continue
                        
                        # 合并普通文件
                        combined_info = split_func["combine_func"](combine_info, splited_data_dir)
                            
                        combined_file_dir = os.path.join(combined_data_dir, os.path.relpath(root, combine_info_dir))
                        if not os.path.exists(combined_file_dir):
                            os.makedirs(combined_file_dir)
                        # 写入合并后的json文件
                        combined_file_path = os.path.join(combined_file_dir, file_name)
                        with open(combined_file_path, "w") as f:
                            json.dump(combined_info, f, ensure_ascii=False, indent=4)
