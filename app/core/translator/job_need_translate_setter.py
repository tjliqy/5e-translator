
from langchain_core.runnables import Runnable
from ..utils.file_work_info import FileWorkInfo
from config import logger
from app.core.utils import Job, replace_cn_pattern, need_translate_str, check_prefix, check_suffix, parse_custom_format, reset_tags_index, format_llm_msg, parse_foundry_items_uuid_format


class JobNeedTranslateSetter(Runnable):
    def __init__(self):
        self.done_jobs:list[Job] = []
        self.byhand = False
        self.force = False
    def invoke(self, input, config = None, **kwargs):
        inputs = [input] if isinstance(input, str) else input
        self.byhand = config['metadata'].get('byhand', False)
        self.force = config['metadata'].get('force', False)
        self.force_title = config['metadata'].get('force_title', False)
        for res in input:
            for job in res.job_list:
                if self.__need_translate_job(job):
                    job.need_translate = True
            yield res
            
    def __need_translate_job(self, job: Job) -> (bool):
        """
        检查是否需要翻译
        """
        # cn_str = job.cn_str if job.cn_str else ""
        # 1.已经校对过的肯定不需要翻译了
        if job.is_proofread:
            return False
        # 3.如果强制翻译标题，且当前术语是标题，则需要翻译
        if self.force_title:
            if len(job.current_names) > 0 and job.en_str == job.current_names[-1][0]:
                # 为了防止原有父级被认为是标题，这里清空原有父级
                job.current_names = job.current_names[:-1]
                return True
            else:
                # 此模式下，非标题的都不翻译
                return False
        # 2.如果没有中文，说明没有翻译过。如果是手动模式或强制翻译模式，则没校对的且包含术语的，也需要翻译
        if job.cn_str is None or (self.byhand == True or self.force == True):
            return need_translate_str(job.en_str) and (job.cn_str is None or job.cn_str != job.en_str)
        # 原来的中文可能存在 {@怪兽 xxx}的情况，需要替换回正确的英文格式{@bestry xxx}
        job.cn_str = replace_cn_pattern(job.cn_str, job.en_str)
        matched_cn_ok = self.__replace_sub_jobs(job.cn_str, job.en_str)
        if matched_cn_ok:
            return False
        
        # print(job.en_str)
        return True
    
    def __replace_sub_jobs(self, cn_str: str, en_str: str|None = None):
        """
        处理@{creature owlbear|phb}类似的情况
        将@{creature owlbear|phb}替换为中文
        """
        if not isinstance(cn_str, str):
            return False

        # 处理只有中文的情况
        if en_str is None:
            # 处理{@tag value} {@tag}自定义格式
            cn_match_k, cn_match_v, is_valid = parse_custom_format(cn_str)
            return is_valid

        # 处理既有英文又有中文的情况
        # 先分别找到中文和英文的自定义格式
        en_match_k, en_match_v, en_is_valid = parse_custom_format(
            en_str, False)
        cn_match_k, cn_match_v, cn_is_valid = parse_custom_format(
            cn_str, False)
        if (not en_is_valid) or (not cn_is_valid) or (len(cn_match_v) != len(en_match_v)):
            return False

        ok, en_match_k, en_match_v, cn_match_k, cn_match_v = reset_tags_index(
            en_match_k, en_match_v, cn_match_k, cn_match_v)
        if not ok:
            return False
        # en_match_k, en_match_v, cn_match_k, cn_match_v = tag_duplicate_removal(en_match_k, en_match_v, cn_match_k, cn_match_v)
        for i, ck in enumerate(cn_match_k):
            cv = cn_match_v[i]
            ek = en_match_k[i]
            ev = en_match_v[i]
            if ev == "":
                continue
            elif cv == "":
                return False

            # 找出嵌套的子value
            # TODO 这里可以优化，直接输出是否有子value
            # _, sub_en_match_v, _ = parse_custom_format(ev, False)
            # new_v = ev
            # # 如果有嵌套的子value
            # if len(sub_en_match_v) > 0:
            #     ok = self.__replace_sub_jobs(cv, ev)
                # if need_translate_str(ev):
                #     new_v = ev
                #     sek, sev, svalid = parse_custom_format(sub_new_v, False)
                #     cek, cev, cvalid = parse_custom_format(new_v, False)
                #     if svalid and cvalid and len(cev) == len(sev):
                #         ok, sek, sev, cek, cev = reset_tags_index(
                #             sek, sev, cek, cev)
                #         if not ok:
                #             return False
        return True
