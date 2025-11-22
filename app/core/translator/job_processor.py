import os
import re
import json
import concurrent.futures

from langchain_core.runnables import Runnable
from config import logger, DS_KEY, SIMPLE_PROMOT, PROMOT_KNOWLEDGE, OUT_PATH
from app.core.utils import Job, TranslatorStatus
from app.core.database import DatabaseAdapter
from .siliconflow_adapter import SiliconFlowAdapter
from .llm_factory import LLMFactory
from app.core.utils import Job, replace_cn_pattern, need_translate_str, check_prefix, check_suffix, parse_custom_format, reset_tags_index, format_llm_msg, parse_foundry_items_uuid_format
from typing import List
from app.core.utils import get_rel_path
from itertools import zip_longest


class JobProcessor(Runnable):
    """解释JOB对象
    多线程逐个处理
    对于每个JOB对象：
    1. 检查是否需要翻译
    2. 召回知识库的知识
    3. 翻译
    4. 回调

    Args:
        Runnable (_type_): _description_
    """

    def __init__(self, thread_num: int = 10, update: bool = False):
        self.thread_num = thread_num
        self.update = update
        self.ok = self.__init_dictionary()
        if not self.ok:
            logger.error(f"初始化字典失败")
            return
        self.ok = self.__init_adapter()
        if not self.ok:
            logger.error(f"加载LLM中间件失败")
            return

        self.byhand = False
        self.force = False
        
    def invoke(self, input, config=None, **kwargs):
        inputs = [input] if isinstance(input, str) else input
        self.byhand = config['metadata'].get('byhand', False)
        self.force = config['metadata'].get('force', False)
        
        if self.byhand:
            # 手动模式，串行执行
            self.thread_num = 1
            
        self.ok = self.__init_factory()
        if not self.ok:
            logger.error(f"初始化LLM工厂失败")
            return
        
        for res in inputs:
            logger.info(f"开始处理 {res.json_path} 中的Job")
            # self.rel_path = get_rel_path(res.json_path)
            # self.obj = res['obj']
            self.done_jobs: List[Job] = []
            self.factory.reset()
            # self.factory.set_finish(False)
            self.factory.add_jobs(res.job_list)
            self.factory.set_finish(True)
            self.factory.start_work()
            if self.factory.isAllDone():
                self.write_2_json(res.out_path, res.json_obj)
            else:
                logger.error(f"处理{res.json_path}中的Job总计{self.factory.job_count}个，成功{self.factory.finish_count}个，失败{self.factory.error_count}个！")
                # 将失败的 job 列表导出到文件，方便人工查看与重试
                failed = []
                try:
                    failed = getattr(self.factory, 'failed_jobs', [])
                except Exception:
                    failed = []

                failed_path = os.path.join(OUT_PATH, res.out_path + '.failed_jobs.json')
                try:
                    os.makedirs(os.path.dirname(failed_path), exist_ok=True)

                    with open(failed_path, 'w') as fh:
                        json.dump([j.to_serializable() for j in failed], fh, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f'写出 failed_jobs 文件失败: {e}')

                if len(failed) > 0:
                    print(f"以下 {len(failed)} 个 Job 处理失败，已保存到: {failed_path}")
                    for j in failed:
                        last = j.last_answer if hasattr(j, 'last_answer') else ''
                        last_short = last if not isinstance(last, str) else (last[:200] + '...' if len(last) > 200 else last)
                        print(f"- uid: {j.uid}, en: {j.en_str}, err_time: {j.err_time}, last_answer: {last_short}")
                    print('\n可用下面命令快速重试这些失败的Job (示例)：')
                    print(f"python3 main.py retry-failed --file \"{failed_path}\" --thread_num {self.thread_num} --byhand {self.byhand} --force {self.force}")
                else:
                    print('没有记录到被丢弃的失败 Job。')
            yield res
            
    def __init_dictionary(self):
        """
        初始化字典
        """
        self.dictionary = DatabaseAdapter(source="GPT")
        return self.dictionary.ok

    def __init_adapter(self):
        self.adapter = SiliconFlowAdapter(DS_KEY)
        return True

    def __init_factory(self):
        def work_func(job: Job, worker_id: int) -> (tuple[Job, TranslatorStatus]):
            # 检测是否需要翻译
            if not job.need_translate:
                return job, TranslatorStatus.SUCCESS
            if self.force and job.sql_id == None:
                # force模式下，只更新有的
                return job, TranslatorStatus.SUCCESS
            # 发送给大模型进行翻译
            request, promot = job.to_llm_question()
            if job.cn_str and job.cn_str != "" and self.byhand:
                print(f"请求细节：{request}")
                print(f"原始中文：{job.cn_str}")
                confirm = input("是否需要大模型翻译？(Y/n)")
                if confirm.lower() == 'n':
                    input_str = input(f"请确认(Y/n)：")
                    if input_str.lower() == 'n':
                        return None, TranslatorStatus.FAILURE
                    elif input_str.lower() != 'y' and input_str != '':
                        job.cn_str = input_str
                    return job, TranslatorStatus.SUCCESS
            
            msg, status = self.adapter.sendText(request, promot)
            if status != TranslatorStatus.SUCCESS:
                logger.warning(f'获取结果错误:{msg}')
                return None, status

            # 对回调信息进行解析
            kimi_data, ok = format_llm_msg(msg)
            if (
                (not ok)
                or "trans_str" not in kimi_data.keys()
                or not isinstance(kimi_data["trans_str"], str)
            ):
                logger.warning(f'解析结果错误:{msg}')
                return None, TranslatorStatus.FAILURE

            cstr = kimi_data["trans_str"]

            cn_str = replace_cn_pattern(
                cstr, job.en_str)
            if not isinstance(cn_str, str):
                job.last_answer = cstr
                return None, TranslatorStatus.FAILURE

            if self.byhand:
                # 手动模式，需要用户确认
                print(f"请求细节：{request}")
                print(f"原始中文：{job.cn_str}")
                print(f"翻译结果：{cn_str}")
                input_str = input(f"请确认(Y/n)：")
                if input_str.lower() == 'n':
                    return None, TranslatorStatus.FAILURE
                elif input_str.lower() == 'y' or input_str == '':
                    job.cn_str = cn_str
                else:
                    job.cn_str = input_str
            else:
                # 自动模式，检查替换是否正确
                # 1. 初筛中文的{ 和 }数量与英文相同
                if cn_str.count('{') != job.en_str.count('{') or cn_str.count('}') != job.en_str.count('}'):
                    logger.warning(f"翻译文本替换错误:{job}")
                    job.last_answer = cn_str
                    return None, TranslatorStatus.FAILURE
                # 2. 检查替换是否正确
                _ ,ok=  self.__replace_sub_jobs(cn_str,job.en_str,job.tag)
                if not ok:
                    job.last_answer = cn_str
                    logger.warning(f"翻译文本替换错误:{job}")
                    return None, TranslatorStatus.FAILURE
                job.cn_str = cn_str
                # job.cn_str = replaced_cn
            return job, TranslatorStatus.SUCCESS

        def put_done_job(job: Job):
            """
            处理完成任务
            """
            if job is not None and job.cn_str is not None:
                if self.update and job.need_translate:
                    # 写入数据库,如果手动模式，则默认就是校对过得
                    if job.sql_id is None:
                        self.dictionary.put(
                            job.en_str, job.cn_str, job.rel_path, proofread=self.byhand, tag=job.tag)
                    else:
                        self.dictionary.update(job.sql_id, job.en_str, job.cn_str, proofread=self.byhand, tag=job.tag)
                self.done_jobs.append(job)
            else:
                logger.error(f"处理完成任务错误:{job}")

        self.factory = LLMFactory(
            work_num=self.thread_num,
            work_func=work_func,
            done_func=put_done_job,
        )
        return True

    def __get(self, en: str, tag="") -> (tuple[str, bool]):
        for j in self.done_jobs:
            if j.en_str == en and j.tag == tag:
                return j.cn_str, True

        return self.dictionary.get(en, tag=tag)

    def __replace_sub_jobs(self, cn_str: str, en_str: str|None = None, tag = ""):
        # print(cn_str)
        def process_value(value, tag=""):
            """
            处理单个值，进行前缀、后缀检查和翻译替换
            """
        # if just_validate:
        #     return value
            if need_translate_str(value):
                value_without_prefix, prefix = check_prefix(value)
                value_pure, suffix = check_suffix(value_without_prefix)
                new_value, ok = self.__get(value_pure,tag)
                if ok and new_value is not None:
                    return f'{prefix}{new_value}{suffix}', True
                else:
                    return value, False
            return value, True
        
        
        processed = False
        if en_str is None:
            # 若没有传入en_str，需要从done_jobs中查找
            for j in self.done_jobs:
                if j.cn_str == cn_str:
                    en_str = j.en_str
                    break
        if en_str is None:
            return cn_str, False

        # 初筛
        if "{@" in cn_str:
            # 初筛，包含@{的，需要继续处理
            p_v, ok = process_value(en_str)
            if ok:
                cn_str = p_v
            processed = True
        en_match_k, en_match_v, en_is_valid = parse_custom_format(
            en_str, False)
        cn_match_k, cn_match_v, cn_is_valid = parse_custom_format(
            cn_str, False)
        if (not en_is_valid) or (not cn_is_valid) or (len(cn_match_v) != len(en_match_v)):
            return cn_str, False

        ok, en_match_k, en_match_v, cn_match_k, cn_match_v = reset_tags_index(
            en_match_k, en_match_v, cn_match_k, cn_match_v)
        if not ok:
            return cn_str, False
        check_split_str = en_str
        # 第一步：把cn_str中的所有@{tag value}都替换为英文中的对应的样子
        # if len(cn_match_k) > 0:
        #     processed = True
            
        for ck, cv, ek, ev in zip(cn_match_k, cn_match_v, en_match_k, en_match_v):
            check_split_str = check_split_str.replace(f"{{@{ek} {ev}}}", "")

            cn_str = cn_str.replace(f"{{@{ck} {cv}}}", f"{{@{ek} {ev}}}",1)
            # 第二步：逐个解析每个ev
            new_v, ok = self.__replace_sub_jobs(cv, ev, tag = ek)
            if not ok:
                return cn_str, False
            cn_str = cn_str.replace(f"{{@{ek} {ev}}}", f"{{@{ek} {new_v}}}",1)
            
        if '|' in check_split_str:
            if tag == "filter":
                filter_values = en_str.split("|")
                if (len(filter_values) > 2):
                    # 正常至少有3个值
                    cv_page = filter_values[1]
                    cv_name, _ = process_value(filter_values[0], tag=cv_page)
                    if cv_page == "bestiary":
                        cv_conditions = []
                        for eev in filter_values[2:]:
                            if eev.startswith('type='):
                                # 锁定type
                                cv_conditions.append(eev)
                            elif eev.startswith('tag='):
                                # 锁定tag
                                cv_conditions.append(eev)
                            else:
                                ccv, _ = process_value(eev)
                                cv_conditions.append(ccv)
                        cn_str = f"{cv_name}|{cv_page}|{'|'.join(cv_conditions)}"
                        return cn_str, True
                    elif cv_page in ["items", "spells", "optionalfeatures", "races"]:
                        cv_conditions = []
                        for eev in filter_values[2:]:
                            ccv, _ = process_value(eev)
                            cv_conditions.append(ccv)
                        cn_str = f"{cv_name}|{cv_page}|{'|'.join(cv_conditions)}"
                        return cn_str, True
            en_split = en_str.split('|')
            cn_split = cn_str.split('|')
            res_split = []
            for i, eev in enumerate(en_split):
                if len(cn_split) > i:
                    ccv = cn_split[i]
                else:
                    ccv = None
                if "{@" in eev and ccv is not None and ccv != eev:
                    res_split.append(ccv)
                else:
                    p_v, ok = process_value(eev, tag=tag)
                    if ok or ccv is None:
                        res_split.append(p_v)
                    else:
                        res_split.append(ccv)
            cn_str = '|'.join(res_split)
        elif processed == False:
            p_v, ok = process_value(en_str, tag = tag)
            if ok:
                cn_str = p_v
        return cn_str, True

    def write_2_json(self, json_path: str, obj: object):
        """
        将处理后的作业信息写入JSON文件。
        该方法会先调用 __replace_jobs 方法替换作业中的相关内容，
        然后将替换后的内容写入JSON文件。

        Returns:
            bool: 如果写入成功返回True，否则返回False。
        """
        # 调用 __replace_jobs 方法替换作业中的相关内容
        new_obj, ok = self.__replace_jobs(obj)
        # 检查替换操作是否成功
        if not ok:
            # 若替换失败，返回False
            logger.warning(f"write_2_json: {json_path} failed")
            return False
        # 若替换成功，调用 __write_json 方法将替换后的内容写入JSON文件
        json_path = os.path.join(OUT_PATH, json_path)
        job_path = json_path + ".jobs"
        if not (os.path.exists(json_path) and os.path.exists(job_path)):
            return False
        try:
            with open(json_path, "w") as file:
                file.write(json.dumps(new_obj, ensure_ascii=False, indent=2))

            # with open(job_path, "w") as file:
            #     file.write(json.dumps(self.done_jobs,
            #                ensure_ascii=False, indent=2))
        except ValueError as e:
            logger.debug(e)
            return False
        return True

    def __replace_jobs(self, obj):
        """_summary_

        Args:
            obj (_type_): _description_

        Returns:
            _type_: _description_
        """
        if isinstance(obj, str):
            # 通过uuid替换指定的job
            pattern = r'\[!@ ([^\]]+)\]'
            matches = re.findall(pattern, obj)
            if len(matches) > 0:
                for job_id in matches:
                    for j in self.done_jobs:
                        if j.uid == job_id:
                            j.cn_str, ok = self.__replace_sub_jobs(
                                j.cn_str, j.en_str, tag=j.tag)
                            obj = obj.replace(f'[!@ {job_id}]', j.cn_str)
                            break

                return obj, True
            else:
                # obj, ok = self.__replace_sub_jobs(obj)
                return obj, False
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'ENG_name':
                    continue
                try:
                    new_v, ok = self.__replace_jobs(v)
                    if ok:
                        # 临时在这里特殊处理foundry-items.json和foundry-optinalfeatures.json中的uuid特殊格式
                        if (k == "uuid"):
                            ev = ''
                            for j in self.done_jobs:
                                if j.cn_str == new_v:
                                    ev = j.en_str
                                    break
                            if ev != '':
                                new_v = ev
                            match_k, match_v,_ = parse_foundry_items_uuid_format(new_v)
                            if (len(match_k) > 0):
                                for mk,mv in zip(match_k, match_v):
                                    cn_v,_ = self.__get(mv, mk)
                                    new_v = new_v.replace(mv, cn_v)
                        
                        obj[k] = new_v
                except Exception as exc:
                    logger.error(f'{k} generated an exception: {exc}')
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     futures = {executor.submit(
            #         self.__replace_jobs, v): k for k, v in obj.items()}
            #     for future in concurrent.futures.as_completed(futures):
            #         k = futures[future]
            #         try:
            #             new_v, ok = future.result()
            #             if ok:
            #                 # 临时在这里特殊处理foundry-items.json和foundry-optinalfeatures.json中的uuid特殊格式
            #                 if (k == "uuid"):
            #                     match_k, match_v,_ = parse_foundry_items_uuid_format(new_v)
            #                     if (len(match_k) > 0):
            #                         for v in match_v:
            #                             cn_v,_ = self.__get(v)
            #                             new_v = new_v.replace(v, cn_v)
                            
            #                 obj[k] = new_v
            #         except Exception as exc:
            #             logger.error(f'{k} generated an exception: {exc}')
            return obj, True
        elif isinstance(obj, list):
            for i, o in enumerate(obj):
                new_o, ok = self.__replace_jobs(o)
                if ok:
                    obj[i] = new_o
            return obj, True
        elif isinstance(obj, bool) or isinstance(obj, int) or isinstance(obj, float):
            return obj, True
        elif obj is None:
            return obj, False
        else:
            logger.warning(f"无法解析！{obj}")
            return obj, False