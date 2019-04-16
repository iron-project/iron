#!/usr/bin/env python3

import json
from template import SQLTemplate

class File(object):
    def __init__():
        self.full_path = ''
        self.base_name = ''
        self.filehash = ''
        self.chunks = []

    def load(self, database_data):
        self.full_path = database_data['id']
        self.base_name = database_data['base_name']
        self.filehash = database_data['file_hash']
        self.chunks = json.loads(database_data['chunks'])


class FileMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def is_exist(self, f):
        record = self.connect.query(self.template.GETFILE, id=f.full_path)
        .as_dict()
        return len(record)

    def fetch(self, full_path):
        record = self.connect.query(self.template.GETFILE, id=full_path)
        .as_dict()
        f = File()
        if len(record) > 0:
            f.load(record[0])
        return f

    def add(self, f):
        self.connect.query(self.template.PUTFILE, id=f.full_path,
                           base_name=f.base_name, file_hash=json.dumps(f.filehash)
                           chunks=json.dumps(f.chunks))

    def delete(self, f):
        self.connect.query(self.template.RMFILE, id=f.full_path)
