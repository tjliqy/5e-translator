import base64
import json

PTTSW_ID_PREIX = "@Key@"
class DocumentBean:
    
    def __init__(self, data: dict, type: str = "", source: str = "", _meta: dict = {}):
        """每个最小的文件单元

        Args:
            value (dict): 拆分后的json内容
        """
        
        self._meta = _meta.copy()
        # 设置id
        if "id" in data:
            self.id = data["id"]
        elif "name" in data:
            self.id = data["name"].replace(" ", "-").replace("/", "").lower()
        else:
            # 基于data内容生成base64编码作为id
            # 将dict转换为bytes
            json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
            # 计算base64编码
            base64_bytes = base64.b64encode(json_bytes)
            # 转换为字符串并移除末尾的等号
            base64_str = base64_bytes.decode('utf-8').rstrip('=')
            # 替换URL不安全字符
            self.id = base64_str.replace('+', '-').replace('/', '_')[:10]
            
        # 设置type
        if type:
            self.type = type
        else:
            raise ValueError(f"DocumentBean {self.id} 的类型(type)不能为空")

        # 设置source
        if source:
            self.source = source.lower()
        elif "source" in data:
            self.source = data["source"].lower()
        else:
            raise ValueError(f"DocumentBean {self.id} 的来源(source)不能为空")
        
        # 设置path
        
        self._meta["pttsw_id"] = f"{self.source}/{self.type}/{self.id}"
        self.path = self._meta["pttsw_id"] + ".json"
        self.data = data
    def __dict__(self):
        return {
            "_meta": self._meta,
            self.type: self.data
        }
        
class CombineInfo:
    def __init__(self, data: dict):
        self.data = data