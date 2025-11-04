import json
from concurrent.futures import ThreadPoolExecutor
from app.core.database import DBDictionary, RedisDB
import re

db = DBDictionary()

def compare_term(term_path: str):
    with open(term_path, 'r') as f:
        lines = f.readlines()
        res:dict[str, str] = {}
        
        # 定义并发处理单行的函数
        def process_line(line):
            term = line.strip()
            cn, ok = db.get(term, load_from_sql=True)
            return term, cn if ok else ""
        
        # 使用线程池并发处理所有行
        with ThreadPoolExecutor() as executor:
            results = executor.map(process_line, lines)
            for term, cn in results:
                res[term] = cn
                print(f"{term} -> {cn}")
        
    with open("term.json", 'w') as f:
        f.write(json.dumps(res, ensure_ascii=False, indent=2))
        
def add_mysql_terms_to_redis():
    mysql_db = DBDictionary()
    redis_db = RedisDB(db=1)
    mysql_terms = mysql_db.get_all_term()
    redis_db.clean()
    for term in mysql_terms:
        redis_db.put(term.en, term.cn, term.category)
        print(f"{term.en} -> {term.cn}")
        
def combine_temp_terms_to_csv():
    mysql_db = DBDictionary()
    mysql_terms = mysql_db.get_all_term()
    print(len(mysql_terms))
    with open("temp_terms.csv", 'w') as f:
        for term in mysql_terms:
            f.write(f"{term.en},{term.cn},{term.category}\n")

def load_term_from_text(file_path: str):
    """
    从文本文件中加载术语，支持多种格式：
    1. 中文在前英文在后直接相连（如"桑缟Songal"）
    2. 中文在前英文在后，中间有空格（如"结阵魔法 Circle Magic"）
    3. 可能包含标点符号（如"什么是结阵法术？ What is a Circle Spell？"）
    4. 支持英文中的所有格和缩写形式（如"法师的法术书 Wizard's Spellbook"）
    5. 支持多词英文术语（如"咒火风暴 Spellfire Storm"）
    
    Args:
        file_path: 包含术语的文本文件路径
        
    Returns:
        dict: 以英文为key，中文为value的术语字典
    """
    try:
        # 尝试使用UTF-8编码打开文件，如果失败则尝试GBK
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
                
        res: dict[str, str] = {}
        
        # 改进的正则表达式，支持中文在前英文在后的多种格式
        # 1. 中文和英文直接相连的格式，支持撇号
        pattern1 = re.compile(r'(?P<chinese>[一-鿿·]+)(?P<english>[a-zA-Z\'\-]+)')
        
        # 2. 中文在前英文在后，中间可能有空格和标点的格式，支持多词术语和撇号
        # 优先匹配包含多个大写单词的专业术语格式
        pattern2 = re.compile(r'(?P<chinese>[一-鿿]+[^一-鿿·]*?)(?P<english>([A-Z][a-z]+\s?)+(Storm|Spell|Magic|Wizard|Sorcerer|Cleric|Druid|Paladin|Ranger|Warlock|Bard|Fighter|Rogue|Monk|Barbarian))')
        
        # 3. 通用格式，匹配任何英文内容
        pattern3 = re.compile(r'(?P<chinese>[一-鿿·]+[^一-鿿·]*?)(?P<english>[a-zA-Z][a-zA-Z\'\-\s]+[a-zA-Z])')
        
        patterns = [pattern2, pattern3, pattern1]  # 按优先级排序
        
        for line_number, line in enumerate(lines, 1):
            # 去除行首尾空白字符
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 尝试用多个正则表达式匹配，按优先级顺序
            matched = False
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    chinese_part = match.group('chinese').strip().rstrip('：:？?(（')
                    english_part = match.group('english').strip().replace('  ',' ')
                    
                    # 英文做key，中文做value存入字典
                    res[english_part] = chinese_part
                    print(f"行 {line_number}: 已解析 '{line}' -> {english_part} -> {chinese_part}")
                    matched = True
                    break
            
            if not matched:
                # 记录未匹配的行
                print(f"行 {line_number}: 未匹配到中文在前英文在后的格式: '{line}'")
        
        print(f"总共解析了 {len(res)} 个术语")
        for english, chinese in res.items():
            print(f"{english}: {chinese}")
        return res
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        return {}
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")
        return {}