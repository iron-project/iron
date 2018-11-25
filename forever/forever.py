#!/usr/bin/env python3

import sys
import os
import json
import records
import xxhash
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
        normpath = os.path.normpath(dir_path)
        if self.__dir_exist__(normpath)[0]:
            return

        if root_path:
            self.conn.query(config.SQL_MKDIR, dir_path=dir_path, dir_name='',
                            sub_dir='[]', sub_file='[]')
            return

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
        print(sub_dir, sub_file)

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
            config.SQL_GETFILE, file_path=remote_path).as_dict()
        return len(file_info), file_info

    def putfile(self, local_path, remote_parent_path):
        parent_path = os.path.normpath(remote_parent_path)
        local_path = os.path.normpath(local_path)
        parent_exist, parent_info = self.__dir_exist__(parent_path)
        if not parent_exist:
            print('remote path: {} is not exist.'.format(parent_path))
            return
        if not os.path.isfile(local_path):
            print('local path: {} is not file.'.format(local_path))
            return
        # If file hash is equal, don't put again.
        # If file hash is not equal, just delete old file.
        file_hash = self.file_util.file_hash(local_path)
        file_name = os.path.split(local_path)[1]
        file_path = os.path.join(parent_path, file_name)
        file_exist, file_info = self.__file_exist__(file_path)
        if file_exist:
            file_info = file_info[0]
            if file_hash == file_info['file_hash']:
                print('{} is exist.'.format(file_path))
                return
            else:
                self.rmfile(file_path)
        # Update chunks
        chunk_info = self.file_util.split(local_path)
        if not self.__store_chunk__(file_path, chunk_info):
            return
        # Update parent path
        parent_info = parent_info[0]
        sub_file = json.loads(parent_info['sub_file'])
        sub_file.append(file_name)
        self.conn.query(config.SQL_UPDATE_DIR, dir_path=parent_path,
                        sub_dir=parent_info['sub_dir'], sub_file=json.dumps(sub_file))
        # Update file
        self.conn.query(config.SQL_PUTFILE, file_path=file_path, file_name=file_name,
                        file_hash=file_hash, sub_chunk=json.dumps(chunk_info))
        return file_path

    def getfile(self, remote_path, local_path):
        pass

    def __rmfile_from_directory__(self, parent_path, file_name):
        exist, dir_info = self.__dir_exist__(parent_path)
        if not exist:
            return
        dir_info = dir_info[0]
        sub_file = json.loads(dir_info['sub_file'])
        if file_name in sub_file:
            sub_file.remove(file_name)
            self.conn.query(config.SQL_UPDATE_DIR, dir_path=parent_path,
                            sub_file=json.dumps(sub_file), sub_dir=dir_info['sub_dir'])

    def __rmfile_all_chunks__(self, file_path, chunk_info):
        file_path_hash = xxhash.xxh64(file_path.encode()).hexdigest()
        for chunk_name in chunk_info['chunk_set']:
            chunk_id = '{}_{}'.format(file_path_hash, chunk_name)
            self.conn.query(config.SQL_RMCHUNK, chunk_id=chunk_id)

    def rmfile(self, file_path):
        file_path = os.path.normpath(file_path)
        file_exist, file_info = self.__file_exist__(file_path)
        if not file_exist:
            return
        file_info = file_info[0]
        parent_path, file_name = os.path.split(file_path)
        self.__rmfile_from_directory__(parent_path, file_name)
        self.__rmfile_all_chunks__(file_path,
                                   json.loads(file_info['sub_chunk']))
        self.conn.query(config.SQL_RMFILE, file_path=file_path)

    def __store_chunk__(self, file_path, chunk_info):
        # TODO: Upload chunks
        file_path_hash = xxhash.xxh64(file_path.encode()).hexdigest()
        for chunk_name in chunk_info['chunk_set']:
            chunk_id = '{}_{}'.format(file_path_hash, chunk_name)
            tmp_chunk_path = os.path.join(config.TMP_PATH, chunk_name)
            chunk_hash = self.file_util.file_hash(tmp_chunk_path)
            self.conn.query(config.SQL_PUTCHUNK, chunk_id=chunk_id,
                            chunk_source=config.BAIDU, chunk_hash=chunk_hash)
        return True

    def copyfile(self, src_file, dst_file):
        pass


class UnitTest(object):
    def __init__(self):
        self.fvr = Forever()
        self.fvr.mkdir('/', root_path=True)

    def unittest_0(self):
        self.fvr.mkdir('/foo')
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

    def unittest_1(self):
        local_path = '../testdata/bin.tar.xz'
        remote_path = '/bar/'
        self.fvr.putfile(local_path, remote_path)
        self.fvr.lsdir('/bar')
        self.fvr.putfile(local_path, remote_path)
        self.fvr.rmfile('/bar/bin.tar.xz')
        self.fvr.lsdir('/bar')
        self.fvr.putfile(local_path, remote_path)
        self.fvr.lsdir('/bar')


if '__main__' == __name__:
    test = UnitTest()
    test.unittest_0()
    test.unittest_1()
