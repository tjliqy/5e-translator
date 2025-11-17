from uuid import uuid4
from langchain_chroma import Chroma
from app.core.embedding.silicon_embeddings import SiliconAIEmbeddings
from config import CHROMA_PERSIST_DIR
import re
from typing import List, Optional


class ChromaAdapter:
    def __init__(self):
        self.embeddings = SiliconAIEmbeddings()
        self.collection: Chroma = Chroma(
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR  # 允许我们将persist_directory目录保存到磁盘上
        )
    
    def _is_long_text(self, text: str) -> (bool):
        """
        简单判断文本是否可能超过512 tokens
        中文通常1个token约等于1-2个汉字，英文通常1个token约等于4个字符
        """
        # 粗略估计，假设平均每个token对应3个字符
        return len(text) > 1500
    
    def _split_text_into_sentences(self, text: str) -> (List[str]):
        """
        将长文本分割为句子列表
        """
        # 使用常见的英文句子结束标点分割
        english_pattern = r'(.*?[.!?])\s+'
        english_sentences = re.findall(english_pattern, text)
        if english_sentences:
            sentences = english_sentences
            # 处理可能遗漏的最后一个句子
            if not text.endswith(tuple('.!?')) and text:
                last_sentence = text[text.rfind('.')+1:].strip() if '.' in text else text.strip()
                if last_sentence and last_sentence not in sentences:
                    sentences.append(last_sentence)
        else:
            # 如果还是无法分句，就简单按段落分割
            sentences = [para.strip() for para in text.split('\n') if para.strip()]
            if not sentences:
                sentences = [text]  # 保底方案
        
        return sentences
    
    def _merge_and_deduplicate_results(self, results_list: List[List]) ->(List):
        """
        合并多个搜索结果列表并去重，保留原始顺序
        """
        merged_results = []
        seen_contents = set()
        
        # 直接遍历所有结果，按照原始顺序添加不重复的结果
        for results in results_list:
            for result in results:
                # 使用page_content作为去重标识
                if result.page_content not in seen_contents:
                    seen_contents.add(result.page_content)
                    merged_results.append(result)
        
        return merged_results

    def query(self, query_text: str, name: str = None, category: str = None, eng_name: str = None):
        where = {}
        if name:
            where['name'] = name
        if category:
            where['category'] = category
        if eng_name:
            where['eng_name'] = eng_name
        if where == {}:
            where = None
        
        # 检查查询文本是否过长
        if self._is_long_text(query_text):
            # 分句处理
            sentences = self._split_text_into_sentences(query_text)
            all_results = []
            
            # 对每个分句进行相似度搜索
            for sentence in sentences:
                if sentence.strip():
                    try:
                        sentence_results = self.collection.similarity_search(
                            sentence,
                            k=1,  # 每个分句少取一些结果
                            filter=where
                        )
                        all_results.extend(sentence_results)
                    except Exception as e:
                        # 如果分句搜索失败，继续处理下一个分句
                        print(f"处理分句时出错: {e}")
                        continue
            
            # 合并结果并去重
            results = self._merge_and_deduplicate_results([all_results])
        else:
            # 短文本直接搜索
            results = self.collection.similarity_search(
                query_text,
                k=5,
                filter=where
            )
        
        # 过滤只保留包含 query_text 的文档
        filtered_results = []
        for doc in results:
            # 检查文档内容是否包含查询文本的关键词或部分内容
            # 对于长文本查询，我们可以降低匹配要求，只需要包含部分关键词
            if self._is_long_text(query_text):
                # 提取一些关键词进行匹配
                keywords = query_text.split()[:5]  # 取前5个词作为关键词
                if any(keyword.lower() in doc.page_content.lower() for keyword in keywords if len(keyword) > 2):
                    filtered_results.append(doc)
            else:
                # 短文本要求精确匹配
                if query_text.lower() in doc.page_content.lower():
                    filtered_results.append(doc)
        
        # 如果过滤后没有结果，返回原始结果（避免空结果集）
        return filtered_results if filtered_results else results

    def add(self, documents):
        print(len(documents))
        max_batch_size = 5461  # 最大批量处理大小
        for i in range(0, len(documents), max_batch_size):
            batch_documents = documents[i:i + max_batch_size]
            uuids = [str(uuid4()) for _ in range(len(batch_documents))]
            self.collection.add_documents(
                documents=batch_documents,
                ids=uuids,
            )
            
    def reset(self):
        self.collection.delete_collection()
        self.collection = Chroma(
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )