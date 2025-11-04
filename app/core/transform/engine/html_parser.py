
from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod
from app.core.transform.bean.bestiary import Bestiary, Attr, is_camp, is_group, BasicBean
import re
import sys
if sys.version_info < (3, 9):
    from typing import List
else:
    List = list
    
def is_new_line(segment):
    previous = segment.previous_sibling
    return previous and previous.name == 'br'


HTML_BR = -1
CONTENT = 0
TITLE_SECONDARY = 1
TITLE_PRIMARY = 2
FONT_SIZE_PATTERN = r'FONT-SIZE:\s*(\d+\.?\d*)pt' 

line_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'div']

class NodeChecker(metaclass=ABCMeta):
    @abstractmethod
    def isPrimaryTitle(self, node):
        pass
    @abstractmethod
    def isSecondaryTitle(self, node):
        pass
    def isContent(self, node):
        pass
    @abstractmethod
    def isBR(self, node):
        pass
    
class BestiaryChecker2(NodeChecker):
    def isPrimaryTitle(self, node):
        pattern = re.compile(FONT_SIZE_PATTERN, re.IGNORECASE)
        if node.has_attr('style'):
            match = pattern.search(node['style'])
            if match:
                font_size = float(match.group(1))
                if font_size >= 13.4:
                    return True
        return False
    def isSecondaryTitle(self, node):
        return node.name == 'b'
    def isContent(self, node):
        return node.name in line_tags
    
    def isBR(self, node):
        return node.name == 'br'
    
    def isBestiaryTextInParser(self, bean :BasicBean, text):
        return bean.name != "" and len(bean.descriptions) ==0 and (is_camp(text) or is_group(text))

class BestiaryChecker3(BestiaryChecker2):
    def isPrimaryTitle(self, node):
        if super().isPrimaryTitle(node):
            return True
        if 'COLOR: rgb(99,36,35)' in node.get('style', ''):
            return True
        return False
        

class BestiaryHtmlParser:
    
    def __init__(self, file_path ,html, checker_list :List[NodeChecker]):
        self.file_path = file_path
        self.soup = BeautifulSoup(html, 'html.parser')
        self.bestiary_list = []
        self.work_stack = []
        self.dictionary = {}
        self.index_dict = {}
        self.current_checker = -1
        self.checker_list = checker_list
    
    def __process_result(self) -> (bool):
        intros = []
        attr_list = []
        while len(self.work_stack) > 0:
            w = self.work_stack.pop()
            if w.name == "":
                continue
            if w.eng_name != "":
                key = w.eng_name.lower()
                if key not in self.dictionary.keys():
                    self.dictionary[key] = set()
                self.dictionary[key].add(w.name)
                
            if w.name == "动作":
                a = Attr()
                a.set_name("动作")
                a.set_attrs(attr_list)
                a.set_text("\n".join(d.replace("\n", "") for d in w.descriptions))
                attr_list = [a]
            elif isinstance(w, Bestiary):
                w.set_attrs(attr_list)
                attr_list = []
                self.bestiary_list.append(w)
            elif isinstance(w, Attr):
                attr_list.append(w)
            else:
                intros.append(w)
        if len(self.bestiary_list) == 0:
            # print (self.file_path)
            return False
            # for a in attr_list:
            #     print(a.to_dict())
        for b in self.bestiary_list:
            b.try_set_intro(intros)
            # print(b.to_dict())
        return True
    
    def old_dfs(self):
        ok = False
        while (not ok):
            if (not self.set_next_checker()):
                print(f"解析失败:{self.file_path}")
                break
            self.__old_dfs(self.soup.body)
            ok = self.__process_result()
        return self.bestiary_list
    
    def set_next_checker(self) -> (bool):
        self.current_checker += 1
        if self.current_checker >= len(self.checker_list):
            return False
        self.checker = self.checker_list[self.current_checker]
        return True
    def __parser(self, title, result_strs, text_type):
        text = "".join(result_strs)
        if text_type == TITLE_PRIMARY and title != "":
            self.work_stack.append(BasicBean())
            self.work_stack[-1].set_name(title)
        elif text_type == TITLE_SECONDARY and title != "":
            if len(result_strs) > 0:
                self.work_stack.append(Attr())
                self.work_stack[-1].set_name(title)
            else:
                result_strs.insert(0, title)
        if len(self.work_stack) > 0 and text != "":
            if self.work_stack[-1].name == "":
                self.work_stack[-1].set_name(text)
            elif self.checker.isBestiaryTextInParser(self.work_stack[-1], text):
                self.work_stack[-1] = Bestiary(self.work_stack[-1])
                self.work_stack[-1].set_group_and_camp(text)
            else:
                self.work_stack[-1].set_text(text)
    
    def __old_dfs(self, node):
        result_strs = []
        text_type = CONTENT
        pattern = re.compile(FONT_SIZE_PATTERN, re.IGNORECASE)
        if self.checker.isPrimaryTitle(node):
            text_type = TITLE_PRIMARY
        elif self.checker.isSecondaryTitle(node):
            text_type = TITLE_SECONDARY
        elif self.checker.isBR(node):
            return "", HTML_BR
        if node.name in line_tags:
            title = ""
            # print(f"当前节点标签名: {node.name}, 文本内容: {node.get_text(strip=True)}")
            for child in node.children:
                if child.name:
                    res, child_type = self.__old_dfs(child)
                    if child_type == HTML_BR:
                        # 逐行分析
                        self.__parser(title, result_strs, text_type)
                        title = ""
                        result_strs = []
                        text_type = CONTENT
                    if child_type > text_type:
                        text_type = child_type
                    if child_type > CONTENT:
                        title += res
                    else:
                        result_strs.append(res)
                        
            self.__parser(title, result_strs, text_type)
            return "", CONTENT
        else:
            for child in node.children:
                if child.name:
                    res, child_type = self.__old_dfs(child)
                    if child_type == HTML_BR:
                        self.__parser('',"".join(result_strs), text_type)
                        result_strs = []
                        text_type = HTML_BR
                    if child_type > text_type:
                        text_type = child_type
                    result_strs.append(res)
                elif isinstance(child, str) and child.strip():
                        result_strs.append(child.strip())
                        # print(f"当前节点标签名: {node.name}, 文本内容: {child.strip()}")
        # if temp_texts:
        #     print(f"当前节点标签名: {node.name}, 文本内容: {temp_texts}")
            
        return "".join(result_strs), text_type
    
    
    
    def dfs(self):
        self.__dfs(self.soup.body)
        self.__process_result()
        return self.bestiary_list
        
    def __dfs(self,node):
        result_strs = []
        if node.name == 'font' and node.get('color') == "#800000":
            self.work_stack.append(BasicBean())
            self.work_stack[-1].set_name(node.get_text(strip=True))
            return ""
        if node.name == 'strong':
            self.work_stack.append(Attr())
        for child in node.children:
            if child.name:
                self.__dfs(child)
            elif isinstance(child, str) and child.strip():
                if len(self.work_stack) > 0:
                    if self.work_stack[-1].name == "":
                        self.work_stack[-1].set_name(child)
                    elif is_camp(child):
                        self.work_stack[-1] = Bestiary(self.work_stack[-1])
                        self.work_stack[-1].set_group_and_camp(child)
                    else:
                        self.work_stack[-1].set_text(child)
                else:
                    result_strs.append(child.strip())
                    # print(f"当前节点标签名: {node.name}, 文本内容: {child.strip()}")
        # if temp_texts:
        #     print(f"当前节点标签名: {node.name}, 文本内容: {temp_texts}")
            
        return "\n".join(result_strs)
    
