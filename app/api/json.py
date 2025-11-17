# api_foo.py
import json
import os
from flask_restful import Resource, Api, request
from .restful_utils import *
from app.model import WordsModel
from config import OUT_PATH
from .base import BaseApi
api = Api()

def find_json_files(root_folder:str):
    json_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.relpath(os.path.join(root, file),root_folder))
                # json_files.append(file)
    return json_files

@api.resource('/json')
class JsonApi(Resource):
    def get(self):
        file_name = request.args.get('file', None, str)
        source = request.args.get('source', None, str)
        
        if file_name:
            file_path = os.path.join(FILE_PATH, file_name)
            if not os.path.exists(file_path):
                return error(f"{file_name}不存在")
            with open(file_path, 'r') as file:
                content = file.read()
                json_content = json.loads(content)
                if source and isinstance(json_content,dict):
                    json_content = self.__check_source(json_content, source)
                return success(data={'file':json_content})
        else:
            if not os.path.exists(FILE_PATH):
                return error("数据目录不存在，请通知管理员检查")
            files = find_json_files(FILE_PATH)
            return success(data=files)
    def __check_source(self, json_dict, source):
        return_dict = {}
        if not isinstance(json_dict, dict):
            return json_dict
        if 'source' in json_dict.keys():
            if json_dict['source'] == source:
                return json_dict
            else:
                return None
        for k,v in json_dict.items():
            if isinstance(v, dict):
                return_dict[k] = self.__check_source(v, source)
            elif isinstance(v, list):
                return_dict[k] = []
                for vv in v:
                    res_temp = self.__check_source(vv, source)
                    if res_temp:
                        return_dict[k].append(self.__check_source(vv, source))
        return return_dict