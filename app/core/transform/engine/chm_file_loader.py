import os
import asyncio
from pathlib import Path
from typing import Dict, Iterator, Union

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

from config import HTML_ROOT_DIR, SKIP_HTML, SKIP_HTML_DIRS, BASE_CATEGORY
from app.core.transform.engine import HtmlParser

class CHMFileLoader(BaseLoader):
    def __init__(self,
            file_path: Union[str, Path],
            open_encoding: Union[str, None] = None,
            bs_kwargs: Union[dict, None] = None,
            get_text_separator: str = "",) -> (None):
        """initialize with path, and optionally, file encoding to use, and any kwargs
        to pass to the BeautifulSoup object.

        Args:
            file_path: The path to the file to load.
            open_encoding: The encoding to use when opening the file.
            bs_kwargs: Any kwargs to pass to the BeautifulSoup object.
            get_text_separator: The separator to use when calling get_text on the soup.
        """

        self.file_path = file_path
        self.open_encoding = open_encoding
        self.bs_kwargs = bs_kwargs
        self.get_text_separator = get_text_separator
        
    def lazy_load(self) -> (Iterator[Document]):
        parser: HtmlParser = HtmlParser(self.file_path, self.open_encoding, self.bs_kwargs)
        parser.parse()
        # print(self.file_path)
        documents = parser.get_documents()
        for d in documents:
            d.metadata['category'] = self.__parse_category()
            d.metadata['source'] = self.file_path
            yield d

    def __parse_category(self):
        for s in reversed(self.file_path.split('/')):
            # 去掉 .htm 和 .html 后缀
            if s.endswith('.htm'):
                s = s[:-4]
            elif s.endswith('.html'):
                s = s[:-5]
            for category, parttens in BASE_CATEGORY.items():
                if s in parttens:
                    return category
        return ''
    
def load_html_to_documents(root_dir=HTML_ROOT_DIR):
    """
    加载根目录下的所有HTML文件
    """
    html_documents = []
    for root, dirs, files in os.walk(root_dir):
        if any(d in SKIP_HTML_DIRS for d in root.split('/')):
            continue
        
        for file in files:
            if file in SKIP_HTML:
                continue
            if file.endswith('.html') or file.endswith('.htm'):
                file_path = os.path.join(root, file)
                loader = CHMFileLoader(file_path,open_encoding='gbk')

                html_documents.extend(loader.load())
                

    return html_documents

def combine_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

if __name__ == "__main__":
    html_files = load_html_to_documents('/data/DND5e_chm/城主指南2024')
    # print(html_files[0])