import os
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
load_dotenv()

HTML_ROOT_DIR = os.getenv("HTML_ROOT_DIR")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



SKIP_HTML=[
    '写在前面.html',
    '更新日志.html',
    '空白页模板.htm',
    'Credits.htm',
    '城主指南2024.htm'
]

SKIP_HTML_DIRS=[
    '废弃文件留档（不全书内无链接，应该',
    '空白页模板',
    '鸣谢',
    '写在前面.files'
]


# 解析引擎
LINE_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'div']
