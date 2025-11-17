#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.mysql import TINYINT

from .base import CRUDMixin, db
import datetime


class ProofreadModel(db.Model, CRUDMixin):
    __tablename__ = 'proofread'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer)
    cn = Column(String)
    accepted = Column(TINYINT)

    modified_at = Column(
        TIMESTAMP, server_default="CURRENT_TIMESTAMP()", onupdate=datetime.datetime.now)
    modified_by = Column(Integer)

    def __init__(self,  word_id, cn,  modified_by, accepted):
        self.word_id = word_id
        self.cn = cn
        self.modified_by = modified_by
        self.accepted = accepted
    def to_dict(self, *keys):
        data = {
            "id": self.id,
            "word_id": self.word_id,
            "cn": self.cn,
            "accepted": self.accepted,
            "modified_at": str(self.modified_at),
            "modified_by": self.modified_by
        }

        for key in keys:
            if isinstance(key, str):
                data[key] = getattr(self, key)
        return data

    def __repr__(self):
        return f"<Proofread {self.word_id}>"
