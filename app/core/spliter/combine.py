import json
import os

from logger_config import logger
from config import SPLITED_5ETOOLS_DATA_DIR
from .bean import PTTSW_ID_PREIX

from typing import List
def combine_bestiary(combine_info: dict, splited_data_dir:str = SPLITED_5ETOOLS_DATA_DIR):
    """合并bestiary文件

    Args:
        combine_info (dict): 合并后的json内容
        splited_data_dir (str, optional): 拆分后的文件目录. Defaults to SPLITED_5ETOOLS_DATA_DIR.
    """
    combined_info = {}
    if "_meta" in combine_info.keys():
        combined_info["_meta"] = combine_info["_meta"]
    combined_info["monster"] = []
    for pttsw_id in combine_info["monster"]:
        splited_data_file_path = os.path.join(splited_data_dir, pttsw_id[len(PTTSW_ID_PREIX):]+".json")
        if not os.path.exists(splited_data_file_path):
            logger.error(f"5etools splited data file {splited_data_file_path} not exists")
            continue
        with open(splited_data_file_path, "r") as f:
            try:
                split_json = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"5etools splited data file {splited_data_file_path} decode error")
                continue
            if "monster" not in split_json.keys():
                logger.error(f"5etools splited data file {splited_data_file_path} key monster not exists")
                continue
            combined_info["monster"].append(split_json["monster"]["data"])
    return combined_info

def combine_normal_file(combine_info: dict, splited_data_dir: str = SPLITED_5ETOOLS_DATA_DIR, skip_keys: List[str] = []):
    """合并普通文件

    Args:
        combined_info (dict): 合并后的json内容
        combined_file_path (str): 合并后的文件路径
    """
    combined_info = {}

    for key, value in combine_info.items():
        if key == "_meta":
            combined_info[key] = value
            continue
        if key in skip_keys:
            combined_info[key] = value
            continue
        elif isinstance(value, list):
            combined_info[key] = []
            for item in value:
                if not isinstance(item, str) or not item.startswith(PTTSW_ID_PREIX):
                    continue
                splited_data_file_path = os.path.join(splited_data_dir, item[len(PTTSW_ID_PREIX):]+".json")
                if not os.path.exists(splited_data_file_path):
                    logger.error(f"5etools splited data file {splited_data_file_path} not exists")
                    continue
                with open(splited_data_file_path, "r") as f:
                    try:
                        split_json = json.load(f)
                    except json.JSONDecodeError:
                        logger.error(f"5etools splited data file {splited_data_file_path} decode error")
                        continue
                    if key not in split_json.keys():
                        logger.error(f"5etools splited data file {splited_data_file_path} key {key} not exists")
                        continue
                    combined_info[key].append(split_json[key])
        else:
            combined_info[key] = value
            continue
    return combined_info