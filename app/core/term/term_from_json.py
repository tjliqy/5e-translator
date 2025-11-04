import json

from typing import Set
from langchain_core.runnables import Runnable

from app.core.utils import read_file, get_rel_path
from config import logger, SKIP_DIRS, SKIP_FILES
from app.core.bean import Term
from app.core.utils import get_tag_from_rel_path

class TermFromJson(Runnable):
    """从5et的Json文件加载术语

    Args:
        Runnable (_type_): _description_
    """
    def __init__(self):
        self.term_set: Set[Term] = set()
    
    def invoke(self, input, config=None, **kwargs):
        """从Json文件中加载术语

        Args:
            input (str): Json文件路径
        """
        inputs = [input] if isinstance(input, str) else input

        for i in inputs:
            logger.info(f"开始解析{i}中的Json")
            self.json_2_term(i)
            yield self.term_set
        
        
    def json_2_term(self, json_file: str):
        """从Json文件中加载术语

        Args:
            json_file (str): Json文件路径
        """
        self.term_set: Set[Term] = set()

        
        self.rel_path = get_rel_path(json_file)
        
        self.tag = get_tag_from_rel_path(self.rel_path)
        # 跳过文件夹
        if any(skip_dir in self.rel_path for skip_dir in SKIP_DIRS):
            # return None, None, False
            return
        # 跳过文件
        if self.rel_path in SKIP_FILES:
            # return None, None, False
            return
        if self.rel_path == "spells/sources.json":
            en_json_obj = json.loads(read_file(json_file))
            for item in en_json_obj.values():
                for key in item.keys():
                    self.term_set.add(Term(key, self.tag, ""))
                # self.term_list.append(Term(item["name"], self.tag, ""))
            return
        
        en_json_obj = json.loads(read_file(json_file))
        if not isinstance(en_json_obj, dict):
            return
        res_terms = self.__process_dict(en_json_obj)
        self.term_set |= res_terms
        
    def __process_dict(self, en_json_obj: dict):
        """处理Json对象

        Args:
            en_json_obj (dict): Json对象
        """
        res_terms = set()
        if "name" in en_json_obj and isinstance(en_json_obj["name"], str):
            res_terms.add(Term(en_json_obj["name"], self.tag, ""))
            # self.__process_item("name", en_json_obj["name"])
        for _, value in en_json_obj.items():
            if isinstance(value, dict):
                res_terms |= self.__process_dict(value)
            elif isinstance(value, list):
                res_terms |= self.__process_list(value)
        return res_terms
    
    def __process_list(self, en_json_obj: list):
        """处理Json列表

        Args:
            en_json_obj (list): Json列表
        """
        res_terms = set()
        for item in en_json_obj:
            if isinstance(item, dict):
                res_terms |= self.__process_dict(item)
            elif isinstance(item, list):
                res_terms |= self.__process_list(item)
        return res_terms