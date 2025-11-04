import re
from config import SKIP_PATTERN, SKIP_PREFIX, SKIP_SUFFIX, TOTAL_SKIP_PREFIX, SKIP_KEYS, SKIP_KEY_PATH, SKIP_ITEMS, FORCE_TRANSLATE_STR, logger
import json


def check_skip_key(key: str, value: str, prefix_key_path: str):
    """根据key检查是否跳过

    Args:
        key (str): 当前key
        history_key_path (str): 前缀key

    Returns:
        _type_: _description_
    """
    if key in SKIP_KEYS:
        return True
    key_with_prefix = prefix_key_path+'/'+key
    return any(hk in key_with_prefix for hk in SKIP_KEY_PATH) or \
        any(si['key'] == key and si['value'] == value for si in SKIP_ITEMS)


def check_prefix(input_str: str):
    prefix = ""
    res_str = input_str
    for sp in TOTAL_SKIP_PREFIX:
        if input_str.startswith(sp):
            prefix = input_str
            res_str = ""
    for sp in SKIP_PREFIX:
        if input_str.startswith(sp):
            prefix = sp
            res_str = input_str[len(sp):]
            break
    return res_str, prefix


def check_suffix(input_str: str):
    suffix = ""
    res_str = input_str
    for sp in SKIP_SUFFIX:
        if input_str.endswith(sp):
            suffix = sp
            res_str = input_str[:-len(sp)]
            break
    return res_str, suffix


def need_translate_str(input_str: str):
    input_str, _ = check_prefix(input_str)
    input_str, _ = check_suffix(input_str)

    # 长度小于2的不翻译
    if len(input_str) <= 2 and input_str.lower() not in FORCE_TRANSLATE_STR:
        return False
    # 包含中文字符的不翻译
    in_pattern_num = 0
    for ch in input_str:
        if ch == '{':
            in_pattern_num += 1
        elif ch == '}':
            in_pattern_num -= 1
        elif in_pattern_num == 0 and u'\u4e00' <= ch <= u'\u9fff':
            return False
    # 正则匹配到的不翻译
    for p in SKIP_PATTERN:
        if re.search(p, input_str):
            return False
        
    if re.fullmatch(r'\d{1,3}(?:,\d{3})*\s+gp', input_str):
        return False
    return True

def parse_foundry_items_uuid_format(text: str) -> (tuple[list[str], list[str], bool]):
    """处理foundry-items.json中uuid的格式一般是@tag[xxx|yyy]

    Args:
        text (str): 待处理的字符串

    Returns:
        str: 处理后的字符串
    """
    tag_list = []
    value_list = []
    is_valid = True
    
    # 匹配 @tag[xxx|yyy] 格式
    pattern = r'@(\w+)\[([^\]]+)\]'
    matches = re.findall(pattern, text)
    if not matches:
        return [],[],False
    
    for match in matches:
        temp_value_list = [match[1]] if '|' not in match[1] else match[1].split('|')
        for _ in range(len(temp_value_list)):
            tag_list.append(match[0])
        value_list.extend(temp_value_list)
        
    return tag_list, value_list, is_valid

