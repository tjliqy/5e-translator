import string
from app.core.transform.bean.basic_bean import *

SEGMENT_TYPE_BASIC = 0
SEGMENT_TYPE_ACTION = 1

CAMP_STR = ['守序', '中立', '混乱', '善良', '邪恶', '无阵营', '任意阵营', '任何阵营']
SIZE_STR = ['微型', '小型', '中型', '大型', '巨型']
GROUP_STR = ['异怪','野兽','类人','天界','天界生物','构装体','龙','元素','精类','邪魔','巨人','类人生物','怪兽','泥怪','植物','不死生物','亡灵']
SIZE_GROUP_STR= []
for s in SIZE_STR:
    for g in GROUP_STR:
        SIZE_GROUP_STR.append(s+g)
class Attr(BasicBean):
    def __init__(self):
        super().__init__()
        self.attrs = []

    def set_attrs(self, attr_list):
        self.attrs.extend(attr_list)

    def to_dict(self):
        return {
            "name": self.name,
            "eng_name": self.eng_name,
            "description": "\\n".join(self.jsonfiy(self.descriptions)),
            'attrs': [a.to_dict() for a in self.attrs],
        }


def split_by_dot(text: str):
    punctuations = string.punctuation+'，。！？： '
    # 构建正则表达式模式
    pattern = f'[{punctuations}]'
    # 使用 re.split 方法按标点符号分割字符串
    result = re.split(pattern, text)
    # 过滤掉分割结果中的空字符串
    result = [part.strip() for part in result if part]

    return result


def is_camp(text: str):
    result = split_by_dot(text)
    for r in result:
        if len(r) > 7:
            continue
        for c in CAMP_STR:
            if c in r:
                return True
    return False

def is_group(text: str):
    result = split_by_dot(text)
    for r in result:
        if len(r) > 7:
            continue
        for c in SIZE_GROUP_STR:
            if c in r:
                return True
        
    
class Bestiary(BasicBean):

    def __init__(self, bean=None):
        super().__init__()
        self.group = ''
        self.camp = ''
        self.speed = ''
        self.actions = []
        self.attrs = []
        self.intros = []
        self.segment_type = SEGMENT_TYPE_BASIC
        if bean:
            self.name = bean.name
            self.eng_name = bean.eng_name
            self.descriptions.extend(bean.descriptions)

    def set_group_and_camp(self, text):
        result = split_by_dot(text)
        # if len(result) != 2:
        #     print("解析阵营出错："+text)
        if is_camp(text):
            self.group = text[:-(len(result[-1])+1)].replace('\n', '')
            self.camp = result[-1].replace('\n', '')
        elif is_group(text):
            self.group = text.replace('\n', '')
    def set_attrs(self, attr_list: list):
        for attr in attr_list:
            if attr.name == "动作":
                self.actions.extend(attr.attrs)
            else:
                self.attrs.append(attr)

    def set_text(self, text):
        parts = split_by_dot(text)
        if self.segment_type == SEGMENT_TYPE_BASIC:
            if self.set_speed(text, parts):
                return
            # elif self.set_action(text, parts, check = True):
            #     return
            self.descriptions.append(text)
        # elif self.segment_type == SEGMENT_TYPE_ACTION:
        #     self.set_action(text, parts, check = False)

    # def set_action(self, text, text_parts, check = True):
    #     if check:
    #         if text == "动作":
    #             return True
    #         return False
    #     self.actions += text
    #     return True

    def set_speed(self, text, text_parts):
        if self.speed != '':
            return False
        if "速度" in text_parts:
            self.speed = text.replace('\n', '')
            return True
        elif "速度" in text:
            i = text.rfind("速度")
            if i+2 < len(text) and text[i+2].isdigit():
                self.speed = text.replace('\n', '')
                return True
        return False

    def try_set_intro(self, intro_list):
        for intro in intro_list:
            if self.eng_name == '':
                if intro.name == self.name and intro.eng_name != "":
                    self.eng_name = intro.eng_name
            if len(intro.descriptions) > 0:
                self.intros.extend(intro.descriptions)

    def to_dict(self):
        return {
            'name': self.name,
            'eng_name': self.eng_name,
            'group': self.group,
            'camp': self.camp,
            'speed': self.speed,
            'actions': [a.to_dict() for a in self.actions],
            'description': '\\n'.join(self.jsonfiy(self.descriptions)),
            'attrs': [a.to_dict() for a in self.attrs],
            'intro': '\\n'.join(self.jsonfiy(self.intros))
        }
