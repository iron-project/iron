#!/usr/bin/env python3

import sys
import os
import json
import records

SQLITE_PATH = 'sqlite://'
TABLE_SCHEMA = 'schema.sql'

SQL_MKDIR = '''
INSERT INTO directory (dir_path, dir_name, sub_dir, sub_file)
VALUES (:dir_path, :dir_name, :sub_dir, :sub_file)
'''

SQL_LSDIR = '''
SELECT * FROM directory WHERE dir_path = :dir_path
'''

SQL_UPDATE_DIR = '''
UPDATE directory SET sub_dir = :sub_dir, sub_file = :sub_file WHERE dir_path = :dir_path
'''


class Forever(object):
    def __init__(self):
        self.conn = records.Database(SQLITE_PATH)
        self.__init_schema__()

    def __init_schema__(self):
        with open(TABLE_SCHEMA, 'r') as schema:
            cmds = schema.read().split(';')
            for cmd in cmds:
                self.conn.query(cmd)

    def __dir_exist__(self, dir_path):
        dir_info = self.conn.query(SQL_LSDIR, dir_path=dir_path).as_dict()
        return len(dir_info), dir_info

    def mkdir(self, dir_path, root_path=False):
        if root_path:
            self.conn.query(SQL_MKDIR, dir_path=dir_path, dir_name='',
                            sub_dir='[]', sub_file='[]')
            return

        normpath = os.path.normpath(dir_path)
        parent_path, basename = os.path.split(normpath)
        exist, parent_path_info = self.__dir_exist__(parent_path)
        if not exist:
            return

        self.conn.query(SQL_MKDIR, dir_path=normpath, dir_name=basename,
                        sub_dir='[]', sub_file='[]')
        parent_path_info = parent_path_info[0]
        parent_path_sub_dir = json.loads(parent_path_info['sub_dir'])
        parent_path_sub_dir.append(basename)
        self.conn.query(SQL_UPDATE_DIR, dir_path=parent_path, sub_dir=json.dumps(parent_path_sub_dir),
                        sub_file=parent_path_info['sub_file'])

    def lsdir(self, dir_path):
        dir_exist, dir_info = self.__dir_exist__(dir_path)
        if dir_exist:
            self.__dir_format__(dir_info[0])
        else:
            print('{} is not exist.'.format(dir_path))

    def __dir_format__(self, dir_info):
        sub_dir = json.loads(dir_info['sub_dir'])
        sub_file = json.loads(dir_info['sub_file'])
        print(sub_dir + sub_file)

    def rmdir(self, dir_path):
        pass

    def copyfile(self, src_file, dst_file):
        pass


if '__main__' == __name__:
    fvr = Forever()
    fvr.mkdir('/', root_path=True)
    fvr.mkdir('/foo')
    fvr.lsdir('/')
    fvr.lsdir('/bar')
    fvr.mkdir('/bar')
    fvr.lsdir('/')