def parse_custom_format(text: str, get_sub_format=True) -> (tuple[list[str], list[str], bool]):
    """处理{@tag value}或{@tag}自定义格式的字符串
    将其转化为 taglist 和 valuelist

    Args:
        text (str): 待处理的字符串
        get_sub_format (bool, optional): 是否递归处理内部的{@tag value}格式. Defaults to True.

    Returns:
        tuple[list[str], list[str], bool]: tag列表，value列表，是否有效
    """
    tag_list = []
    value_list = []
    index = 0
    is_valid = True  # 标记是否是有效格式

    while index < len(text):
        # 查找 {@ 标记的起始位置
        start_index = text.find("{@", index)
        # 若没找到，则不需要处理，直接返回
        if start_index == -1:
            # TODO 这里需要确认一下是否需要将is_valid设为False
            break
        # 找到 tag 的开始位置
        start_tag = start_index + 2
        # 找到 tag 结束的位置
        end_tag = text.find(" ", start_tag)
        # 若没找到空格，则是 {@tag}这种结构
        if end_tag == -1:
            end_index = text.find("}", start_tag)
            # 若没找到结束的}，则是无效格式
            if end_index == -1:
                is_valid = False
                index = start_index + 1  # TODO 为什么这么做？
                continue
            # {@tag}的格式只需要给tag赋值
            tag = text[start_tag:end_index]
            value = ""
        else:
            # 处理{@tag value}的格式
            tag = text[start_tag:end_tag]
            temp_end_tag = tag.find("}")
            if temp_end_tag != -1:
                # 若在tag中找到}，则需要截取tag
                # 可能是{@tag} other_str的情况
                end_tag -= (len(tag) - temp_end_tag)
                tag = tag[:temp_end_tag]
                value = ""
                current_index = end_tag + 1
            else:
                # 找到 value 部分，处理嵌套情况
                start_value = end_tag + 1
                brace_count = 1  # 嵌套层级
                current_index = start_value
                # 校验{}是否成对出现
                while current_index < len(text):
                    if text[current_index] == "{":
                        brace_count += 1
                    elif text[current_index] == "}":
                        brace_count -= 1
                        if brace_count == 0:  # 找到和最外层{@匹配的}
                            break
                    current_index += 1
                # 若{}没有成对出现，则是无效格式
                if brace_count != 0:
                    index = start_index + 1
                    is_valid = False
                    continue
                # 给value赋值
                value = text[start_value:current_index]
        # 存储结果
        tag_list.append(tag)
        value_list.append(value)

        if is_valid and get_sub_format:
            # 递归处理 value 中可能存在的嵌套结构
            nested_tag, nested_value, nested_is_valid = parse_custom_format(
                value, True)
            # 若嵌套结构无效，则当前结构也无效
            is_valid = is_valid and nested_is_valid
            tag_list.extend(nested_tag)
            value_list.extend(nested_value)
        index = current_index + 1 if end_tag != - \
            1 else start_index + len(tag) + 3
    return tag_list, value_list, is_valid


def only_has_format(text):
    """判断除了{@aaa bbb}格式以外的部分有没有英文（即是否可以使用英文原文），有则为False， 没有则为True
        
    Args:
        text (str): 待处理的字符串

    Returns:
        bool: 若只有{@tag xxx}的文本，则返回True， 否则返回False
    """
    # 移除所有 {@aaa bbb} 格式的内容
    while "{@" in text:
        start_index = text.find("{@")
        brace_count = 1
        current_index = start_index + 2
        while current_index < len(text):
            if text[current_index] == "{":
                brace_count += 1
            elif text[current_index] == "}":
                brace_count -= 1
                if brace_count == 0:
                    break
            current_index += 1
        if brace_count != 0:
            return False
        text = text[:start_index] + text[current_index + 1:]
    # 检查剩余部分是否有英文
    return not bool(re.search(r'[a-zA-Z]', text))


def split_string(text):
    result = []
    current_part = ""
    in_special_format = False
    i = 0
    while i < len(text):
        if text[i:i + 2] == "{@" and not in_special_format:
            # 进入特定格式
            in_special_format = True
            current_part += text[i:i + 2]
            i += 2
        elif text[i] == '}' and in_special_format:
            # 离开特定格式
            in_special_format = False
            current_part += text[i]
            i += 1
        elif text[i] == '|' and not in_special_format:
            # 遇到分隔符且不在特定格式内
            result.append(current_part)
            current_part = ""
            i += 1
        else:
            # 普通字符，继续积累
            current_part += text[i]
            i += 1

    # 添加最后一部分
    if current_part:
        result.append(current_part)
    return result


