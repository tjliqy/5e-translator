# coding=utf-8
import re
from typing import List
from langchain_core.documents import Document

def split_chinese_english(s):
    s = s.replace('\xa0', '')

    # 匹配中文字符
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5·]+')
    # 匹配英文字符和空格
    english_pattern = re.compile(r'[a-zA-Z\s-]+')

    # 查找中文字符串
    chinese_match = chinese_pattern.match(s)
    if chinese_match:
        chinese_str = chinese_match.group()
        # 从匹配到的中文后面开始查找英文字符串
        remaining_str = s[len(chinese_str):].lstrip()
        english_match = english_pattern.match(remaining_str)
        chinese_str = chinese_str.replace('\n', '')
        chinese_str = re.sub(r'\s+', ' ', chinese_str)
        if english_match:
            english_str = english_match.group().replace('\n', '')
            english_str = re.sub(r'\s+', ' ', english_str)

            return chinese_str, english_str
        else:
            return re.sub(r'\s+', ' ', s), ''
    return s, ''


class BasicBean:
    def __init__(self):
        self.name = ''
        self.eng_name = ''
        self.rate = 0
        self.descriptions = []
        self.children:List[BasicBean] = []

    def set_name(self, text):
        self.name, self.eng_name = split_chinese_english(text)

    def set_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        if text == '':
            return
        self.descriptions.append(text)

    def to_dict(self):
        return {
            "name": self.name,
            "eng_name": self.eng_name,
            "description": "\\n".join(self.jsonfiy(self.descriptions))
        }
        
    def get_documents(self) -> (List[Document]):
        documents:List[Document] = []
        def to_document(bean:BasicBean, parent_name:str):
            nonlocal documents
            name = parent_name+bean.name
            for doc in bean.descriptions:
                documents.append(Document(
                    page_content=f'{name}:{doc}' if name else doc, 
                    metadata={
                        "name": name,
                        "eng_name": bean.eng_name,
                    }
                    ))
            for child in bean.children:
                to_document(child, name+'/')
        to_document(self, '')
        return documents
    
    def jsonfiy(self, texts:list):
        return (d.replace('\n', '\\n').replace('\r\n', '\\n').replace('"','\\"') for d in texts)