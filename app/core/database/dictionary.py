import threading
from . import DBDictionary, RedisDB
class DatabaseAdapter:
    def __init__(self, source="", version='1.209.1') -> (None):
        self.lock = threading.Lock()
        self.ok = True
        self.redis_db = RedisDB()
        # self.redis_db = None
        # if not self.redis_db.ok:
        #     self.ok = False
        #     return
        self.db_d = DBDictionary(source, version)
        if not self.db_d.ok:
            self.ok = False
            return
            
    def get(self, k: str, rel_f="", tag=""):
        v = None
        if self.redis_db != None:
            v_list = self.redis_db.get(k, tag=tag)
            if v_list != None and len(v_list) > 0:
                return v_list[0], True
        if self.db_d != None:
            # TODO: 这里的load_from_sql不应该为True，因为这个函数只有job_processor调用，这是不应该再回表查了
            # 现在开启这里的原因是，部分有tag且大小写不一致的情况没有完全写入source表里，所以无法确保在analysis阶段找到，后续应该处理这种情况
            
            v = self.db_d.get(k, rel_f, load_from_sql=True, tag=tag)
            if v != None:
                return v['cn'], True
        return v, False
    

    def put(self, key: str, value: str, rel_f:str, proofread = False, tag="") -> (bool):
        if self.redis_db != None:
            ok = self.redis_db.put(key, value, tag=tag)
            if not ok:
                return ok
        ok = self.db_d.put(key, value, rel_f, proofread=proofread, tag=tag)
        return ok
    
    def update(self, sql_id: int, en:str, cn: str, proofread: bool= False, tag="") -> (bool):
        if self.redis_db != None:
            ok = self.redis_db.put(en, cn, tag=tag)
            if not ok:
                return ok
        return self.db_d.update(sql_id, cn, proofread, tag=tag)
    # def update(self, key: str, value: str, old_value, rel_f:str, proofread=False) -> (bool):
    #     return False
        # ok = True
        # ok = self.redis_db.update(key, value, tag=tag)
        # if not ok:
        #     return ok
        # if self.db_d != None:
        #     ok = self.db_d.update(key, value, old_value, rel_f, proofread=proofread)
        #     if not ok:
        #         return False
        # return True
    
    # def close(self):
    #     if self.redis_db != None:
    #         self.redis_db.close()
