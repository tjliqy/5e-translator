# api_foo.py
from flask_restful import Resource, Api, request
from .restful_utils import *
from app.model import UserModel
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .base import BaseApi
import json
api = Api()
login_manager = LoginManager()

class User(UserMixin, UserModel):
    # def __init__(self,user_id):
    #     self.id = user_id
        
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    def login(self):
        sql_user = self.query.filter_by(username = self.username).first()
        if not sql_user:
            return False, "该用户名未注册"
        if sql_user.password != self.password:
            return False, "密码错误"
        self.id = sql_user.id
        return True, ""
    
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
    # return User(userid)

@api.resource('/user')
class UserApi(Resource, BaseApi):
    model = User
    @login_required
    def get(self):
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            user = UserModel.query.get(user_id)
            return self._get_id(user)
        else:
            return error('当前无用户登录')
    @login_required
    def post(self):
        return error("禁止新增")
        
    @login_required
    def update(self):
        return error("禁止修改")
    
    @login_required
    def put(self):
        return error("禁止更新")
    # def delete(self, id):
    #     s = NewsModel.query.get(id)
    #     if s:
    #         if s.delete():
    #             return success()
    #         else:
    #             return error()
    #     else :
    #         return error(f"删除失败：没有id为{id}的脚本")

    # def post(self):
    #     if request.is_json:
    #         data = request.get_json()
    #         new_script = NewsModel.create(script_name=data['script_name'], setting=json.dumps(
    #             data['setting']), modified_by=data['modified_by'])
            
    #         return success(message=f"Script {new_script.script_name} has been created successfully.")
    #     else:
    #         return error("The request payload is not in JSON format")
@api.resource('/login')
class LoginApi(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        # 校验用户名密码
        user = User(data["username"],data["password"])
        ok, msg = user.login()
        if not ok:
            return error(message=msg)
        login_user(user)
        return success(message=f"Login successfully.", data = {'token':'admin_token'})

@api.resource('/logout')
class LogoutApi(Resource):
    @login_required
    def post(self):
        logout_user()
        return success(message="Logged out successfully!")
