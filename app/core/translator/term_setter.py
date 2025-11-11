from langchain_core.runnables import Runnable
from app.core.database import RedisDB
from ..utils.file_work_info import FileWorkInfo
from langchain_core.documents import Document
from config import logger
from app.core.bean import Term
import re  # 添加正则表达式模块
import concurrent.futures
from typing import List, Dict, Any

class TermSetter(Runnable):
    def __init__(self):
        self.term_db: RedisDB = RedisDB(db=1)
        term_set = self.term_db.keys()
        if term_set:
            # 2. 处理术语列表（排序：长术语优先）
            self.terms = sorted(term_set, key=lambda x: len(x), reverse=True)
            self.exact_pattern = re.compile(r'\b(' + '|'.join(re.escape(term) for term in self.terms) + r')\b')
        self.max_workers = 8  # 设置线程池大小，可根据实际情况调整

    def _process_job(self, job: Any) -> (Any):
        """处理单个job的术语匹配"""
        # 如果已经校对过了，则跳过
        if not job.need_translate:
            return job
        # 如果有知识库，则不添加术语，为了防止知识库搞错了，所以暂时注释掉
        # if job.knowledge and len(job.knowledge) > 0:
        #     return job
        # 如果英文和中文相同，则跳过
        if job.cn_str is not None and job.cn_str == job.en_str:
            return job
        
        logger.info(f"term_setter: {job.en_str}")
        # 将英文句子拆分为可能的术语

        # 3. 分两步匹配：先精确匹配大小写，再不区分大小写匹配剩余术语
        # 3.1 精确大小写匹配
        exact_matches = self.exact_pattern.findall(job.en_str)
        
        # 3.2 移除已精确匹配的术语，对剩余术语进行不区分大小写匹配
        remaining_terms = [term for term in self.terms if term not in exact_matches]
        case_insensitive_matches = []
        if remaining_terms:
            # 创建剩余术语的小写映射表（键：小写术语，值：原始术语）
            term_map_remaining = {term.lower(): term for term in remaining_terms}
            # 使用小写术语构建模式，确保匹配时不区分大小写
            case_insensitive_pattern = re.compile(
                r'\b(' + '|'.join(re.escape(term.lower()) for term in remaining_terms) + r')\b', 
                re.IGNORECASE
            )
            # 从文本中查找匹配项（可能是任意大小写）
            text_matches = case_insensitive_pattern.findall(job.en_str)
            # 将文本匹配项转换为术语库中的原始大小写
            case_insensitive_matches = [term_map_remaining[match.lower()] for match in text_matches]

        # 3.3 合并结果并去重（保留精确匹配优先顺序）
        matched_keys = list(dict.fromkeys(exact_matches + case_insensitive_matches))
        # 3.4 合并Job中的当前名称并去重
        # 4. 根据key查询术语中文
        matched_terms = []
        for en in matched_keys:
            term_cn = self.term_db.get(en, job.tag)
            if term_cn is not None:
                matched_terms.append(Term(en, job.tag, term_cn))
        job.terms = matched_terms  # 假设job对象有terms属性
        return job

    def invoke(self, input, config=None, **kwargs):
        """术语设置器
        从术语库中查询相关术语，添加到job的term字段中

        Args:
            input (FileWorkInfo): 包含文件信息和任务列表的对象
            config (_type_, optional): _description_. Defaults to None.

        Yields:
            FileWorkInfo: 添加了知识库信息的包含文件信息和任务列表的对象
        """
        if (config['metadata'].get('splited', False)):
            for res in input:
                yield res
            return
        for res in input:
            # 使用线程池并发处理job_list中的每个job
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有任务到线程池
                future_to_job = {executor.submit(self._process_job, job): job for job in res.job_list}
                
                # 收集处理结果
                processed_jobs = []
                for future in concurrent.futures.as_completed(future_to_job):
                    try:
                        processed_job = future.result()
                        processed_jobs.append(processed_job)
                    except Exception as exc:
                        # 获取出错的原始job
                        original_job = future_to_job[future]
                        logger.error(f"处理job时出错: {original_job.en_str}, 错误: {str(exc)}")
                        # 将出错的job也添加回结果列表
                        processed_jobs.append(original_job)
                
                # 替换原来的job_list
                res.job_list = processed_jobs
            
            yield res