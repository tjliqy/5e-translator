import json
import os
import chardet
from app.core.transform.engine.html_parser import BestiaryHtmlParser, BestiaryChecker2, BestiaryChecker3

def transfrom_dir(dir_path, old_format=False, dictionary={}):
    files = os.listdir(dir_path)  # 得到文件夹下的所有文件名称
    jsons = []
    for f in files:
        file_path = os.path.join(dir_path, f)
        if f.lower().endswith(".html") or f.lower().endswith(".htm"):
            # print(file_path)

            # file_path =os.path.join(dir_path,"纽吉怪.htm")

            with open(file_path, 'rb') as file:
                raw_data = file.read()

                detected_encoding = chardet.detect(raw_data)['encoding']
                # print(detected_encoding)
                html_content = raw_data.decode('gbk')
                if old_format:
                    bhp = BestiaryHtmlParser(file_path, html_content, [BestiaryChecker2(), BestiaryChecker3()])
                    jsons.extend(b.to_dict() for b in bhp.old_dfs())
                else:
                    bhp = BestiaryHtmlParser(file_path, html_content, [BestiaryChecker2()])
                    jsons.extend(b.to_dict() for b in bhp.dfs())
                dictionary.update(bhp.dictionary)

                # if len(jsons) == 0:
                #     print(file_path)
                # for j in jsons:
                # if len(j.actions) + len(j.attrs) + len(j.descriptions) == 0:
                #     print(j.name)
                # print(j.name)
                # print(j.eng_name)
                # print(f'acti:{len(j.actions)}')
                # print(f'attr:{len(j.attrs)}')
                # print(f'desc:{len(j.descriptions)}')

        elif os.path.isdir(file_path):
            jsons.extend(transfrom_dir(file_path))

    return jsons

def transfrom_bestiary(base_path, dictionary={}):
    
    wrong_paths = [
        # '布布的星界怪兽展',
        '范·里希腾的鸦阁魔域指南/鸦阁怪物', # 这个读不出来
        # '费资本的巨龙宝库/怪物图鉴', # 这个很少，可能有问题
        # '怪物图鉴',
        # '荒洲探险家指南/荒洲生物图集',
        # '拉尼卡公会长指南/生物',
        # '龙枪：龙后之影/盟友与敌人',
        # '塞洛斯之神话奥德赛/生物图鉴',
    ]
    dir_paths = [
        # '艾伯伦：从终末战争中崛起/新伙伴与敌人',
        # '艾奎兹玄有限责任公司/怪物',
        # '多元宇宙的怪物/图鉴',
        # '巨人之荣耀/图鉴',
        # # '模组', # 部分可以
        # '魔邓肯的众敌卷册/图鉴',
        # '莫提的位面游记',
        # '斯翠海文：混沌研习/图鉴',
        # '万象无常书',
        # '玩家手册2024/生物',
        # '瓦罗怪物指南/图鉴',
    ]

    json_results = {}
    for dp in wrong_paths:
        print(dp)
        dir_path = os.path.join(base_path, dp)
        file_jsons = transfrom_dir(dir_path, True, dictionary)
        json_results[dp] = file_jsons
    for dp in dir_paths:
        print(dp)
        dir_path = os.path.join(base_path, dp)
        file_jsons = transfrom_dir(dir_path, False, dictionary)
        json_results[dp] = file_jsons

    return json_results, dictionary


def test():
    file_path = '/data/DND5e_chm/范·里希腾的鸦阁魔域指南/鸦阁怪物/不可名状之恐怖.htm'
    with open(file_path, 'rb') as file:
        raw_data = file.read()

        detected_encoding = chardet.detect(raw_data)['encoding']
        # print(detected_encoding)
        html_content = raw_data.decode('gbk')

        bhp = BestiaryHtmlParser(file_path, html_content, [BestiaryChecker2(), BestiaryChecker3()])
        return bhp.old_dfs()