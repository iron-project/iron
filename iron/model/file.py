#!/usr/bin/env python3

import os
from sqlalchemy.ext.mutable import MutableList
from iron.model import db


class File(db.Model):
    path = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    chunks = db.Column(MutableList.as_mutable(db.PickleType))


class FileOperator:
    @staticmethod
    def create(path: str) -> File:
        return File(path=path, name=os.path.split(path)[1], chunks=[])

    @staticmethod
    def pardir(f: File) -> str:
        return os.path.split(f.path)[0]

    @staticmethod
    def get(path: str) -> File:
        return File.query.get(path)

    @staticmethod
    def marshal(f: File) -> str:
        return {'path': f.path, 'name': f.name, 'chunks': f.chunks}
