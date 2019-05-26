#!/usr/bin/env python3

import json, os
import pysnooper
from iron.model.template import SQLTemplate

class File(object):
    def __init__(self):
        self.full_path = ''
        self.base_name = ''
        self.filehash = ''
        self.chunks = []

    def pardir(self):
        return os.path.split(self.full_path)[0]

    def load(self, database_data):
        self.full_path = database_data['id']
        self.base_name = database_data['base_name']
        self.filehash = database_data['file_hash']
        self.chunks = json.loads(database_data['chunks'])


class FileMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def create(self, full_path):
        f = File()
        normpath = os.path.normpath(path)
        f.base_name = os.path.basename(normpath)
        f.full_path = normpath

    def exist(self, f):
        record = self.connect.query(
            self.template.GETFILE, id=f.full_path).as_dict()
        return len(record) > 0

    # @pysnooper.snoop()
    def fetch(self, full_path):
        record = self.connect.query(
            self.template.GETFILE, id=full_path).as_dict()
        if len(record) > 0:
            f = File()
            f.load(record[0])
            return f
        return None

    def add(self, f):
        self.connect.query(
            self.template.PUTFILE, id=f.full_path,
            base_name=f.base_name, file_hash=f.filehash,
            chunks=json.dumps(f.chunks))

    def delete(self, f):
        self.connect.query(
            self.template.RMFILE, id=f.full_path)
