
# file_loader
# output: files
# 
# json_job_gen
# jobs
# kimi_pool
# res

import os
import json
from config import *
from langchain_core.runnables import RunnableLambda
from .file_work_info import FileWorkInfo
from typing import List

find_json_files = RunnableLambda(lambda root_folder: __find_json_files(root_folder))
write_translate_cache = RunnableLambda(lambda file_work_info: __write_translate_cache(file_work_info))
def __find_json_files(root_folder:str):
    # 判断root_folder是文件还是文件夹
    if os.path.isfile(root_folder):
        # 如果是文件则直接返回
        if root_folder.endswith('.json'):
            yield root_folder
    else:
        for root, _, files in os.walk(root_folder):
            for file in files:
                if file.endswith('.json'):
                    yield os.path.join(root, file)

def read_file(json_file):
    with open(json_file, 'r') as file:
        content = file.read()
        return content


def get_same_files(en_root_folder=EN_PATH, cn_root_folder='') :
    en_json_files = find_json_files(en_root_folder)
    res = []
    for en_json in en_json_files:
        rel_file_path = get_rel_path(en_json, en_root_folder)
        cn_json = os.path.join(cn_root_folder, rel_file_path)
        if not os.path.exists(cn_json):
            cn_json = ""
        res.append([en_json, cn_json])
    return res

def get_rel_path(en_file, en_root_folder=EN_PATH):
    return os.path.relpath(en_file, en_root_folder)

def __write_translate_cache(file_work_infos:List[FileWorkInfo]):
    """将翻译的中间过程obj及job_list写入缓存文件

    Args:
        file_work_infos (List[FileWorkInfo]): _description_

    Yields:
        _type_: _description_
    """
    for file_work_info in file_work_infos:
        out_path = os.path.join(OUT_PATH, file_work_info.json_path)  # 输出目录
        rel_out_dir = os.path.dirname(out_path)  # 输出文件的文件夹

        # 若输出文件夹不存在则创建
        if not os.path.exists(rel_out_dir):
            os.makedirs(rel_out_dir)

        # 写入替换好Job uuid的Json文件
        with open(out_path, 'w') as file:
            file.write(json.dumps(file_work_info.json_obj, ensure_ascii=False, indent=2))

        # 写入Job列表文件
        with open(out_path+'.jobs', 'w') as file:
            file.write('[\n')
            first_flag = True
            for j in file_work_info.job_list:
                if first_flag:
                    first_flag = False
                else:
                    file.write(',\n')
                file.write(json.dumps(
                    j, default=lambda o: o.__dict__, ensure_ascii=False, indent=2))
            file.write('\n]')
        file_work_info.json_path = out_path
        yield file_work_info
    
if __name__ == "__main__":
    for f in get_same_files():
        print(f)
    print(len(get_same_files()))
    # print(find_json_files(EN_PATH))