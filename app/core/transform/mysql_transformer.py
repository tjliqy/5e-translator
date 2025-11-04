from app.core.database import MySQLDatabase
from config import DB_CONFIG, logger
from langchain_core.documents import Document


def get_proofread_words():
    """从Mysql获取所有已校对的单词列表
    """
    db = MySQLDatabase(host=DB_CONFIG['HOST'],
                       port=DB_CONFIG['PORT'],
                       user=DB_CONFIG['USER'],
                       password=DB_CONFIG['PASSWORD'],
                       database=DB_CONFIG['DATABASE'])
    res = db.select('words', columns=['en', 'cn', 'category'], condition={'proofread': 1})
    for r in res:
        yield r


def is_nessesary_embedding(word):
    """判断单词是否需要embedding
    """
    # 完全相等则不需要embedding
    print(word)
    if word['en'] == word['cn']:
        return False


def word_to_document(word):
    """将单词转换为document
    """
    return Document(
        page_content=f"{word['en']}:{word['cn']}",
        metadata={
            "name": word['cn'],
            "eng_name": word['en'],
            "category": word['category'],
            "source": "database"
        }
    )