#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate(db = db)

session = db.session

class CRUDMixin(object):
    def __init__(self) -> None:
        self.session = session
        
    @classmethod
    def create(cls, commit=True,createFunc=None, **kwargs):
        # try:
        instance = cls(**kwargs)
        return instance.save(commit=commit, saveFunc=createFunc)
    
    def update(self, commit=True,updateFunc=None, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        try: 
            if commit:
                session.commit()
                if callable(updateFunc):
                    updateFunc(self)
            return self
        except:
            session.rollback()
            return None
    
    def delete(self, commit=True, deleteFunc=None):
        try:
            session.delete(self)
            if callable(deleteFunc):
                deleteFunc(self)
            if commit:
                session.commit()
            return True
        except:
            session.rollback()
            return False
    def page(self, commit=True):
        instance = self.query.paginate(page=1, per_page=10, error_out=False)
    def save(self, commit=True, saveFunc=None):
        try: 
            session.add(self)
            if commit:
                session.commit()
                if callable(saveFunc):
                    saveFunc(self)
            return self
        except:
            session.rollback()
            return None
    
    @staticmethod
    def list_to_dict(items,*keys):
        return [item.to_dict(keys) for item in items]
    
    def to_dict(self,*keys):
        data = {}
        for key in keys:
            data[key] = getattr(self, key)
        return data
    