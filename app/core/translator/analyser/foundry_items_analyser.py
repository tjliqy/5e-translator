import uuid
from config import logger
from typing import List
from .base_analyser import BaseAnalyser
from app.core.database import DBDictionary
from app.core.utils import parse_foundry_items_uuid_format, need_translate_str
class FoundryItemsAnalyser(BaseAnalyser):
    def __init__(self, dictionary: DBDictionary, rel_path: str) -> (None):
        super().__init__(dictionary, rel_path)
        
        
    def process_dict(self, en_dict, key_path, current_names = [], skip_keys = ["uuid"]):

        if "uuid" in en_dict:
            match_k, match_v, _ = parse_foundry_items_uuid_format(en_dict["uuid"])
            if len(match_k) == 0:
                return super().process_dict(en_dict, key_path, current_names, [])
            uid = uuid.uuid1()
            cn_str = None
            j = self.get_job(en_dict["uuid"])
            if j is not None:
                uid = j.uid
            else :
                self.set_job(uid, en_dict["uuid"], en_dict["uuid"], current_names=current_names)
            en_dict["uuid"] = f'[!@ {uid}]'
            
            for m, t in zip(match_v, match_k):
                if need_translate_str(m):
                    j = self.get_job(m, tag=t)
                    if j is None:
                        uid = uuid.uuid1()
                        self.set_job(uid, m, None, t, current_names=current_names)
        return super().process_dict(en_dict, key_path, current_names, skip_keys)