#!/usr/bin/env python3

import json, os
from iron.model.template import SQLTemplate

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

    def pardir(self):
        return os.path.split(self.full_path)[0]

    def add_directory(self, d):
        if d.base_name in self.directories:
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

    def create(self, full_path):
        d = Directory()
        normpath = os.path.normpath(path)
        d.base_name = os.path.basename(normpath)
        d.full_path = normpath

    def exist(self, d):
        record = self.connect.query(
            self.template.GETDIR, id=d.full_path).as_dict()
        return len(record) > 0

    def fetch(self, full_path):
        record = self.connect.query(
            self.template.GETDIR, id=full_path).as_dict()
        if len(record) > 0:
            d = Directory()
            d.load(record[0])
            return d
        return None

    def add(self, d):
        self.connect.query(self.template.PUTDIR, id=d.full_path,
                           base_name=d.base_name, files=json.dumps(d.files),
                           directories=json.dumps(d.directories))

    def update(self, d):
        self.connect.query(self.template.SETDIR, id=d.full_path,
                           directories=json.dumps(d.directories),
                           files=json.dumps(d.files))

    def delete(self, d):
        self.connect.query(self.template.RMDIR, id=d.full_path)
