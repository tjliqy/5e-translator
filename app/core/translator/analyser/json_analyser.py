import json
import uuid
import os
from typing import List
from config import  EN_PATH, PLU_EN_PATH, SKIP_FILES, SKIP_DIRS, logger, SPLITED_5ETOOLS_DATA_DIR
from app.core.utils import read_file, get_rel_path, FileWorkInfo, Job
from app.core.database import DBDictionary
from langchain_core.runnables import Runnable
from .base_analyser import BaseAnalyser
from .spell_source_analyser import SpellSourceAnalyser
from .foundry_items_analyser import FoundryItemsAnalyser


class JsonAnalyser(Runnable):
    def __init__(self) -> (None):
        self.job_list: List[Job] = []  # Job列表，存放所有Job
        self.name_list: List[str] = []  # 存放所有name的值（目前仅用于更新数据库的is_key字段）
        self.ok = self.__init_dictionary()  # 初始化字典
        if not self.ok:
            return
        self.knowledge = None
        self.byhand = False
        self.splited = False # 是否是处理拆分后的数据

    def __init_dictionary(self):
        """
        初始化字典
        """
        self.dictionary = DBDictionary()
        return self.dictionary.ok

    def invoke(self, input, config=None, **kwargs):
        inputs = [input] if isinstance(input, str) else input
        self.splited = config['metadata'].get('splited', False)
        
        # print(config)
        for j in inputs:
            logger.info(f"开始解析{j}中的Json")
            job_list, obj, ok = self.json_2_job(j)
            if not ok:
                logger.error(f"JsonAnalyser: 分析{j}时出错")
                continue
            if job_list is None or len(job_list) == 0 or obj is None:
                continue
            # for job in job_list:
            #     if not job.validate():
            #         logger.error(f"JsonAnalyser: 分析{j}时出错，Job不合法")
            #         continue
            if self.splited:
                yield FileWorkInfo(job_list, obj, self.rel_path, get_rel_path(j, SPLITED_5ETOOLS_DATA_DIR))
            else:
                yield FileWorkInfo(job_list, obj, self.rel_path, self.rel_path)

    def txt_2_json(self, json_txt):
        """
        json转txt

        :param json_txt
        :return:object, bool Json对象，是否成功
        """
        return json.loads(json_txt), True

    def json_2_job(self, json_file: str, is_plu=False) -> (tuple[List[Job], object, bool]):
        """
        json_2_job:分析JSON文件组中需要翻译的任务

        :param json_file: 传入英文Json文件的路径
        :return: jobList, object, bool: 工作列表、替换work_id后的原文件内容、 是否成功
        """
        self.job_list = []

        en_json_obj = None
        # 获取相对路径，这个路径会根据是否是PLU的源数据来做不同的处理
        if is_plu:
            self.rel_path = get_rel_path(json_file, PLU_EN_PATH)
        elif self.splited:
            en_json_obj, ok = self.txt_2_json(read_file(json_file))
            if not ok:
                return None, None, False
            if not isinstance(en_json_obj, dict):
                return None, None, True
            if "_meta" not in en_json_obj or "origin_file" not in en_json_obj["_meta"]:
                return None, None, True
            self.rel_path = en_json_obj["_meta"]["origin_file"]
        else:
            self.rel_path = get_rel_path(json_file)

        # 清空字典缓存，防止上一个文件的字典污染这次查询
        self.dictionary.clear()
        # 从数据库导出当前文件的相关翻译条目，为后续直接匹配正确的翻译做准备
        self.dictionary.dump(self.rel_path)
        # 清空name_list，防止上一个文件的name污染这次查询
        self.name_list = []
        # 跳过文件夹
        if any(skip_dir in self.rel_path for skip_dir in SKIP_DIRS):
            return None, None, False
        # 跳过文件
        if self.rel_path in SKIP_FILES:
            return None, None, False
        if en_json_obj is None:
            # 读取json文件
            en_json_obj, ok = self.txt_2_json(read_file(json_file))
            if not ok:
                return None, None, False
            if not isinstance(en_json_obj, dict):
                return None, None, True
        obj = {}  # 替换了Job uuid 标识符的json对象
        if self.rel_path == "spells/sources.json":
            # 针对法术source文件进行特殊处理
            obj, self.job_list = SpellSourceAnalyser(
                self.dictionary, self.rel_path).process(en_json_obj)
        elif self.rel_path == "foundry-items.json" \
            or self.rel_path == "foundry-optionalfeatures.json" \
            or self.rel_path == "class/foundry.json"\
            or self.rel_path == "spells/foundry.json":
            obj, self.job_list = FoundryItemsAnalyser(
                self.dictionary, self.rel_path).process(en_json_obj)
        else:  # 正常处理文本逻辑
            if is_plu:
                self.rel_path = os.path.join('plu/', self.rel_path)
            # 只处理dict格式的文件
            obj, self.job_list = BaseAnalyser(
                self.dictionary, self.rel_path).process(en_json_obj, self.byhand)


        return self.job_list, obj, True


if __name__ == "__main__":
    json_analyser = JsonAnalyser(has_knowledge=False)
    f = "spells/spells-tce.json"
    # jf = [EN_PATH+f, CN_PATH+f]
    # jf = PLU_EN_PATH+f
    # json_analyser.json_2_job(jf,True)
    jf = os.path.join(EN_PATH, f)
    json_analyser.json_2_job(jf, False)