def tag_duplicate_removal(en_match_k, en_match_v, cn_match_k, cn_match_v):
    # 去重
    en_match_kr = []
    en_match_vr = []
    cn_match_kr = []
    cn_match_vr = []
    for i in range(len(en_match_k)):
        new_tag = True
        for j in range(len(en_match_kr)):
            if (en_match_k[i], en_match_v[i]) == (en_match_kr[j], en_match_vr[j]):
                new_tag = False
                break
        if new_tag:
            en_match_kr.append(en_match_k[i])
            en_match_vr.append(en_match_v[i])
            cn_match_kr.append(cn_match_k[i])
            cn_match_vr.append(cn_match_v[i])
    return en_match_kr, en_match_vr, cn_match_kr, cn_match_vr


def reset_tags_index(en_match_k, en_match_v, cn_match_k, cn_match_v):
    """按照英文的tag顺序对中文的tag重新排序

    Args:
        en_match_k (_type_): 英文tag列表
        en_match_v (_type_): 英文value列表
        cn_match_k (_type_): 中文tag列表
        cn_match_v (_type_): 中文value列表

    Returns:
        _type_: _description_
    """
    # 如果tag完全相同，则直接返回
    # TODO 可能出现tag相同但value顺序颠倒的情况
    if en_match_k == cn_match_k:
        return True, en_match_k, en_match_v, cn_match_k, cn_match_v

    en_match_kr = []
    en_match_vr = []
    cn_match_kr = []
    cn_match_vr = []

    tmp_kr = []
    tmp_vr = []
    while len(en_match_k) > 0:
        emk = en_match_k.pop()
        emv = en_match_v.pop()
        get_matching_tag = False
        while len(cn_match_k) > 0:
            cmk = cn_match_k.pop()
            cmv = cn_match_v.pop()
            if emk == cmk:
                get_matching_tag = True
                en_match_kr.append(emk)
                en_match_vr.append(emv)
                cn_match_kr.append(cmk)
                cn_match_vr.append(cmv)
                break
            else:
                tmp_kr.append(cmk)
                tmp_vr.append(cmv)
        if get_matching_tag:
            cn_match_k.extend(tmp_kr)
            cn_match_v.extend(tmp_vr)
            tmp_kr = []
            tmp_vr = []
        else:
            return False, None, None, None, None
    return True, en_match_kr, en_match_vr, cn_match_kr, cn_match_vr


def strip_name(name:str):
    """对字符串进行精简
    1. 去除前缀和后缀括号中的内容
    2. 去除前缀和后缀中的{aaa bbb}格式
    3. 去除前缀和后缀中的空格
    Args:
        name (str): 需要处理的字符串

    Returns:
        str: 处理后的精简字符串
    """
    import re
    
    # 先去除首尾空格
    s = name.strip()
    
    # 定义要处理的模式对：(前缀模式, 后缀模式)
    patterns = [
        (r'^\(.*?\)', r'\(.*?\)$'),  # 括号
        (r'^\{.*?\}', r'\{.*?\}$'),  # 大括号
    ]
    
    # 对每种模式，反复移除前缀和后缀，直到不再变化
    for prefix_pattern, suffix_pattern in patterns:
        while True:
            new_s = re.sub(prefix_pattern, '', s)
            new_s = re.sub(suffix_pattern, '', new_s)
            if new_s == s:
                break
            s = new_s.strip()  # 每次替换后重新去除空格
    
    # 最后再去除一次空格
    return s.strip().lower()


def replace_cn_pattern(cn_str: str, en_str: str) -> (str):
    """检查类似{@item xxx} 被翻译为{@物品 xxx}的情况

    Args:
        cn_str (str): 中文字符串
        en_str (str): 英文字符串

    Returns:
        str: 替换回英文pattern的字符串
    """
    if isinstance(cn_str, str) and isinstance(en_str, str):
        #
        cn_match = re.findall(r"{@(\w+)", cn_str)
        en_match = re.findall(r"{@(\w+)", en_str)
        if cn_match and en_match:
            if len(cn_match) != len(en_match):
                return cn_str
            for i, m in enumerate(cn_match):
                for ch in m:
                    # 检查是否为中文
                    if "\u4e00" <= ch <= "\u9fff":
                        cn_str = cn_str.replace(m, en_match[i])
                        break
    return cn_str


