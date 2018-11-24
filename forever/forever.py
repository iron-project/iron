#!/usr/bin/env python3

import sys
import os
import json
import records
import config
from fileutil import FileUtil


class Forever(object):
    def __init__(self):
        self.conn = records.Database(config.SQLITE_PATH)
        self.__init_schema__()
        self.file_util = FileUtil(config.DEFAULT_CHUNK_SIZE, config.TMP_PATH)

    def __init_schema__(self):
        with open(config.TABLE_SCHEMA, 'r') as schema:
            cmds = schema.read().split(';')
            for cmd in cmds:
                self.conn.query(cmd)

    def __dir_exist__(self, dir_path):
        dir_info = self.conn.query(
            config.SQL_LSDIR, dir_path=dir_path).as_dict()
        return len(dir_info), dir_info

    def mkdir(self, dir_path, root_path=False):
        if root_path:
            self.conn.query(config.SQL_MKDIR, dir_path=dir_path, dir_name='',
                            sub_dir='[]', sub_file='[]')
            return

        normpath = os.path.normpath(dir_path)
        parent_path, basename = os.path.split(normpath)
        exist, parent_path_info = self.__dir_exist__(parent_path)
        if not exist:
            return

        self.conn.query(config.SQL_MKDIR, dir_path=normpath, dir_name=basename,
                        sub_dir='[]', sub_file='[]')
        parent_path_info = parent_path_info[0]
        parent_path_sub_dir = json.loads(parent_path_info['sub_dir'])
        parent_path_sub_dir.append(basename)
        self.conn.query(config.SQL_UPDATE_DIR, dir_path=parent_path,
                        sub_dir=json.dumps(parent_path_sub_dir),
                        sub_file=parent_path_info['sub_file'])

    def lsdir(self, dir_path):
        dir_path = os.path.normpath(dir_path)
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
        dir_path = os.path.normpath(dir_path)
        exist, dir_info = self.__dir_exist__(dir_path)
        if not exist:
            print('{} is not exist.'.format(dir_path))
            return
        dir_info = dir_info[0]
        sub_dir = json.loads(dir_info['sub_dir'])
        sub_file = json.loads(dir_info['sub_file'])
        if len(sub_dir) or len(sub_file):
            print('{} is not empty.'.format(dir_path))
            return
        parent_path, basename = os.path.split(dir_path)
        exist, parent_path_info = self.__dir_exist__(parent_path)
        parent_path_info = parent_path_info[0]
        parent_path_sub_dir = json.loads(parent_path_info['sub_dir'])
        parent_path_sub_dir.remove(basename)
        self.conn.query(config.SQL_UPDATE_DIR, dir_path=parent_path,
                        sub_dir=json.dumps(parent_path_sub_dir),
                        sub_file=parent_path_info['sub_file'])
        self.conn.query(config.SQL_RMDIR, dir_path=dir_path)

    def __file_exist__(self, remote_path):
        file_info = self.conn.query(
            config.SQL_LSFILE, file_path=remote_path).as_dict()
        return len(file_info), file_info

    def __file_partition__(self, local_path, chunk_size=config.DEFAULT_CHUNK_SIZE):
        pass

    def putfile(self, local_path, remote_path):
        pass

    def getfile(self, remote_path, local_path):
        pass

    def copyfile(self, src_file, dst_file):
        pass


class UnitTest(object):
    def __init__(self):
        self.fvr = Forever()
        self.fvr.mkdir('/', root_path=True)

    def unittest_0(self):
        self.fvr.mkdir('/foo')
        self.fvr.lsdir('/')
        self.fvr.lsdir('/bar')
        self.fvr.mkdir('/bar')
        self.fvr.lsdir('/')
        self.fvr.lsdir('/bar')
        self.fvr.mkdir('/bar/bla')
        self.fvr.rmdir('/bar/')
        self.fvr.rmdir('/bla')
        self.fvr.rmdir('/foo')
        self.fvr.lsdir('/')
        self.fvr.lsdir('/foo')


if '__main__' == __name__:
    test = UnitTest()
    test.unittest_0()
