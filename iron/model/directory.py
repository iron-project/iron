#!/usr/bin/env python3

import json, os
from iron.model.template import SQLTemplate

class Directory(object):
    def __init__(self):
        self.path = ''
        self.dir_name = ''
        self.files = []
        self.directories = []

    def load(self, database_data):
        self.path = database_data['id']
        self.dir_name = database_data['dir_name']
        self.files = json.loads(database_data['files'])
        self.directories = json.loads(database_data['directories'])

    def pardir(self):
        return os.path.split(self.path)[0]

    def add_directory(self, d):
        if d.dir_name not in self.directories:
            self.directories.append(d.dir_name)
        return self

    def add_file(self, f):
        if f.file_name not in self.files:
            self.files.append(f.file_name)
        return self

    def rm_directory(self, d):
        self.directories.remove(d.dir_name)
        return self

    def rm_file(self, f):
        self.files.remove(f.file_name)
        return self

class DirectoryMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def create(self, path):
        normpath = os.path.normpath(path)
        d = Directory()
        d.dir_name = os.path.basename(normpath)
        d.path = normpath
        return d

    def exist(self, d):
        record = self.connect.connection().query(
            self.template.GETDIR, id=d.path).as_dict()
        return len(record) > 0

    def fetch(self, path):
        normpath = os.path.normpath(path)
        record = self.connect.connection().query(
            self.template.GETDIR, id=normpath).as_dict()
        if len(record) > 0:
            d = Directory()
            d.load(record[0])
            return d
        return None

    def add(self, d):
        self.connect.connection().query(
            self.template.PUTDIR, id=d.path,
            dir_name=d.dir_name, files=json.dumps(d.files),
            directories=json.dumps(d.directories))

    def update(self, d):
        self.connect.connection().query(
            self.template.SETDIR, id=d.path,
            directories=json.dumps(d.directories),
            files=json.dumps(d.files))

    def delete(self, d):
        self.connect.connection().query(self.template.RMDIR, id=d.path)
