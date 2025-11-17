# api_foo.py
from flask_restful import Resource, Api, request
from .restful_utils import *
from app.model import SourceModel, session
from .base import BaseApi
import json
from flask_login import login_required
from sqlalchemy import text

api = Api()

@api.resource('/source')
class SourceApi(Resource, BaseApi):
    model = SourceModel
    
    @login_required
    def get(self):
        return super().get()
     
    @login_required
    def put(self):
        params = request.get_json()
        print(params)
        if params['file'] is None or params['word_id'] is None or params['new_word_id'] is None:
            return error("更新失败：file、word_id、new_word_id不能为空")
        try:
            procedure = text("CALL replacesource(:old_file, :old_word_id, :new_word_id)")
            result = session.execute(procedure, {
                'old_file': params['file'],
                'old_word_id': params['word_id'],
                'new_word_id': params['new_word_id']
            })
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"存储过程执行失败: {e}")
            return error("替换失败")
        # item = self.model.query.filter(getattr(self.model, 'file') == params['file'])\
        #     .filter(getattr(self.model, 'word_id') == params['word_id']).first()
        # if item is None:
        #     return error(f"更新失败：没有找到相关条目")
        # new_item = self.model.create(commit=True, createFunc=None, word_id = params['new_word_id'], file = item.file, version = item.version)
        # if new_item is None:
        #     return error("更新失败：无法增加新条目")
        # if item.delete():
        #     new_item.delete()
        #     return error(f"更新失败：数据库更新失败")
        # return success(message=f"Item has been updated successfully.", data = item.to_dict())
        
    @login_required
    def post(self):
        return super().post()
        
    def _create(self, words):
        if words is None:
            raise Exception("words is none")

    
    def _delete(self, words):
        if words is None:
            raise Exception("words is none")

    
    def _update(self,words):
        if words is None:
            raise Exception("words is none")
