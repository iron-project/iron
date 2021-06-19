#!/usr/bin/env python3

import os
import json
from sqlalchemy.ext.mutable import MutableList
from iron.model import db


class Directory(db.Model):
    path = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    files = db.Column(MutableList.as_mutable(db.PickleType))
    dirs = db.Column(MutableList.as_mutable(db.PickleType))


class DirectoryOperator:
    @staticmethod
    def create(path: str) -> Directory:
        return Directory(path=path, name=os.path.split(path)[1], dirs=[], files=[])

    @staticmethod
    def pardir(d: Directory) -> str:
        return os.path.split(d.path)[0]

    @staticmethod
    def get(path: str) -> Directory:
        return Directory.query.get(path)

    @staticmethod
    def marshal(d: Directory) -> str:
        return {'path': d.path, 'name': d.name, 'dirs': d.dirs, 'files': d.files}
