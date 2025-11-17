# api_foo.py
from flask import request
from .restful_utils import *
from typing import Union
from app.model import db, CRUDMixin

import json


class BaseApi():
    model: Union[CRUDMixin, db.Model] = None

    def get(self):
        pageNum = request.args.get('page', None, int)
        pageSize = request.args.get('limit', 10, int)
        id = request.args.get('id', None, int)
        query = self.model.query

        # 查询指定id的
        if id:
            s = query.get(id)
            return self._get_id(s)
        else:
            sort_by = request.args.get('sort')
            equal_filters = dict()
            contain_filters = dict()
            not_equal_filters = dict()
            not_contain_filters = dict()
            for attr, v in request.args.items():
                if attr.startswith('eq_'):
                    equal_filters[attr[3:]] = v
                elif attr.startswith('in_'):
                    contain_filters[attr[3:]] = v
                elif attr.startswith('neq_'):
                    not_equal_filters[attr[4:]] = v
                elif attr.startswith('nin_'):
                    not_contain_filters[attr[4:]] = v
            # for attr in self.model.equal_filters:
            #     equal_filters[attr] = request.args.get(attr, None)
            # for attr in self.model.contain_filters:
            #     contain_filters[attr] = request.args.get(attr, None)
            for f in equal_filters:
                if equal_filters[f]:
                    query = query.filter(getattr(self.model, f) == equal_filters[f])
            for f in contain_filters:
                if contain_filters[f]:
                    query = query.filter(getattr(self.model, f).contains(contain_filters[f]))
            for f,v in not_equal_filters.items():
                if v:
                    query = query.filter(getattr(self.model, f) != v)
            for f,v in not_contain_filters.items():
                if v:
                    query = query.filter(getattr(self.model, f).notlike(f'%{v}%'))
            if sort_by:
                if sort_by[0] == '+':
                    query = query.order_by(getattr(self.model, sort_by[1:]).asc())
                elif sort_by[0] == '-':
                    query = query.order_by(getattr(self.model, sort_by[1:]).desc())
            query = self._get(query)
            # 查询分页
            if pageNum:
                
                pageItems = query.paginate(
                    page=pageNum, per_page=pageSize, error_out=False)
                return success(data={"count": pageItems.total, "items": self.model.list_to_dict(pageItems.items)})
            # 查询列表
            else:
                items = query.all()
                results = self.model.list_to_dict(items)
        return success(data={"count": len(results), "items": results})
    
    def _get(self, query):
        return query
    
    def _get_id(self, item):
        result = item.to_dict()
        return success(data=result)

    def delete(self):
        return error("无法删除")
        id = request.args.get('id', None, int)
        if not id:
            return error("删除失败：id不能为空")
        s = self.model.query.get(id)
        if s is None:
            return error(f"删除失败：没有id={id}的条目")    
        if not s.delete(commit=True, deleteFunc=self._delete):
            return error(f"删除失败：数据库删除失败")
        return success("删除成功", data=s.to_dict())
    
    def _delete(self, item):
        print(item)
    
    def post(self):
        if request.is_json:
            data = request.get_json()
            item = self.model.create(commit=True, **data, createFunc=self._create)
            if item is None:
                return error("新增失败：数据库新增失败")
           
            return success(message=f"Item has been created successfully.", data = item.to_dict())
        else:
            return error("The request payload is not in JSON format")
    def _create(self, item):
        pass

    def put(self):
        # id = request.args.get('id', None, int)
        params = request.get_json()
        if params['id'] is None:
            return error("更新失败：id不能为空")
        item = self.model.query.get(params['id'])
        if item is None:
            return error(f"更新失败：没有id={params['id']}的条目")
        if item.update(commit=True,  updateFunc=self._update,**params) is None:
            return error(f"更新失败：数据库更新失败")
        return success(message=f"Item has been updated successfully.", data = item.to_dict())
    def _update(self, item):
        pass