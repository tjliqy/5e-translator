import os
from langchain_core.runnables import Runnable
from config import logger, OUT_PATH
from app.core.database import DBDictionary

class DatabaseCleaner(Runnable):
    def __init__(self):
        self.ok = self.__init_dictionary()
        if not self.ok:
            logger.error(f"加载字典文件失败")
            raise Exception(f"加载字典文件失败")
    
    def __init_dictionary(self):
        """
        初始化字典
        """
        self.dictionary = DBDictionary()
        return self.dictionary.ok
    
    def invoke(self, input, config = None, **kwargs):
        pass