import uuid
from config import logger,KEY_MATCHED_TAG
from typing import List
from app.core.utils import Job, check_skip_key, parse_custom_format, only_has_format, split_string, need_translate_str, check_prefix, check_suffix, get_tag_from_rel_path
from app.core.database import DBDictionary


class BaseAnalyser:
    def __init__(self, dictionary: DBDictionary, rel_path: str) -> (None):
        self.name_list: List[str] = []
        self.job_list: List[Job] = []
        self.dictionary = dictionary
        self.rel_path = rel_path
        self.name_tag = get_tag_from_rel_path(self.rel_path)

    def process(self,  en_dict: dict, byhand: bool = False):
        self.byhand = byhand
        res_dict, ok = self.process_dict(en_dict, "")
        if not ok:
            raise RuntimeError(f'process error:{en_dict}')
        return res_dict, self.job_list

    def str_2_job(self, en_str: str, current_names: list = [], tag = ""):
        """根据字符串生成JOB对象

        Args:
            en_str (str): 原始英文字符串
            current_name (str, optional): 所属元素的名字. Defaults to None.

        Returns:
            job_str: 整理后的有job替换id的字符串
        """
        # "需要考虑句中有{@tag 标识|对的|1}"的情况。job添加["需要考虑句中有{@tag 标识|对的|1}","标识","对的",]
        match_k, match_v, is_valid = parse_custom_format(en_str)
        if len(match_v) == 0:
            # 没找到tag则直接整句按|拆分即可
            return self.__split_and_append_job(en_str, current_names=current_names)
        else:
            uid = uuid.uuid1()
            cn_str = None
            if only_has_format(en_str):
                cn_str = en_str
            j = self.get_job(en_str, tag=tag)
            if j is not None:
                uid = j.uid
            else:
                # 将本身添加到Job列表
                self.set_job(uid, en_str, cn_str, current_names=current_names, tag=tag)
            en_str = f'[!@ {uid}]'

            # 处理tag的value内容
            for m, t in zip(match_v, match_k):
                self.__split_and_append_job(m, t, current_names=current_names)
            return en_str

    def set_job(self, uid: str, en: str, cn: (str | None) = None, tag=None, current_names: list = []):
        """向Job列表中添加Job

        Args:
            uid (str): Job的UUID
            en (str): 英文文本
            cn (str, optional): 中文文本. Defaults to None.
            tag (str, optional): 标签. Defaults to "".
            current_names (list, optional): 当前元素的名称列表. Defaults to [].
        """
        is_proofread = False
        sql_id = None
        modified_at = 0
        if cn is None:
            # 如果只有{@tag xxx}的文本，则无需翻译，直接原样放置即可
            if only_has_format(en):
                cn = en
            else:
                # 先从内存中读取
                cn_bean = self.dictionary.get(
                    en, load_from_sql=False, ignore_case=True, tag=tag)
                if cn_bean == None:
                    # 从数据库中读取
                    cn_bean = self.dictionary.get(
                        en, rel_f=self.rel_path, load_from_sql=True, ignore_case=True, tag=tag)
                if cn_bean != None:
                    cn = cn_bean['cn']
                    is_proofread = cn_bean['proofread']
                    sql_id = cn_bean['sql_id']
                    modified_at = cn_bean['modified_at']
        
        # 手动翻译关键字（name）
        if self.byhand and is_proofread != 1 and ((current_names != [] and en == current_names[-1]) or  len(en.split(' ')) < 5) and need_translate_str(en):
        # if self.byhand and is_proofread != 1 and len(en.split(' ')) < 4:
            print(f'手动翻译：{en} -> {cn}')
            self.dictionary.update_by_hand(en, cn)
            
        # 将当前元素的名称列表转换为(name,cn_str)的元组列表
        names_in_job = []
        for name in current_names:
            name_job = self.get_job(name,tag=self.name_tag)
            if name_job is None:
                continue
            if name_job.is_proofread:
                names_in_job.append((name,name_job.cn_str))
            else:
                names_in_job.append((name, ""))
        self.job_list.append(Job(uid, en, cn, self.rel_path, tag, [
        ], names_in_job, is_proofread, sql_id, modified_at=modified_at))

    def process_dict(self, en_dict: dict, key_path: str, current_names: list = [], skip_keys: list = []):
        """检查dict类型，输出处理完的dict

        Args:
            en_dict (dict): 英文dict
            key_path (str): key路径
            current_name (str, optional): 所属元素的名称. Defaults to None.

        Returns:
            res_dict(dict): 中文dict
            is_ok(bool): 是否解析成功
        """
        res_dict = {}  # 结果dict
        __current_names = current_names.copy()  # 当前元素的名称列表，深拷贝，防止污染上一级的
        skip_name = False
        # 先找到name字段，放入当前元素的名称列表，同时增加ENG_name字段记录原始英文名
        if "name" in en_dict.keys() and isinstance(en_dict['name'], str):
            __current_names.append(en_dict["name"])
            self.name_list.append(en_dict["name"])
            res_dict['ENG_name'] = en_dict["name"]
            name_job = self.get_job(en_dict["name"],tag=self.name_tag)
            if name_job is None:
                cn_bean = self.dictionary.get(
                    en_dict["name"], load_from_sql=False, ignore_case=True, tag=self.name_tag)
                if cn_bean != None:
                    res_dict['name'] = cn_bean['cn']
                    # print(self.name_tag)
                            # 将当前元素的名称列表转换为(name,cn_str)的元组列表
                    names_in_job = []
                    for name in current_names:
                        name_job = self.get_job(name,tag=self.name_tag)
                        if name_job is None:
                            continue
                        if name_job.is_proofread:
                            names_in_job.append((name,name_job.cn_str))
                        else:
                            names_in_job.append((name, ""))
                    names_in_job.append((en_dict["name"], cn_bean['cn'] if cn_bean['proofread'] else ""))
                    self.job_list.append(Job(uuid.uuid1(), en_dict["name"], cn_bean['cn'], self.rel_path, self.name_tag, [
                    ], names_in_job, cn_bean['proofread'], cn_bean['sql_id'], modified_at=cn_bean['modified_at']))
                    skip_name = True
            else:
                res_dict['name'] = name_job.cn_str
                skip_name = True
                # print(res_dict['name'])
        # 递归处理dict的所有字段
        for k, v in en_dict.items():
            # 检查是否需要跳过
            if skip_name and k == 'name':
                continue
            if check_skip_key(k, v, key_path) or k in skip_keys:
                res_dict[k] = v
            else:
                tag = ""
                if k in KEY_MATCHED_TAG.keys():
                    tag = KEY_MATCHED_TAG[k]
                tmp_dict, ok = self.process_base_item(
                    v, key_path+'/'+k, __current_names, tag=tag)
                if not ok:
                    raise RuntimeError(f'process error:{k}')
                res_dict[k] = tmp_dict

        return res_dict, True

    def process_base_item(self, en_item, key_path: str, current_names: list = [], tag=""):
        """转换json_item的入口函数，主要用于根据不同的类型调用不同的处理函数

        Args:
            en_item (obj): 英文的json_item
            key_path (str): 路径
            current_name (str, optional): 所属元素的名称. Defaults to None.

        Returns:
            res_item: 转换后的item
            is_ok(bool): 是否成功
        """
        if en_item is None:
            # logger.info(f"{self.rel_path}中存在空变量！请注意！")
            return en_item, True
        elif isinstance(en_item, int) or isinstance(en_item, float) or isinstance(en_item, bool):
            # 整型、浮点型、布尔型不翻译
            return en_item, True
        elif isinstance(en_item, str):
            tmp_str = self.str_2_job(en_item, current_names, tag)
            return tmp_str, True
        elif isinstance(en_item, dict):
            return self.process_dict(en_item, key_path, current_names)
        elif isinstance(en_item, list):
            return self.__process_list(en_item, key_path, current_names)
        return None, False

    def __process_list(self, en_list, key_path, current_names: list = []):
        res_list = []
        for v in en_list:
            tmp_list, ok = self.process_base_item(v, key_path, current_names)
            if not ok:
                logger.error(f"{self.rel_path}解析{v}时出错")
            res_list.append(tmp_list)

        return res_list, True

    def __split_and_append_job(self, s, tag=None, current_names: list = []):
        """
        对输入的字符串进行分割检查和处理，生成带有Job UUID替换标识的字符串。

        Args:
            s (str): 待处理的字符串
            tag (str, optional): 标签，默认为空字符串
            current_name (str, optional): 所属元素的名称，默认为 None

        Returns:
            str: 处理后的字符串，包含Job UUID替换标识
        """
        res_str = s
        sub_str_list = split_string(res_str)
        str_list = [res_str] if len(sub_str_list) == 1 else sub_str_list

        def _process_value(v, tag=None):
            if need_translate_str(v):
                uid = uuid.uuid1()
                # 去除前缀后缀
                sk_without_prefix, prefix = check_prefix(v)
                sk_pure, suffix = check_suffix(sk_without_prefix)
                # 生成Job 如果已经有相同的Job，则更新uuid
                j = self.get_job(sk_pure, tag=tag)
                if j is not None:
                    uid = j.uid
                else:
                    # 如果是新的Job，则添加到Job列表
                    self.set_job(uid, sk_pure, None, tag=tag,
                                   current_names=current_names)

                return f'{prefix}[!@ {uid}]{suffix}'
            else:
                return v
        # if len(sub_ks) > 1:
        if tag == "filter":
            if (len(str_list) > 2):
                # 正常至少有3个值
                cv_page = str_list[1]
                cv_name = _process_value(str_list[0], tag=cv_page)
                if cv_page == "bestiary":
                    cv_conditions = []
                    for eev in str_list[2:]:
                        if eev.startswith('type='):
                            # 锁定type
                            cv_conditions.append(eev)
                        elif eev.startswith('tag='):
                            # 锁定tag
                            cv_conditions.append(eev)
                        else:
                            ccv = _process_value(eev)
                            cv_conditions.append(ccv)
                    res_str = f"{cv_name}|{cv_page}|{'|'.join(cv_conditions)}"
                    return res_str
                elif cv_page in ["items", "spells", "optionalfeatures", "races"]:
                    cv_conditions = []
                    for eev in str_list[2:]:
                        ccv = _process_value(eev)
                        cv_conditions.append(ccv)
                    res_str = f"{cv_name}|{cv_page}|{'|'.join(cv_conditions)}"
                    return res_str
                
        replaced_keys = []  # 替换为Job UUID后的文本
        for sk in str_list:
            replaced_keys.append(_process_value(sk, tag=tag))
        res_str = '|'.join(replaced_keys)
        return res_str

    def get_job(self, en, tag=""):
        # first_match = None
        for j in self.job_list:
            if j.en_str == en:
                if j.tag == tag:
                    # 优先匹配tag和en都相同的
                    return j
        if self.dictionary.get(en, load_from_sql=False, tag=tag) is not None:
            # 这里说明source表匹配到了en和tag完全相同的，但是还没有在job_list中，所以暂时返回None，让后续逻辑建一个新的
            return None
        else:
            # 这里说明表里没有en和tag完全相同的，则可以尝试匹配只有en相同，但tag为None的
            for j in self.job_list:
                if j.en_str == en and j.tag is None:
                    return j

