
from langchain_core.runnables import Runnable
from app.core.database import ChromaAdapter
from ..utils.file_work_info import FileWorkInfo
from langchain_core.documents import Document
from app.core.transform.pdf_transformer import transform_pdf
from config import logger, BESTIARY_FILE_MAP,CHM_ROOT_DIR,SPLITED_5ETOOLS_DATA_DIR, SPLITED_DIR_MAP, SPLITED_SOURCE_MAP
import os

KNOWLEDGE_SOURCE_DICT = {
    "book/book-xphb.json": "城主指南2024"
}
class KnowledgeSetter(Runnable):
    def __init__(self):
        self.knowledge_db:ChromaAdapter = ChromaAdapter()
        self.knowledge_source_dirs = []
    def invoke(self, file_infos, config = None, **kwargs):
        """知识库设置器
        从知识库中查询相关知识，添加到job的knowledge字段中

        Args:
            input (FileWorkInfo): 包含文件信息和任务列表的对象
            config (_type_, optional): _description_. Defaults to None.

        Yields:
            FileWorkInfo: 添加了知识库信息的包含文件信息和任务列表的对象
        """
        if (config['metadata'].get('splited', False)):
            for res in file_infos:
                is_loaded_documents = False
                for job in res.job_list:
                    if not job.need_translate:
                        continue    
                    if job.cn_str is not None and job.cn_str == job.en_str:
                        continue
                    if not is_loaded_documents:
                        # title = res.json_obj['_meta']['title']
                        # knowledge_text, need_embedding = self.__map_chm_knowledge(res.json_path, title)
                        is_loaded_documents = self.__map_chm_knowledge(res.out_path, "")
                    
                    documents:Document = self.knowledge_db.query(job.en_str)
                    documents = documents[:2]
                    if len(documents) != 0:
                        job.knowledge.extend([d.page_content for d in documents])
                yield res
            return
        for res in file_infos:
            if "adventure" in res.json_path or "book-erlw" in res.json_path:
                yield res
                # yield self.__get_adventure_knowledge_by_embendding(res)
            else:
                for job in res.job_list:
                    # 如果已经校对过了，则跳过
                    if not job.need_translate:
                        continue
                    # 如果英文和中文相同，则跳过
                    if job.cn_str is not None and job.cn_str == job.en_str:
                        continue
                    # print(job.current_names)
                    if res.json_path == 'spells/spells-xphb.json' and len(job.current_names) > 0:
                        # print(job.current_names[0].keys())
                        spell_en = job.current_names[0][0]
                        try:
                            with open(os.path.join("/data/DND5e_chm/玩家手册2024/法术详述", f"spells/{spell_en.lower()}.txt"), 'r', encoding='utf-8') as infile:
                                job.knowledge.append(infile.read())
                        except Exception as e:
                            logger.error(f"读取文件 {os.path.join('/data/DND5e_chm/玩家手册2024/法术详述', f'spells/{spell_en.lower()}.txt')} 时出错: {e}")
                            logger.error(f"查询知识库: {job.en_str}  {job.current_names} 失败")
                    elif res.json_path in BESTIARY_FILE_MAP.keys():
                        bestiary_en = job.current_names[0][0]
                        # 去掉bestiary_en括号里的内容
                        bestiary_en = bestiary_en.split("(")[0].strip()
                        try:
                            chm_file_file = f"{BESTIARY_FILE_MAP[res.json_path]}/bestiary/{bestiary_en.lower()}.txt"
                            if os.path.exists(os.path.join(CHM_ROOT_DIR, chm_file_file)):
                                with open(os.path.join(CHM_ROOT_DIR, chm_file_file), 'r', encoding='utf-8') as infile:
                                    job.knowledge.append(infile.read()) 
                            if os.path.exists(os.path.join(CHM_ROOT_DIR, chm_file_file.replace(".txt", "s.txt"))):
                                with open(os.path.join(CHM_ROOT_DIR, chm_file_file.replace(".txt", "s.txt")), 'r', encoding='utf-8') as infile:
                                    job.knowledge.append(infile.read())
                            if len(job.knowledge) == 0: 
                                logger.error(f"{bestiary_en.lower()} 未找到知识源")
                        except Exception as e:
                            logger.error(f"读取文件 {os.path.join(CHM_ROOT_DIR, chm_file_file)} 时出错: {e}")
                            logger.error(f"查询知识库: {job.en_str}  {job.current_names} 失败")

                        
                    continue
                    logger.info(f"查询知识库: {job.en_str}")
                    # 先按照英文名称查询
                    documents = self.knowledge_db.query(job.en_str, eng_name=job.en_str)
                    if len(documents) != 0:
                        job.knowledge.append(documents[0].metadata['name'].split('/')[-1])
                        continue
                    
                    # 再按照中文名称查询
                    if job.cn_str is not None:
                        documents = self.knowledge_db.query(job.cn_str)
                    
                        for doc in documents:
                            job.knowledge.append(doc.page_content)
                    # 如果这个Job有CurrentNames字段，则用最后一个（离这个Job最近的）来查询知识库
                    if len(job.knowledge) == 0 and len(job.current_names) > 0:
                        name_documents = self.knowledge_db.query(job.current_names[-1])
                        documents.extend(name_documents)
                        for name_doc in name_documents:
                            if job.en_str in name_doc.page_content:
                                job.knowledge.append(name_doc.page_content)
                    
                    # 如果json有对应的源文件，则按照源文件进行筛选
                    if job.rel_path in KNOWLEDGE_SOURCE_DICT.keys():
                        key = KNOWLEDGE_SOURCE_DICT[job.rel_path]
                        job.knowledge = list(map(lambda k: k.page_content, filter(lambda k: key in k.metadata['source'], documents)))
                    print(len(job.knowledge))
                    if len(job.knowledge) > 0:
                        print(job.en_str)
                yield res
    def __get_adventure_knowledge_by_embendding(self, file_work_info: FileWorkInfo) -> (FileWorkInfo):
        for job in file_work_info.job_list:
            if not job.need_translate:
                continue
            documents:Document = self.knowledge_db.query(job.en_str)
            documents = documents[:2]
            if len(documents) != 0:
                job.knowledge.extend([d.page_content for d in documents])
        return file_work_info
    def __get_adventure_knowledge(self, file_work_info: FileWorkInfo) -> FileWorkInfo:
        """获取冒险指南中的知识"""
        pdf_file_path = "/data/5e-translator/data/idrotf.pdf"
        if not os.path.exists(pdf_file_path):
            return file_work_info
        paragraphs = transform_pdf(pdf_file_path)
        for job in file_work_info.job_list:
            if not job.need_translate:
                continue
            en_name = job.en_str
            chapter_id = ''
            if '.' in en_name:
                # 处理章节标题，一般为：S1. xxx， 优先匹配.前面的部分
                chapter_id = en_name.split('.')[0].strip().lower()
                en_name = en_name.split('.')[-1].split(':')[-1].strip().lower()
            if chapter_id != '':
                for para in paragraphs:
                    if chapter_id in para['title'].lower():
                        job.knowledge.append(para['title'])
            if len(job.knowledge) > 0:
                continue
            if en_name != '':
                for para in paragraphs:
                    if en_name in para['title'].lower():
                        job.knowledge.append(para['title'])
                if len(job.knowledge) == 0:
                    for para in paragraphs:
                        for c in para['content']:
                            if en_name in c.lower():
                                job.knowledge.append(c)
                                
            if len(job.knowledge) > 0 or len(job.current_names) == 0:
                continue
            for name in reversed(job.current_names):
                en_name = name[0]
                if '.' in en_name:
                    chapter_id = en_name.split('.')[0].strip().lower()
                    en_name = en_name.split('.')[-1].split(':')[-1].strip().lower()
                if chapter_id != '':
                    for para in paragraphs:
                        if chapter_id in para['title'].lower():
                            if len(para['content']) > 0:
                                job.knowledge.append(' '.join(para['content']))
                            else:
                                job.knowledge.append(para['title'])
                    if len(job.knowledge) > 0:
                            break
                for para in paragraphs:
                    if en_name in para['title'].lower():
                        if len(para['content']) > 0:
                            job.knowledge.append(' '.join(para['content']))
                        else:
                            job.knowledge.append(para['title'])
                if len(job.knowledge) > 0:
                    break
        return file_work_info
    
    
    def __map_chm_knowledge(self, rel_path, title:str):
        """映射chm文件中的知识"""
        base_dirs = []
        for k,v in SPLITED_DIR_MAP.items():
            if k in rel_path:
                base_dirs.extend(v)

        if len(base_dirs) == 0:
            for k, v in SPLITED_SOURCE_MAP.items():
                if k in rel_path:
                    base_dirs.append(v)
                    break
                    
        if len(base_dirs) == 0:
            # TODO 通过llm自动匹配
            return False

        if self.knowledge_source_dirs == base_dirs:
            # 判断当前知识库，避免重复加载
            return True
        from config import CHM_TXT_DIR
        from app.core.transform import load_adventure_files
        documents = []
        for base_dir in base_dirs:
            
            documents.extend(load_adventure_files(os.path.join(CHM_TXT_DIR, base_dir)))
        #对lines临时进行嵌入编码
        self.knowledge_db.reset()
        self.knowledge_db.add(documents)
        self.knowledge_source_dirs = base_dirs
        return True