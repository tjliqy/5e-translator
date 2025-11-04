
from typing import List, Set
from langchain_core.runnables import Runnable

from app.core.database import DBDictionary
from app.core.bean import Term

class AddTermCnFromDB(Runnable):
    """根据术语的英文从数据库读取术语的中文

    Args:
        Runnable (_type_): _description_
    """
    def __init__(self):
        self.db = DBDictionary()
        
    def invoke(self, input:List[Set[Term]], config = None, **kwargs):
        for term_set in input:
            for term in term_set:
                if term.cn == "":
                    term.cn = self.db.get(term.en,load_from_sql=True,tag=term.category)
                if term.cn != "":
                    self.db.put_term(term)
                yield term