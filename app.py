#!/usr/bin/python3
# -*- coding: UTF-8 -*-

    
from flask import Flask
from flask_cors import CORS
from app.api import login_manager, api_bp as api_blueprint
from app.model import db, migrate

from config import DB_CONFIG, swagger

if __name__ == '__main__':
    # download_requirements()
    
    import pymysql
    pymysql.install_as_MySQLdb()
    app = Flask(__name__)
    # app.config.from_object(config[config_name])
    # config[config_name].init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['DATABASE']}"
    app.config['JSON_AS_ASCII'] = False 
    app.config['SECRET_KEY'] = 'your-secret-key'

    CORS(app)
    db.init_app(app)
    swagger.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.run(host='0.0.0.0', port=80, debug=True)
