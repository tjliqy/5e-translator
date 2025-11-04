
from app.core.transform.bean.bestiary import Bestiary, Attr, is_camp, is_group, BasicBean
import re
import os
import sys
import fitz  # PyMuPDF库，用于更精确地提取文本和字体信息
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

if sys.version_info < (3, 9):
    from typing import List
else:
    List = list

class PdfParser:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.chinese_punctuation = r"。！？；…"
        self.chinese_sentence_pattern = re.compile(f'([^{self.chinese_punctuation}]*[{self.chinese_punctuation}])')
    
        
    def parse(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PDF文件不存在: {self.file_path}")
        if not self.file_path.lower().endswith('.pdf'):
            raise ValueError(f"文件不是PDF格式: {self.file_path}")
        
        try:
            self.doc = fitz.open(self.file_path)

            # 存储所有段落的列表，每个段落包含标题和内容
            self.paragraphs = []
            
            # 当前正在处理的段落
            current_paragraph = {
                'title': '',
                'content': []
            }
            all_blocks = []
            # 遍历每一页
            for page_num in range(len(self.doc)):
                # 获取当前页
                page = self.doc[page_num]
                
                # 提取页面中的所有文本块（包含字体信息）
                blocks = page.get_text("dict")["blocks"]
                all_blocks.extend(blocks)
                
            # 用于存储当前页的所有字体大小
            font_sizes = []
            
            # 第一次遍历：收集所有字体大小，用于确定标题阈值
            for block in all_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span.get("size") and span.get("text").strip():
                                font_sizes.append(span["size"])
            
            # 如果没有找到字体大小，使用默认阈值
            if not font_sizes:
                title_font_threshold = 14  # 默认标题字体大小阈值
            else:
                # 计算字体大小的中位数作为标题判断的参考
                font_sizes.sort()
                mid_index = len(font_sizes) // 2
                title_font_threshold = font_sizes[mid_index] * 1.2  # 比平均字体大20%的作为标题
            # print(title_font_threshold)
            # 第二次遍历：根据字体大小识别标题和正文
            pre_title = ""
            for block in all_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span.get("text", "").strip()
                            if not text or text.isspace():
                                continue
                            
                            # 获取字体大小
                            font_size = span.get("size", 0)
                            
                            # 判断是否为标题（字体较大）
                            if font_size >= title_font_threshold:
                                if len(current_paragraph['content']) == 0:
                                    current_paragraph['title'] += text
                                    continue
                                # 如果当前已有正在处理的段落且内容不为空，保存当前段落
                                if current_paragraph['title'] or len(current_paragraph['content']) > 0:
                                    if not current_paragraph['title']:
                                        current_paragraph['title'] = pre_title
                                        
                                    # current_paragraph['content'] = 
                                    self.paragraphs.append(current_paragraph)
                                pre_title = text
                                # 开始新的段落，设置标题
                                current_paragraph = {
                                    'title': text,
                                    'content': []
                                }
                            elif text != '':
                                # 正文内容，添加到当前段落
                                current_paragraph['content'].append(text)
            
            # 添加最后一个段落（如果有）
            if current_paragraph['title'] or current_paragraph['content']:
                self.paragraphs.append(current_paragraph)
            
            # 关闭文档
            self.doc.close()
            
            return self.paragraphs
        except Exception as e:
            raise RuntimeError(f"处理PDF文件时出错: {str(e)}")
        
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
    def get_documents(self) -> (List[Document]):
        documents = []
        for p in self.paragraphs:
            titles = self.__split_sentences(p['title'].replace('  ',' '))
            for t in titles:
                documents.append(Document(
                    page_content=t, 
                    # metadata={'title': p['title']}
                ))
            p['content'] = self.__split_sentences(' '.join(p['content']).replace('  ',' '))
            for c in p['content']:
                documents.append(Document(
                    page_content=c, 
                    # metadata={'title': p['title']}
                ))
        return documents
    