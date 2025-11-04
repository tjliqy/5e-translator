import json
from config import *

class Job:
    def __init__(self, uid: str, en_str, cn_str, rel_path="", tag="", knowledge=[],current_names=[], is_proofread=False, sql_id=None) -> (None):
        self.uid = str(uid)
        self.en_str = en_str
        self.cn_str = cn_str
        self.rel_path = rel_path
        if tag is None:
            self.tag = ""
        else:
            self.tag = tag
        self.knowledge = knowledge
        self.terms = []
        self.current_names = current_names
        self.is_proofread = is_proofread
        self.reference = ""
        self.err_time = 0
        self.need_translate = False
        self.sql_id = sql_id

    def __str__(self):
        return f'en_str:{self.en_str} \ncn_str:{self.cn_str}'

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return __value == self.en_str
        else:
            return self == __value
        
    def to_llm_question(self) -> (tuple[str, str]):
        """
        转换为LLM问题
        """
        reference = []
        if self.knowledge is not None and len(self.knowledge):
            if self.rel_path == 'spells/spells-xphb.json':
                return json.dumps({"parents":self.current_names, "reference":self.knowledge, "trans_str": self.en_str}, ensure_ascii=False), PROMOT_SPELL_XPHB

            elif self.rel_path in BESTIARY_FILE_MAP.keys():
                return json.dumps({"parents":self.current_names, "reference":self.knowledge, "trans_str": self.en_str}, ensure_ascii=False), PROMOT_BESTIARY_XMM
            else:
                reference.extend(self.knowledge)
        if self.terms is not None and len(self.terms):
            reference.extend([f"{term.en}:{term.cn}" for term in self.terms])
        if len(reference) > 0:
            return json.dumps({"parents":self.current_names, "reference":reference, "trans_str": self.en_str}, ensure_ascii=False), PROMOT_KNOWLEDGE
        else:
            return json.dumps({"parents":self.current_names, "trans_str": self.en_str}, ensure_ascii=False), SIMPLE_PROMOT
    
    def validate(self) -> (bool):
        """
        验证Job是否合法
        """
        # cn_str = replace_cn_pattern(self.cn_str, self.en_str)
        _, matched_cn_ok = self.__replace_sub_jobs()
        return matched_cn_ok

    def __replace_sub_jobs(self):
        """
        处理@{creature owlbear|phb}类似的情况
        将@{creature owlbear|phb}替换为中文
        """
        # def process_value(value):
        #     """
        #     处理单个值，进行前缀、后缀检查和翻译替换
        #     """
        #     if need_translate_str(value):
        #         value_without_prefix, prefix = check_prefix(value)
        #         value_pure, suffix = check_suffix(value_without_prefix)
        #         new_value, ok = self.__get(value_pure)
        #         if ok and new_value is not None:
        #             return f'{prefix}{new_value}{suffix}'
        #     return value

        if not isinstance(self.cn_str, str):
            return self.cn_str, False

        # 处理既有英文又有中文的情况
        # 先分别找到中文和英文的自定义格式
        en_match_k, en_match_v, en_is_valid = parse_custom_format(
            self.en_str, False)
        cn_match_k, cn_match_v, cn_is_valid = parse_custom_format(
            self.cn_str, False)
        if (not en_is_valid) or (not cn_is_valid) or (len(cn_match_v) != len(en_match_v)):
            return self.cn_str, False

        ok, en_match_k, en_match_v, cn_match_k, cn_match_v = reset_tags_index(
            en_match_k, en_match_v, cn_match_k, cn_match_v)
        if not ok:
            return self.cn_str, False
        # en_match_k, en_match_v, cn_match_k, cn_match_v = tag_duplicate_removal(en_match_k, en_match_v, cn_match_k, cn_match_v)
        for i, ck in enumerate(cn_match_k):
            cv = cn_match_v[i]
            ek = en_match_k[i]
            ev = en_match_v[i]
            if ev == "":
                continue
            elif cv == "":
                return self.cn_str, False

            # 找出嵌套的子value
            # TODO 这里可以优化，直接输出是否有子value
            # _, sub_en_match_v, _ = parse_custom_format(ev, False)
            # new_v = ev
            # 如果有嵌套的子value
            # if len(sub_en_match_v) > 0:
            #     sub_new_v, ok = self.__replace_sub_jobs(cv, ev)
            #     if need_translate_str(ev):
            #         new_v = process_value(ev)
            #         sek, sev, svalid = parse_custom_format(sub_new_v, False)
            #         cek, cev, cvalid = parse_custom_format(new_v, False)
            #         if svalid and cvalid and len(cev) == len(sev):
            #             ok, sek, sev, cek, cev = reset_tags_index(
            #                 sek, sev, cek, cev)
            #             if not ok:
            #                 return cn_str, False
            #             for j, _ in enumerate(cek):
            #                 new_v = new_v.replace(
            #                     f"{{@{cek[j]} {cev[j]}}}", f"{{@{sek[j]} {sev[j]}}}", 1)
            #     cn_str = cn_str.replace(
            #         f"{{@{ck} {cv}}}", f"{{@{ek} {new_v}}}", 1)
            # elif '|' in ev:
            #     new_v = '|'.join(process_value(eev) for eev in ev.split('|'))
            #     if f"{{@{ck} {cv}}}" not in cn_str:
            #         print(f"错误！{cv}！！！{cn_str} {en_str}")
            #     cn_str = cn_str.replace(
            #         f"{{@{ck} {cv}}}", f"{{@{ek} {new_v}}}", 1)
            # else:
            #     new_v = process_value(ev)
            #     if f"{{@{ck} {cv}}}" not in cn_str:
            #         print(f"错误！{cv}！！！{cn_str} {en_str}")
            #     cn_str = cn_str.replace(
            #         f"{{@{ck} {cv}}}", f"{{@{ek} {new_v}}}", 1)
        return self.cn_str, True