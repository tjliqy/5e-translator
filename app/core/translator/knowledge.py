import os
import re
import json
# import Levenshtein
from app.core.utils import get_pure_text
from app.core.database import DBDictionary
KNOWLEDGE_DIVIDER = "!@!"
class Knowledge:
    def __init__(self, path: str, dictionary=None):
        """
        初始化 Knowledge 类，读取指定路径的 JSON 文件并存储为 self.source

        Args:
            path (str): JSON 文件的路径
        """
        self.source = {}
        self.index = {}
        self.dictionary = dictionary
        try:
            # 检查文件是否存在
            if os.path.exists(path):
                # 打开文件并读取内容
                with open(path, 'r', encoding='utf-8') as f:
                    # 解析 JSON 内容
                    self.source = json.load(f)
                    self.index = self.__build_index()
            else:
                print(f"文件 {path} 不存在。")
        except json.JSONDecodeError:
            print(f"无法解析 {path} 为有效的 JSON 文件。")
        except Exception as e:
            print(f"读取文件 {path} 时发生错误: {e}")
    
    def __build_index(self):
        index = {}

        def build_index_recursive(data, path=""):
            if isinstance(data, dict):
                eng_name = data.get('eng_name')
                if eng_name:
                    eng_name = eng_name.lower()
                    if eng_name not in index.keys():
                        index[eng_name] = set()
                    index[eng_name].add(path)
                for key, value in data.items():
                    new_path = f"{path}{KNOWLEDGE_DIVIDER}{key}" if path else key
                    build_index_recursive(value, new_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    new_path = f"{path}{KNOWLEDGE_DIVIDER}{i}" if path else str(i)
                    build_index_recursive(item, new_path)

        build_index_recursive(self.source)
        return index

    def __calculate_similarity(self, str1, str2):
        """
        计算两个字符串的相似度

        Args:
            str1 (str): 第一个字符串
            str2 (str): 第二个字符串

        Returns:
            float: 相似度，范围从 0 到 1
        """
        # 计算编辑距离
        # distance = Levenshtein.distance(str1, str2)
        distance = 1
        # 计算相似度
        similarity = 1 - (distance / max(len(str1), len(str2)))
        return similarity
    def __get_source(self, key, prefix_paths=[]):
        results = []  # 用于存储所有匹配路径的值
        if key in self.index:
            for path in self.index[key]:
                if len(prefix_paths)>0:
                    is_right_path = False
                    # 检查 path 是否以 prefix_paths 中的任何一个路径开头
                    # 如果不是，则跳过当前路径
                    # 如果是，则将对应的值添加到结果列表中
                    for pp in prefix_paths:
                        if path.startswith(pp):
                            is_right_path = True
                            break
                    if not is_right_path:
                        continue
                tmp_keys = path.split(KNOWLEDGE_DIVIDER)
                # 根据 tmp_keys 获取 source 中对应的值
                current = self.source
                for tmp_key in tmp_keys:
                    if tmp_key.isdigit():
                        tmp_key = int(tmp_key)
                    try:
                        current = current[tmp_key]
                    except (KeyError, IndexError):
                        # 如果路径无效，跳过当前路径
                        break
                else:
                    # 如果路径有效，将对应的值添加到结果列表中
                    results.append((current,path))
        return results
    
    def __get_similarity_source(self, key, prefix_paths=[]):
        max_similarity = 0
        max_similarity_key = None
        for tmp_key in self.index.keys():
            similarity = self.__calculate_similarity(key, tmp_key)
            if similarity > max_similarity:
                if len(prefix_paths)>0:
                    is_right_path = False
                    for path in self.index[tmp_key]:
                        # 检查 path 是否以 prefix_paths 中的任何一个路径开头
                    # 如果不是，则跳过当前路径
                    # 如果是，则将对应的值添加到结果列表中
                        for pp in prefix_paths:
                            if path.startswith(pp):
                                is_right_path = True
                                break
                    if not is_right_path:
                        continue
                max_similarity = similarity
                max_similarity_key = tmp_key
        if max_similarity_key and max_similarity >= 0.6:
            # print(max_similarity)
            return self.__get_source(max_similarity_key)
    
    def get_translate_name_source(self, key, sources, trans = None):
        similarity = 0
        if trans == None:
            trans,_ = self.dictionary.get(key)
        if not trans:
            return None
        source, similarity = self.__get_translate_name_source_similarity(key, sources, trans)
        if similarity > 0.6:
            return source
        else:
            # pattern = r'[\(\[{\{（].*?[）\)\]\}]'
            pure_trans  = get_pure_text(trans)
            if pure_trans == trans:
                return None
            source, similarity = self.__get_translate_name_source_similarity(key, sources, pure_trans, need_pure = True)
            if similarity > 0.6:
                return source
        return None
    
    
    def __get_translate_name_source_similarity(self, key, sources, trans = None, need_pure = False):
        result_source = None
        similarity = 0
        if trans == None:
            trans,_ = self.dictionary.get(key)
        if not trans:
            return None, 0
        for s in sources:
            if isinstance(s, dict):
                eng_name = s.get('eng_name')
                if need_pure:
                    name = get_pure_text(s.get('name'))
                else:
                    name = s.get('name')
                if (eng_name == None or eng_name == "") and name:
                    # 确认是否可能是key翻译后的文本
                    similarity = self.__calculate_similarity(trans, name)
                    result_source = s
                for v in s.values():
                    temp_source, temp_similarity = self.__get_translate_name_source_similarity(key, [v], trans=trans, need_pure = need_pure)
                    if temp_similarity > similarity:
                        similarity = temp_similarity
                        result_source = temp_source
            elif isinstance(s, list):
                for v in s:
                    temp_source, temp_similarity = self.__get_translate_name_source_similarity(key, [v], trans=trans, need_pure = need_pure)
                    if temp_similarity > similarity:
                        similarity = temp_similarity
                        result_source = temp_source
        return result_source, similarity
    def _find_sources_by_key(self, key, k, current_paths, current_sources, name):
        get_for_sure_result = False
        if key in self.index.keys():
            source_path_list = self.__get_source(key, current_paths)
            get_for_sure_result = True
        # 如果当前key不再索引中，则匹配一个字符串相似度最高的key
        elif key != k and k in self.index.keys():
            source_path_list = self.__get_source(k, current_paths)
            get_for_sure_result = True
        else:
            source_path_list = self.__get_similarity_source(key, current_paths)
            if k != key and (source_path_list is None or len(source_path_list) == 0):
                source_path_list = self.__get_similarity_source(k, current_paths)

        if source_path_list is None or len(source_path_list) == 0:
            # 判断current_sources中每个dict元素的'name'字段是否可能是key的中文翻译，如果找到匹配的则使用该元素
            sources = self.get_translate_name_source(key, current_sources)
            if sources:
                current_sources = [sources]
                # 这里path可能有问题
                # print(current_sources)
                return current_sources, current_paths, False

        if source_path_list and len(source_path_list) > 0:
            current_sources = []
            current_paths = []
            for source_path in source_path_list:
                current_sources.append(source_path[0])
                current_paths.append(source_path[1])
        else:
            return current_sources, current_paths, False

        return current_sources, current_paths, get_for_sure_result

    def get(self, name: str, key: str):
        result = []
        current_sources = []
        current_paths = []
        keys = key.lower().split(KNOWLEDGE_DIVIDER)
        temp_index_path = ""
        base_sources = []
        # 遍历 keys 逐层匹配，找到的source的层级关系需要与keys尽量一致
        for key in keys:
            pattern = r'[\(\[{\{].*?[\)\]\}]'
            k = re.sub(pattern, '', key)
            k = re.sub(r'^[0-9\W]+|[0-9\W]+$', '', k)
            current_sources, current_paths, get_for_sure_result = self._find_sources_by_key(key, k, current_paths, current_sources, name)
            if len(base_sources) == 0:
                base_sources = current_sources
            if len(keys) > 1 and key == keys[-1] and not get_for_sure_result:
                new_sources, _, _ = self._find_sources_by_key(key, k, current_paths, base_sources, name)
                if new_sources != base_sources:
                    current_sources = new_sources
            for current_source in current_sources:
                if key.lower() == current_source['eng_name'].lower():
                    result.append({key:current_sources[0]['name']})
                    
        # 如果s转为json字符串后长度大于500，则去除s中所有"eng_name"不为空的dict
        for current_source in current_sources:
            json_str = bytes(json.dumps(current_source),
                                'utf-8').decode('unicode_escape')
            if len(json_str) > 200:
                def remove_eng_name_dicts(data, is_first_level=True):
                    if isinstance(data, dict):
                        if not is_first_level and (data.get('eng_name') or data.get('name')):
                            return None
                        # 去除空的键值对
                        new_data = {k: remove_eng_name_dicts(v, is_first_level=False) for k, v in data.items() if
                                    remove_eng_name_dicts(v, is_first_level=False) is not None}
                        # 如果处理后字典为空，则返回 None
                        return new_data if new_data else None
                    elif isinstance(data, list):
                        new_data = [remove_eng_name_dicts(item, is_first_level=False) for item in data if
                                    remove_eng_name_dicts(item, is_first_level=False) is not None]
                        # 如果处理后列表为空，则返回 None
                        return new_data if new_data and len(new_data) > 0 else None
                    elif isinstance(data, str):
                        # 如果字符串为空，则返回 None
                        return data if data.strip() else None
                    return data

                result.append(remove_eng_name_dicts(current_source))
            else:
                result.append(current_source)
        return result if result else None
if __name__ == "__main__":
    dictionary = DBDictionary()
    dictionary.dump('bestiary/bestiary-erlw.json')
    k = Knowledge("/data/chm-transform/jsons.json", dictionary=dictionary)
    print(k.get("4. Blinding Ray","Belashyrra!@!Eye Ray!@!4. Blinding Ray"))