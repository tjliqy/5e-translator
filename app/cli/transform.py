import os
import re
from bs4 import BeautifulSoup
from app.core.transform import load_html_to_documents,load_adventure_files
from app.core.database import ChromaAdapter
from uuid import uuid4
from langchain_chroma import Chroma
from app.core.embedding.silicon_embeddings import SiliconAIEmbeddings
from config import CHROMA_PERSIST_DIR
import shutil
import os

def transform_html_2_txt(base_path):
    """
    转换html文件为txt文件
    转换base_path目录下的所有html文件为txt文件
    转换后的txt文件与html文件在同一目录下，文件名相同，只是扩展名不同
    转换后的txt文件内容为html文件的文本内容，不包含html标签

    Args:
        base_path (str): HTML文件所在的基础目录路径
    """
    # 检查目录是否存在
    if not os.path.isdir(base_path):
        raise ValueError(f"目录不存在: {base_path}")

    # 遍历目录下所有HTML文件
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                html_path = os.path.join(root, file)
                txt_path = os.path.splitext(html_path)[0] + '.txt'

                # 读取并解析HTML内容
                try:
                    encodings = ['utf-8', 'gbk', 'latin-1']
                    content = None
                    
                    for encoding in encodings:
                        try:
                            with open(html_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    soup = BeautifulSoup(content, 'html.parser')

                    # 提取文本内容（保留原始HTML换行结构）
                    text_parts = []
                    for element in soup.descendants:
                        if element.name is None:
                            # 处理文本节点
                            if element:
                                text_parts.append(element.replace('\n',''))
                        elif element.name == 'br':
                            # 处理<br>标签为换行
                            text_parts.append('\n')
                        elif element.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul', 'ol']:
                            # 块级元素前后添加空行
                            text_parts.append('\n\n')

                    # 合并内容并处理连续空行
                    text_content = ''
                    for i, t in enumerate(text_parts):
                        # 如果连续2个t都是英文，则判断他们之前有没有空格，没有则加一个
                        if i != 0 and re.match(r'^[a-zA-Z]+$', t) and re.match(r'^[a-zA-Z]+$', text_parts[i-1]):
                            if not re.search(r'[a-zA-Z]\s+[a-zA-Z]', t + text_parts[i-1]):
                                text_content += ' '
                        text_content += t
                    # 替换多个连续换行符为两个换行符（保留段落结构）
                    text_content = re.sub(r'\n+', '\n\n', text_content).strip()

                    # 写入TXT文件
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)

                    print(f"转换完成: {html_path} -> {txt_path}")

                except Exception as e:
                    print(f"处理文件失败 {html_path}: {str(e)}")
                    
def load_files_into_chroma_db(adventure_dir):
    """
    加载PDF文件到Chroma数据库
    """
    
    documents = load_adventure_files(adventure_dir)
    knowledge_db:ChromaAdapter = ChromaAdapter()
    # for d  in list(filter(lambda d: len(d.page_content) > 512, documents)):
    #     print(d.page_content)
    # documents = list(filter(lambda d: len(d.page_content) < 512, documents))
    
    knowledge_db.reset()
    knowledge_db.add(documents)

def load_chm_files_into_chroma_db(chm_dir):
    """
    加载CHM文件到Chroma数据库
    """
    documents = load_html_to_documents(chm_dir)
    knowledge_db:ChromaAdapter = ChromaAdapter()
    knowledge_db.reset()
    knowledge_db.add(documents)
    

if __name__ == '__main__':
    load_files_into_chroma_db('/data/DND5e_chm/城主指南2024')