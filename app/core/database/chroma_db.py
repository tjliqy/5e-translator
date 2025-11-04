from uuid import uuid4
from langchain_chroma import Chroma
from app.core.embedding.silicon_embeddings import SiliconAIEmbeddings
from config import CHROMA_PERSIST_DIR


class ChromaAdapter:
    def __init__(self):
        self.embeddings = SiliconAIEmbeddings()
        self.collection: Chroma = Chroma(
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR  # 允许我们将persist_directory目录保存到磁盘上
        )

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
        results = self.collection.similarity_search(
            query_text,
            k=3,
            filter=where)
        return results

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