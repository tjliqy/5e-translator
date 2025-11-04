import json

class Term:
    """术语
    用于表示dnd中的术语，包括英文、中文、分类等信息
    """
    def __init__(self, en: str, category: str, cn: str):
        self.en = en
        self.category = category
        self.cn = cn
        
    def __eq__(self, value):
        if isinstance(value, Term):
            return self.en == value.en and self.category == value.category
        return False
    
    def __hash__(self):
        return hash((self.en, self.category))
    
    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

    # def __dict__(self):
    #     return {"en": self.en, "category": self.category, "cn": self.cn}
    