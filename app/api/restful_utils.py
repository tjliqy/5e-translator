#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import jsonify

class HttpCode(object):
    ok = 20000
    un_auth_error = 401
    params_error = 400
    server_error = 500

def restful_result(code, message, data):
    return jsonify({"code": code, "message": message, "data": data or {}})

def success(message="", data=None):
    """
    正确返回
    :return:
    """
    return restful_result(code=HttpCode.ok, message=message, data=data)
def error(message=""):
    return restful_result(code=HttpCode.server_error, message=message, data=None)