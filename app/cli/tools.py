import os
import re
from typing import List
from config import CHM_ROOT_DIR, BESTIARY_FILE_MAP

def merge_txt(base_dir: str):
    """
    在base_dir文件夹中查找包含.txt文件（包括子目录中的）
    并将其中的txt合并为一个
    """
    # 检查目录是否存在
    if not os.path.exists(base_dir):
        print(f"错误：目录 {base_dir} 不存在")
        return
    
    # 收集所有的.txt文件（包括子目录中的）
    txt_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
                print(f"找到文件：{file}")
    
    # 如果没有找到.txt文件，提示用户
    if not txt_files:
        print(f"在 {base_dir} 中没有找到.txt文件（包括子目录）")
        return
    
    # 创建合并后的文件名
    merged_filename = os.path.join(base_dir, "merged_result.txt")
    
    # 合并文件内容
    try:
        with open(merged_filename, 'w', encoding='utf-8') as outfile:
            for file_path in txt_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        # 添加文件路径作为分隔符，便于识别内容来源
                        relative_path = os.path.relpath(file_path, base_dir)
                        # 写入文件内容
                        outfile.write(infile.read())
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错：{e}")
        print(f"成功合并 {len(txt_files)} 个文件（包括子目录中的文件）到 {merged_filename}")
    except Exception as e:
        print(f"创建合并文件时出错：{e}")


def split_spells_in_xphb(xphb_spell_dir:str) -> List[str]:
    """
    从怪物图鉴2025中提取所有法术的目录
    """
    # 检查目录是否存在
    if not os.path.exists(xphb_spell_dir):
        print(f"错误：目录 {xphb_spell_dir} 不存在")
        return []
    
    # 收集所有的.txt文件（包括子目录中的）
    txt_files = []
    for root, dirs, files in os.walk(xphb_spell_dir):
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
                print(f"找到文件：{file}")
    
    
    # 如果没有找到.txt文件，提示用户
    if not txt_files:
        print(f"在 {xphb_spell_dir} 中没有找到法术目录（包括子目录）")
        return []
    
    try:
        # with open(merged_filename, 'w', encoding='utf-8') as outfile:
        spell_item = {
            'cn': '',
            'en': '',
            'content':''
        }
        def write_spell_item(spell_item: dict):
            # print(spell_item)
            if spell_item['cn'] and spell_item['en'] and spell_item['content']:
                try:
                    with open(os.path.join(xphb_spell_dir, f"spells/{spell_item['en'].lower()}.txt"), 'a', encoding='utf-8') as outfile:
                        outfile.write(f"{spell_item['cn']}\n{spell_item['en']}\n{spell_item['content']}\n")
                except Exception as e:
                    print(f"写入文件 {spell_item['en']}.txt 时出错：{e}")    
            else:
                print(f"跳过空项：{spell_item['cn']}")
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    while line := infile.readline():
                        if '｜' in line:
                            split_line = line.split('｜')
                            # print(split_line)
                            if len(split_line) == 2:
                                # 先写入当前spell_item
                                write_spell_item(spell_item)
                                # 清空当前spell_item
                                spell_item = {
                                    'cn': '',
                                    'en': '',
                                    'content':''
                                }
                                spell_item['cn'] = split_line[0].strip()
                                spell_item['en'] = split_line[1].strip()
                                continue
                        if line.strip() and 'coding:' not in line:
                            spell_item['content'] += line.strip() + '\n'

            except Exception as e:
                print(f"读取文件 {file_path} 时出错：{e}")
        write_spell_item(spell_item)

    except Exception as e:
        print(f"{e}")
        
    # return txt_files

def split_bestiary_in_chm(bestiary_dir:str):
    """
    从不全书的指定文件夹中提取所有怪物的目录
    """
    # 检查目录是否存在
    if not os.path.exists(bestiary_dir):
        print(f"错误：目录 {bestiary_dir} 不存在")
        return []
    
    # 收集所有的.txt文件（包括子目录中的）
    txt_files = []
    for root, dirs, files in os.walk(bestiary_dir):
        if 'bestiary' in root:
            continue
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    
    # 如果没有找到.txt文件，提示用户
    if not txt_files:
        print(f"在 {bestiary_dir} 中没有找到怪物图鉴目录（包括子目录）")
        return []
    
    try:
        # with open(merged_filename, 'w', encoding='utf-8') as outfile:

        def write_bestiary_item(bestiary_item: dict):
            # print(spell_item)
            if bestiary_item['cn'] and bestiary_item['en'] and bestiary_item['content']:
                try:
                    with open(os.path.join(bestiary_dir, f"bestiary/{bestiary_item['en'].lower()}.txt"), 'a', encoding='utf-8') as outfile:
                        outfile.write(f"{bestiary_item['cn']}\n{bestiary_item['en']}\n{bestiary_item['content']}\n")
                except Exception as e:
                    print(f"写入文件 {bestiary_item['en']}.txt 时出错：{e}")    
            else:
                print(f"跳过空项：{bestiary_item['cn']}")
        for file_path in txt_files:
            bestiary_item = {
                'cn': '',
                'en': '',
                'content':''
            }
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    bestiary_item['cn'] = os.path.basename(file_path).split('.')[0]
                    while line := infile.readline():
                        if line.strip() == '':
                            continue
                        elif "coding:" in line:
                            continue
                        elif  bestiary_item['en'] == '':
                            # 怪物图鉴的格式命名为先中文名再英文名，中间可能没有分隔符，只截取英文部分
                            en_match = re.search(r'[A-Za-z0-9\s\-\'"]+', line)
                            if en_match:
                                bestiary_item['en'] = en_match.group(0).strip()
                            # 如果没有匹配到，使用整行作为英文名称（去掉多余空格）
                            if not bestiary_item['en']:
                                bestiary_item['content'] += line
                        else:
                            # 英文名称已设置，将剩余内容添加到content字段
                            bestiary_item['content'] += line
                        
                    write_bestiary_item(bestiary_item)

            except Exception as e:
                print(f"读取文件 {file_path} 时出错：{e}")

    except Exception as e:
        print(f"{e}")
        
    # return txt_files
    
if __name__ == "__main__":
    # merge_txt("/data/DND5e_chm/怪物图鉴2025")
    # split_spells_in_xphb("/data/DND5e_chm/玩家手册2024/法术详述")
    for bestiary_dir in BESTIARY_FILE_MAP.values():
        split_bestiary_in_chm(os.path.join(CHM_ROOT_DIR, bestiary_dir))
