#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from .base import CRUDMixin, db
import datetime


class SourceModel(db.Model, CRUDMixin):
    __tablename__ = 'source'

    word_id = Column(Integer, ForeignKey('words.id'), primary_key=True,)
    file = Column(String, primary_key=True,)
    version = Column(String(length=10))
    words = relationship('WordsModel', backref='words')

    def __init__(self, word_id, file, version):
        super().__init__()
        self.word_id = word_id
        self.file = file
        self.version = version
        
    def to_dict(self, *keys):
        data = {
            "word_id": self.word_id,
            "file": self.file,
            "version": self.version,
            "words": self.words.to_dict()
        }
        # if words :
            # data['words'] = self.words
        for key in keys:
            if isinstance(key, str):
                data[key] = getattr(self, key)
        return data

    def __repr__(self):
        return f"<Source {self.en}>"
