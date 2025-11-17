#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.mysql import TINYINT

from .base import CRUDMixin, db
import datetime


class WordsModel(db.Model, CRUDMixin):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, autoincrement=True)
    en = Column(String)
    cn = Column(String)
    json_file = Column(String)
    source = Column(String(length=255))
    version = Column(String(length=10))
    is_key = Column(TINYINT)
    proofread = Column(TINYINT)
    category = Column(String)
    created_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP()")
    modified_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP()", onupdate=datetime.datetime.now)
    modified_by = Column(Integer)
    
    equal_filters = []
    contain_filters = ['en', 'cn']

    def __init__(self, en, cn, json_file, modified_by, source = "", version = 0):
        self.en = en
        self.cn = cn
        self.json_file = json_file
        self.modified_by = modified_by
        self.source = source
        self.version = version
    def to_dict(self, *keys):
        data = {
            "id": self.id,
            "en": self.en,
            "cn": self.cn,
            "json_file": self.json_file,
            "source": self.source,
            "version": self.version,
            "is_key": self.is_key,
            "proofread":self.proofread,
            "created_at": str(self.created_at),
            "modified_at": str(self.modified_at),
        }

        for key in keys:
            if isinstance(key, str):
                data[key] = getattr(self, key)
        return data

    def __repr__(self):
        return f"<Word {self.en}>"
