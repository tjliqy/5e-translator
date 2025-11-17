# api_foo.py
from flask_restful import Resource, Api, request
from .restful_utils import *
from app.model import WordsModel, SourceModel, ProofreadModel, session
from .base import BaseApi
import json
from sqlalchemy import text

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

api = Api()

# @api.resource('/words','/words/<int:id>')
@api.resource('/words')
class WordsApi(Resource, BaseApi):
    model = WordsModel
    
    def _get(self, query):
        # 根据文件名进行子查询
        # query = query.filter(getattr(self.model, 'category').is_(None))
        # query = query.filter()
        source_file = request.args.get('source_file')
        has_proofread = request.args.get('has_proofread', None, int)
        if has_proofread:
            has_proofread_subquery = ProofreadModel.query \
                .with_entities(ProofreadModel.word_id) \
                .distinct()
            if has_proofread == 1:
                query = query.filter(WordsModel.id.in_(has_proofread_subquery))
            else:
                query = query.filter(~WordsModel.id.in_(has_proofread_subquery))
        if source_file:
            source_subquery = SourceModel.query \
                .with_entities(SourceModel.word_id) \
                .filter(SourceModel.file == source_file) \
                .subquery()
            query = query.filter(WordsModel.id.in_(source_subquery))
        return query
    
    def _create(self, words):
        if words is None:
            raise Exception("words is none")

    
    def _delete(self, words):
        if words is None:
            raise Exception("words is none")

    
    def _update(self,words):
        if words is None:
            raise Exception("words is none")

# @api.resource('/relations')
# class RelationApi(Resource, BaseApi):
#     model = WordsApi
#     @login_required
#     def get(self):
#         if not current_user.is_authenticated:
#             return error("请先登录！")
#         pageNum = request.args.get('page', None, int)
#         pageSize = request.args.get('limit', 10, int)
#         en = request.args.get('en', None, str)
#         pageItems = self.model.query.filter(getattr(self.model, 'en').contains(en)).paginate( page=pageNum, per_page=pageSize, error_out=False)
#         return success(data={"count": pageItems.total, "items": self.model.list_to_dict(pageItems.items)})

@api.resource('/replace-key')
class ReplaceKeyApi(Resource):
    
    @login_required
    def post(self):
        if current_user.roles != 'admin':
            return error(current_user.roles + "无法使用此接口")
        data = request.get_json()
        if data["wrongCn"] is None or data["rightCn"] is None or data["en"] is None:
            return error("参数不正确")
        # WordsModel.query.filter(WordsModel.en.in_(data['in_en'])).filter(WordsModel.cn.in_(data['nin_cn'])).update()
        try:
            stmt = text("update words set cn = replace(cn,:wrongCn, :rightCn ) where cn like :wrongLikeCn and cn not like :rightLikeCn and source = 'GPT' and en like :en and proofread =0;")
            # stmt = text("select * from words where cn like :wrongLikeCn and source = 'GPT' and en like :en and proofread =0;")
            result = session.execute(stmt, {
                "wrongCn": data['wrongCn'],
                "rightCn": data['rightCn'],
                "wrongLikeCn": f"%{data['wrongCn']}%",
                "rightLikeCn": f"%{data['rightCn']}%",
                "en": f"%{data['en']}%",
            })
            session.commit()
        except:
            session.rollback()
            return error("更新失败")
        return success(data={'count':result.rowcount})
        