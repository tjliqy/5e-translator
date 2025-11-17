#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flasgger import Swagger

SWAGGER_TITLE = "【KIWI-ADMIN】Kiwi后台管理工具api文档"
SWAGGER_DESC = "API接口"
# 地址，必须带上端口号
SWAGGER_HOST = "127.0.0.1:8081"

WEB_RESULT_URL="http://10.58.102.86/server/" # 结果目录api


# API可视化管理
swagger_config = Swagger.DEFAULT_CONFIG

# 标题
swagger_config['title'] = SWAGGER_TITLE   
# 描述信息
swagger_config['description'] = SWAGGER_DESC
# Host    
swagger_config['host'] = SWAGGER_HOST

swagger = Swagger(config=swagger_config)