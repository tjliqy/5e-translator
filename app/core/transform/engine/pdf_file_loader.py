import os
import asyncio
from pathlib import Path
from typing import Dict, Iterator, Union

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

from .pdf_parser import PdfParser
from .word_parser import WordParser
from .txt_parser import TxtParser



class AdventureFileLoader(BaseLoader):
    def __init__(self,
            file_path: Union[str, Path],) -> (None):
        """initialize with path, and optionally, file encoding to use, and any kwargs
        to pass to the BeautifulSoup object.

        Args:
            file_path: The path to the file to load.
        """

        self.file_path = file_path
        # self.open_encoding = open_encoding
        
    def lazy_load(self) -> (Iterator[Document]):
        if self.file_path.endswith('.pdf'):
            parser: PdfParser = PdfParser(self.file_path)
            parser.parse()
            documents = parser.get_documents()
            for d in documents:
                # d.metadata['category'] = self.__parse_category()
                d.metadata['source'] = self.file_path
                # print(d)
                yield d
        elif self.file_path.endswith('.doc') or self.file_path.endswith('.docx'):
            parser: WordParser = WordParser(self.file_path)
            parser.parse()
            documents = parser.get_documents()
            print(len(documents))
            for d in documents:
                # d.metadata['category'] = self.__parse_category()
                d.metadata['source'] = self.file_path
                # print(d)
                yield d
        elif self.file_path.endswith('.txt'):
            parser: TxtParser = TxtParser(self.file_path)
            parser.parse()
            documents = parser.get_documents()
            for d in documents:
                # d.metadata['category'] = self.__parse_category()
                d.metadata['source'] = self.file_path
                # print(d)
                yield d
            
    
def load_adventure_files(root_dir):
    """
    加载根目录下的所有PDF文件
    """
    adventure_documents = []
    if not os.path.exists(root_dir):
        return []
    if os.path.isfile(root_dir):
        loader = AdventureFileLoader(root_dir)
        adventure_documents.extend(loader.load())
        return adventure_documents
    for root, dirs, files in os.walk(root_dir):
        # if any(d in SKIP_HTML_DIRS for d in root.split('/')):
        #     continue
        
        for file in files:
            # if file in SKIP_HTML:
            #     continue
            if file.endswith('.pdf') or file.endswith('.doc') or file.endswith('.docx') or file.endswith('.txt'):
                file_path = os.path.join(root, file)
                loader = AdventureFileLoader(file_path)
                adventure_documents.extend(loader.load())

    return adventure_documents

if __name__ == "__main__":
    html_files = load_adventure_files('/data/5e-translator/data')
    # print(html_files[0])