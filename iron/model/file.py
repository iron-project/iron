#!/usr/bin/env python3

import json, os
import pysnooper
from iron.model.template import SQLTemplate

class File(object):
    def __init__(self):
        self.path = ''
        self.file_name = ''
        self.file_hash = ''
        self.chunks = {}

    def pardir(self):
        return os.path.split(self.path)[0]

    def load(self, database_data):
        self.path = database_data['id']
        self.file_name = database_data['file_name']
        self.file_hash = database_data['file_hash']
        self.chunks = json.loads(database_data['chunks'])


class FileMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def create(self, path):
        normpath = os.path.normpath(path)
        f = File()
        f.file_name = os.path.basename(normpath)
        f.path = normpath
        return f

    def exist(self, f):
        record = self.connect.query(
            self.template.GETFILE, id=f.path).as_dict()
        return len(record) > 0

    # @pysnooper.snoop()
    def fetch(self, path):
        normpath = os.path.normpath(path)
        record = self.connect.query(
            self.template.GETFILE, id=normpath).as_dict()
        if len(record) > 0:
            f = File()
            f.load(record[0])
            return f
        return None

    def add(self, f):
        self.connect.query(
            self.template.PUTFILE, id=f.path,
            file_name=f.file_name, file_hash=f.file_hash,
            chunks=json.dumps(f.chunks))

    def delete(self, f):
        self.connect.query(
            self.template.RMFILE, id=f.path)
