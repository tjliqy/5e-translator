#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, String, TIMESTAMP

from .base import CRUDMixin, db
import datetime


class UserModel(db.Model, CRUDMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=255))
    password = Column(String(length=255))
    roles = Column(String(length=255))
    created_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP()")
    modified_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP()", onupdate=datetime.datetime.now)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_dict(self, *keys):
        data = {
            "id": self.id,
            "username": self.username,
            "roles":self.roles,
            "created_at": str(self.created_at),
            "modified_at": str(self.modified_at),
        }

        for key in keys:
            if isinstance(key, str):
                data[key] = getattr(self, key)
        return data

    
    def __repr__(self):
        return f"<Script {self.username}>"
