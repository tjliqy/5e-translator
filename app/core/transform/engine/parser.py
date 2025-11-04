import importlib.util

from bs4 import BeautifulSoup, NavigableString
from app.core.transform.bean.bestiary import Attr, BasicBean
from typing import List, Union
from pathlib import Path
from app.core.transform.engine.node_checker import *
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

# FONT_SIZE_PATTERN = r'FONT-SIZE:\s*(\d+\.?\d*)pt'

class LineInfo:
    def __init__(self, text: str, rate: int):
        self.text = text
        self.rate = rate


class HtmlParser:

    def __init__(self,
                 file_path: Union[str, Path],
                 open_encoding: Union[str, None] = None,
                 bs_kwargs: Union[dict, None] = None,
                 checker_list: List[NodeChecker] = [NodeChecker()]):
        try:
            import bs4
        except ImportError:
            raise ImportError(
                "beautifulsoup4 package not found, please install it with "
                "`pip install beautifulsoup4`"
            )
        self.file_path = file_path
        self.open_encoding = open_encoding
        if bs_kwargs is None:
            if not importlib.util.find_spec("lxml"):
                raise ImportError(
                    "By default BSHTMLLoader uses the 'lxml' package. Please either "
                    "install it with `pip install -U lxml` or pass in init arg "
                    "`bs_kwargs={'features': '...'}` to overwrite the default "
                    "BeautifulSoup kwargs."
                )
        bs_kwargs = {"features": "lxml"}
        self.bs_kwargs = bs_kwargs

        self.work_stack: List[BasicBean] = []
        self.lines: List[LineInfo] = []
        self.dictionary = {}
        self.index_dict = {}
        self.current_checker = -1
        self.checker_list = checker_list
        self.processed = False

    def __process_result(self, stack: List[BasicBean]) -> (bool):
        if (len(stack) == 0):
            return False
        for w in stack:
            if w.name == "":
                print(f"Error：当前节点标签名: {w.name}, 文本内容: {w.descriptions}")
                continue
            if w.eng_name != "":
                key = w.eng_name.lower()
                if key not in self.dictionary.keys():
                    self.dictionary[key] = set()
                self.dictionary[key].add(w.name)
            self.__process_result(w.children)
        return True

    def parse(self):
        with open(self.file_path, encoding=self.open_encoding) as f:
            self.soup = BeautifulSoup(f, **self.bs_kwargs)

        self.processed = False
        while (not self.processed):
            if (not self.set_next_checker()):
                print(f"解析失败:{self.file_path}")
                break
            self.lines = self.__html_to_lines(self.soup.body)
            for line in self.lines:
                self.__parser(line, self.work_stack)
            self.processed = self.__process_result(self.work_stack)
        return self.lines

    def get_documents(self) -> (List[Document]):
        res_documents = []
        documents = []
        for w in self.work_stack:
            documents.extend(w.get_documents())
        for d in documents:
            sentences = self.__split_sentences(d.page_content)
            if len(sentences) > 0:
                for s in sentences:
                    res_documents.append(Document(page_content=s, metadata=d.metadata))
            else:
                res_documents.append(d)
        return res_documents

    def set_next_checker(self) -> (bool):
        self.current_checker += 1
        if self.current_checker >= len(self.checker_list):
            return False
        self.checker = self.checker_list[self.current_checker]
        return True

    def __parser(self, line: LineInfo, stack: List[BasicBean]):
        if line.rate > NodeType.LINE.value:
            if len(stack) == 0 or line.rate >= stack[-1].rate:
                stack.append(BasicBean())
                stack[-1].rate = line.rate
                stack[-1].set_name(line.text)
            else:
                stack[-1].children = self.__parser(line, stack[-1].children)
        else:
            if len(stack) == 0:
                stack.append(BasicBean())
            tmp_stack = stack[-1]
            while (tmp_stack.children):
                tmp_stack = tmp_stack.children[-1]
            tmp_stack.set_text(line.text)
        return stack

    def __html_to_lines(self, node: BeautifulSoup) -> (List[LineInfo]):
        """
        逐行获取，给行评级。生成行List。
        """
        if (node is None):
            return []
        lines: List[LineInfo] = []
        if not node.name:
            if isinstance(node, str):
                lines.append(
                    LineInfo(node.replace("\n", ""), NodeType.CONTENT.value))
        elif self.checker.isBR(node):
            lines.append(LineInfo("\n", NodeType.BR.value))
        elif self.checker.isTable(node):
            lines.extend(self.__html_to_table_lines(node))
        else:
            node_rate = self.checker.rate(node)
            current_line = ""

            def add_current_line():
                """添加当前行到结果列表，并清空当前行"""
                nonlocal current_line
                if current_line:
                    lines.append(LineInfo(current_line, node_rate))
                    current_line = ""

            for child in node.children:
                child_lines = self.__html_to_lines(child)
                for child_line in child_lines:
                    if child_line.rate == NodeType.CONTENT.value:  # 如果是内容，说明这行没结束，则向current_line追加
                        current_line += child_line.text
                    elif child_line.rate == NodeType.BR.value:  # 如果换行了，则需要清空current_line
                        add_current_line()
                    else:  # 这种情况表示，不是内容或者换行符，而是行或者标题
                        add_current_line()
                        if child_line.rate < node_rate:
                            child_line.rate = node_rate
                        lines.append(child_line)

            add_current_line()
        return lines

    def __html_to_table_lines(self, node: BeautifulSoup):
        lines: List[LineInfo] = []
        if not self.checker.isTable(node):
            return lines

        trs = node.find_all('tr')
        # 检查是否至少有2行
        if len(trs) < 2:
            has_header = False
        else:
            first_tr = trs[0]
            second_tr = trs[1]
            first_tds = first_tr.find_all('td')
            second_tds = second_tr.find_all('td')

            # 检查第一行是否有有效文本
            has_valid_text = any(td.get_text(strip=True) for td in first_tds)

            # 检查第一行与第二行本身 node 与其子节点的 class、style 等属性是否完全一致
            attrs_match = True
            if len(first_tds) == len(second_tds):
                for td1, td2 in zip(first_tds, second_tds):
                    if td1.attrs != td2.attrs:
                        attrs_match = False
                        break
                    for child1, child2 in zip(td1.children, td2.children):
                        if isinstance(child1, NavigableString) != isinstance(child2, NavigableString):
                            attrs_match = False
                            break
                        elif isinstance(child1, NavigableString): # 两行子节点类型相等的情况，只需要判断一个的类型是否为字符串即可
                            continue
                        if child1.attrs != child2.attrs:
                            attrs_match = False
                            break
            else:
                attrs_match = False

            has_header = has_valid_text and (not attrs_match)

        row_titles: List[str] = []
        if has_header:
            for td in first_tr.find_all('td'):
                row_titles.append(td.get_text(strip=True))

        start_index = 1 if has_header else 0

        for index, tr in enumerate(trs):
            # 根据是否有标题行决定是否跳过第一行
            if index < start_index:
                continue
            row_content: str = ''

            if has_header:
                for title, td in zip(row_titles, tr.find_all('td')):
                    text = td.get_text(strip=True)
                    row_content += f'{title}:{text} '
            else:
                # 没有标题行，直接拼接单元格内容
                for td in tr.find_all('td'):
                    text = td.get_text(strip=True)
                    row_content += f'{text} '
            lines.append(LineInfo(row_content.strip(), NodeType.LINE.value))
        return lines
    
    def __split_sentences(self, text: str) -> (List[str]):
        """
        将中文文本分割为句子
        :param text: 未分句的中文文本
        :return: 分句后的中文句子列表
        """
        CHUNK_SIZE = 200

        # 知识库中相邻文本重合长度
        OVERLAP_SIZE = 30
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=OVERLAP_SIZE
        )
        return text_splitter.split_text(text)