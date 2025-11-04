
from langchain_core.runnables import Runnable
from app.core.database import ChromaAdapter
from ..utils.file_work_info import FileWorkInfo
from langchain_core.documents import Document
from app.core.transform.pdf_transformer import transform_pdf
from app.core.utils import Job
from app.core.database import DBDictionary

from config import logger
import os

class ByHandHandler(Runnable):
    def __init__(self):
        # self.knowledge_db:ChromaAdapter = ChromaAdapter()
        self.byhand = False
        self.dictionary = DBDictionary()
        
    def invoke(self, input: list[FileWorkInfo], config = None, **kwargs):
        """手动处理器
        主要处理name字段关键字和小于4个单词的词组

        Args:
            input (FileWorkInfo): 包含文件信息和任务列表的对象
            config (_type_, optional): _description_. Defaults to None.

        Yields:
            FileWorkInfo: 添加了知识库信息的包含文件信息和任务列表的对象
        """
        self.byhand = config['metadata'].get('byhand', False)
        if self.byhand:
            for res in input:
                for job in res.job_list:
                    if not job.need_translate:
                        continue
                    if (len(job.current_names) > 0 and job.en_str == job.current_names[-1][0]) \
                            or len(job.en_str.split(' ')) < 5:
                            
                        print(job.to_llm_question()[0])
                        self.dictionary.update_by_hand(job.en_str, job.cn_str)
                        # job.need_translate = True
                    # else:
                        # job.need_translate = False
                yield res
                    
        else:
            for res in input:
                yield res
        