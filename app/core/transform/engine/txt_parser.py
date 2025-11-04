import sys
if sys.version_info < (3, 9):
    from typing import List
else:
    List = list

import os
import re
from typing import List, Dict, Tuple
import os
import re
import sys
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


if sys.version_info < (3, 9):
    from typing import List, Dict, Tuple
else:
    List = list
    Dict = dict
    Tuple = tuple

# 导入所需的库
try:
    import docx2txt
    import olefile
    import subprocess
    import zipfile
    import shutil
    import tempfile
    # 添加python-docx库用于提取字体信息
    try:
        import docx
    except ImportError:
        print("请安装python-docx库以支持精确的字体信息提取: pip install python-docx")
        docx = None
except ImportError:
    print("请安装必要的库: pip install docx2txt olefile")
    sys.exit(1)

class TxtParser:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.chinese_punctuation = r"。！？；…"
        self.chinese_sentence_pattern = re.compile(f'([^{self.chinese_punctuation}]*[{self.chinese_punctuation}])')
        self.documents = []  # 存储解析后的段落
        self.paragraphs_with_format = []  # 存储带格式信息的段落

    def parse(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"TXT文件不存在: {self.file_path}")
        
        # 支持.doc和.docx格式
        file_ext = os.path.splitext(self.file_path)[1].lower()
        if file_ext != '.txt':
            raise ValueError(f"文件不是TXT格式: {self.file_path}")
        
        try:
            self._parse_txt_file()
            return self.documents
        except Exception as e:
            raise RuntimeError(f"处理TXT文件时出错: {str(e)}")
        
    def _parse_txt_file(self):
        """解析TXT文件，根据不同格式选择合适的解析方法"""
        try:
            # 读取TXT文件内容
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        split_contents = self.__split_sentences(line)
                        for content_chunk in split_contents:
                            self.documents.append(Document(page_content=content_chunk))
        except Exception as e:
            raise RuntimeError(f"解析TXT文件时出错: {str(e)}")

    def __split_sentences(self, text: str) -> List[str]:
        """
        将文本分割为适当大小的块
        """
        # 知识库中单段文本长度
        CHUNK_SIZE = 150
        
        # 知识库中相邻文本重合长度
        OVERLAP_SIZE = 30
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=OVERLAP_SIZE
        )
        
        return text_splitter.split_text(text)
    
    def get_documents(self) -> (List[Document]):
        
        return self.documents