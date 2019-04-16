#!/usr/bin/env python3

import json
from template import SQLTemplate

class Directory(object):
    def __init__(self):
        self.full_path = ''
        self.base_name = ''
        self.files = []
        self.directories = []

    def load(self, database_data):
        self.full_path = database_data['id']
        self.base_name = database_data['base_name']
        self.files = json.loads(database_data['files'])
        self.directories = json.loads(database_data['directories'])

    def add_directory(self, d):
        if d.base_name in self.directoies:
            return False
        self.directories.append(d.base_name)
        return True

    def add_file(self, f):
        if f.base_name in self.files:
            return False
        self.files.append(f.base_name)
        return True

    def rm_directory(self, d):
        self.directories.remove(d.base_name)

    def rm_file(self, f):
        self.files.remove(f.base_name)

class DirectoryMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def is_exist(self, d):
        record = self.connect.query(self.template.GETDIR, id=d.full_path)
        .as_dict()
        return len(record)

    def fetch(self, full_path):
        record = self.connect.query(self.template.GETDIR, id=full_path)
        .as_dict()
        d = Directory()
        if len(record) > 0:
            d.load(record[0])
        return d

    def add(self, d):
        self.connect.query(self.template.PUTDIR, id=d.full_path,
                           base_name=d.base_name, files=json.dumps(d.files)
                           directories=json.dumps(d.directories))

    def update(self, d):
        self.connect.query(self.template.SETDIR, id=d.full_path,
                           directories=json.dumps(d.directories),
                           files=json.dumps(d.files))

    def delete(self, d):
        self.connect.query(self.template.RMDIR, id=d.full_path)