def format_llm_msg(msg: str) -> (tuple[object, bool]):
    """格式化llm返回的消息

    Args:
        msg (str): llm返回的消息

    Returns:
        tuple[object, bool]: 格式化后的消息和是否成功
    """
    # 检查是否包含json代码块格式
    if msg.find("```json") != -1:
        start_index = msg.find("```json") + len("```json")
        end_index = msg.find("```", start_index)
        if end_index == -1:
            return None, False
        json_content = msg[start_index:end_index]
    # 检查是否有大括号包裹的部分
    elif msg.find("{") != -1:
        start_index = msg.find("{")
        left_ = 1  # 大括号的层级
        for i in range(start_index+1, len(msg)):
            if msg[i] == "{":
                left_ += 1
            elif msg[i] == "}":
                left_ -= 1
            if left_ == 0:
                json_content = msg[start_index: i+1]
                break
        if left_ != 0:
            return None, False
    else:
        return None, False
    try:
        kimi_data = json.loads(json_content)
        return kimi_data, True
    except json.decoder.JSONDecodeError as e:
        try:
            # 替换中文的引号,使得json可以解析
            json_content = json_content.replace("  “", '  "').replace("”:", '":').replace(
                "”：", '":').replace("”,\n", '",\n').replace("”\n", '"\n')
            kimi_data = json.loads(json_content)
            return kimi_data, True
        except json.decoder.JSONDecodeError as _:
            # 解析不出来的情况，认为需要手动解析，
            logger.error("手动解析" + json_content)
            return None, False

def get_tag_from_rel_path(rel_path: str):
    if '/' in rel_path:
        dirname = rel_path.split('/')[0]
        if dirname == 'adventure':
            return 'adventure'
        elif dirname == 'bestiary':
            return 'creature'
        elif dirname == 'book':
            return 'book'
        elif dirname == 'spells':
            return 'spell'
        else:
            return ''
    else:
        rel_name = rel_path.replace('.json', '').replace(
            'fluff-', '').replace('foundry-', '')
        if rel_name == 'actions':
            return 'action'
        elif rel_name == 'adventures':
            return 'adventure'
        elif rel_name == 'backgrounds':
            return 'background'
        elif rel_name == 'bastions':
            return ''
        elif rel_name == 'books':
            return 'book'
        elif rel_name == 'charcreationoptions':
            return 'charoption'
        elif rel_name == 'conditionsdiseases':
            return ''  # TODO：condition或者disease都有可能，暂不处理
        elif rel_name == 'cultsboons':
            return 'cult'
        elif rel_name == 'decks':
            return 'deck'
        elif rel_name == 'deities':
            return 'deity'
        elif rel_name == 'enconters':
            return 'enconters'
        elif rel_name == 'feats':
            return 'feat'
        elif rel_name == 'languages':
            return 'language'
        elif rel_name == 'objects':
            return 'object'
        elif rel_name == 'races':
            return 'race'
        elif rel_name == 'recipes':
            return 'recipe'
        elif rel_name == 'rewards':
            return 'reward'
        elif rel_name == 'senses':
            return 'sense'
        elif rel_name == 'skills':
            return 'skill'
        elif rel_name == 'trapshazards':
            return ''  # TODO: trap或者shazards都有可能，暂不处理
        elif rel_name == 'vehicles':
            return 'vehicle'
        elif rel_name == 'items':
            return 'item'
        elif rel_name == 'items-base':
            return 'item'
        elif rel_name == 'items-base':
            return 'item'
        elif rel_name == 'magicvariants':
            return 'item'
        elif rel_name == 'optionalfeatures':
            return 'optfeature'
        elif rel_name == 'psionics':
            return 'psionic'
        elif rel_name == 'tables':
            return 'table'
        elif rel_name == 'variantrules':
            return 'variantrule'
        
    return ''