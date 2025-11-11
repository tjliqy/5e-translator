
from typing import List,Optional

from config import logger
from .bean import DocumentBean, PTTSW_ID_PREIX

def split_common_entry(origin_json: dict, prefix_id: str) -> (Optional[List[DocumentBean]]):
    """拆分entries字段中的条目，返回拆分后的SplitBean列表（暂未完成）

    Args:
        origin_json (dict): 原始json数据
        prefix_id (str): 前缀id，用于生成拆分后的json文件id

    Returns:
        Optional[List[SplitBean]]: 拆分后的SplitBean列表，若拆分失败则返回None
    """
    
    if "type" not in origin_json or not origin_json["type"]:
        logger.error(f"common entry json {prefix_id} not found type field or type is empty")
        return None
    res_bean_list = []
    if origin_json["type"] == "section":
        section_json = origin_json
        current_id = prefix_id
        section_name = origin_json["name"]
        
        # 去掉entries字段
        if "entries" in section_json:
            del section_json["entries"]
            for entry_index, entry in enumerate(section_json["entries"]):
                split_bean = DocumentBean(entry)
                split_bean.id = f"{prefix_id}-{entry_index}"
                res_bean_list.append(split_bean)

def split_bestiary(origin_json: dict, source:str) -> (Optional[List[DocumentBean]]):
    """检查bestiary-xxx.json是否符合拆分条件，符合则返回拆分后的SplitBean列表

    Args:
        origin_json (_type_): _description_
        prefix_id (str): 前缀id，用于生成拆分后的json文件id

    Returns:
        _type_: _description_
    """
    
    # 检查基础data字段是否存在
    if "monster" not in origin_json or not isinstance(origin_json["monster"], list):
        # logger.error(f"bestiary json {prefix_id} not found data field or data is not list")
        return None
    
    combine_info = {}
    res = []

    if "_meta" in origin_json.keys():
        _meta = origin_json["_meta"]
        combine_info["_meta"] = _meta
    else:
        _meta = {}
    combine_info["monster"] = []
    for item in origin_json["monster"]:
        document_bean = DocumentBean({
            "dataType" : "monster",
            "data": item,
            "name": item["name"] ,
            "type": "statblockInline",
        }, type="monster", source=source, _meta=_meta)
        res.append(document_bean)
        combine_info["monster"].append(PTTSW_ID_PREIX + document_bean._meta["pttsw_id"])
    return res, combine_info

def split_class(origin_json: dict, source:str) -> (Optional[List[DocumentBean]]):
    """检查class-xxx.json是否符合拆分条件，符合则返回拆分后的SplitBean列表

    Args:
        origin_json (_type_): _description_
        prefix_id (str): 前缀id，用于生成拆分后的json文件id

    Returns:
        _type_: _description_
    """
    combine_info = {}
    res = []
    if "_meta" in origin_json.keys():
        combine_info["_meta"] = origin_json["_meta"]
        _meta = origin_json["_meta"]
    else:
        _meta = {}
    # 检查基础data字段是否存在
    if "classFeature" not in origin_json or not isinstance(origin_json["classFeature"], list):
        # logger.error(f"class json {prefix_id} not found classFeature field or data is not list")
        return None
    combine_info["classFeature"] = []
    for item in origin_json["classFeature"]:
        document_bean = DocumentBean(item, type="classFeature", _meta=_meta)
        res.append(document_bean)
        combine_info["classFeature"].append(PTTSW_ID_PREIX + document_bean._meta["pttsw_id"])
    if "subclassFeature" in origin_json and isinstance(origin_json["subclassFeature"], list):
        combine_info["subclassFeature"] = []
        for item in origin_json["subclassFeature"]:
            document_bean = DocumentBean(item, type="subclassFeature", _meta=_meta)
            res.append(document_bean)
            combine_info["subclassFeature"].append(PTTSW_ID_PREIX + document_bean._meta["pttsw_id"])
    return res, combine_info

def split_normal_file(origin_json: dict, source:str, skip_keys: List[str] = []):
    """检查普通文件是否符合拆分条件，符合则返回拆分后的DocumentBean列表

    Args:
        origin_json (dict): 源Json解析后的对象
        prefix_id (str): 前缀id，用于生成拆分后的json文件id
        base_keys (List[str]): 基础key列表，用于检查基础data字段是否存在

    Returns:
        Optional[List[DocumentBean]]: 拆分后的DocumentBean列表，若拆分失败则返回None
    """
    res = []
    _meta = {}
    combine_info = {}
    for key, value in origin_json.items():
        if key == '_meta':
            combine_info[key] = value
            _meta = value
        elif key in skip_keys:
            combine_info[key] = value
            continue
        elif isinstance(value, list):
            combine_info[key] = []
            for item in value:
                document_bean = DocumentBean(item, type=key, _meta=_meta, source=source)
                res.append(document_bean)
                combine_info[key].append(PTTSW_ID_PREIX + document_bean._meta["pttsw_id"])
        else:
            combine_info[key] = value
    return res, combine_info
