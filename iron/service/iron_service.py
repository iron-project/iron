#!/usr/bin/env python3

import sys
import os
import json
import records
import xxhash

from iron.model.chunk import Chunk, ChunkMapper
from iron.model.file import File, FileMapper
from iron.model.directory import Directory, DirectoryMapper
from iron.util.file_operator import FileUtil
from iron.service.config_service import ConfigService
from iron.service.chunk_service import ChunkServiceFactory


class Iron(object):
    def __init__(self, config=ConfigService()):
        self.config = config
        self._init_mappers()
        self.file_util = FileUtil(self.config.DEFAULT_CHUNK_SIZE, self.config.TMP_PATH)
        self.chunk_service = ChunkServiceFactory.create(self.config.BAIDU)

    def _init_mappers(self):
        self.connect = records.Database(self.config.template.SQLITE_PATH)
        with open(self.config.template.TABLE_SCHEMA, 'r') as schema:
            for sql in schema.read().split(';'):
                self.connect.query(sql)

        self.chunk_mapper = ChunkMapper(self.connect)
        self.file_mapper = FileMapper(self.connect)
        self.directory_mapper = DirectoryMapper(self.connect)

    def mkdir(self, dir_path, root_path=False):
        d = self.directory_mapper.create(dir_path)
        if self.directory_mapper.exist(d):
            return True

        if root_path:
            self.directory_mapper.add(d)
            return True

        p = self.directory_mapper.fetch(d.pardir())
        if p is None:
            print('{} is not exist.',format(p.full_path))
            return False

        self.directory_mapper.add(d)
        p.add_directory(d)
        self.directory_mapper.update(p)
        return True

    def lsdir(self, dir_path):
        dir_path = os.path.normpath(dir_path)
        d = self.directory_mapper.fetch(dir_path)
        if d is not None:
            print(directory.directories, directory.files)
            return d

        print('{} is not exist.'.format(dir_path))

    def rmdir(self, dir_path):
        d = self.directory_mapper.create(dir_path)
        if self.directory_mapper.exist(d):
            print('{} is not exist.'.format(dir_path))
            return False

        d = self.directory_mapper.fetch(d.full_path)
        if len(d.directories) or len(d.files):
            print('{} is not empty.'.format(dir_path))
            return False

        p = self.directory_mapper.fetch(d.pardir())
        assert(p is not None)
        p.rm_directory(d)
        self.directory_mapper.update(p)
        self.directory_mapper.delete(d)

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
        self.connect.query(self.config.template.SETDIR, dir_path=parent_path,
                           sub_dir=parent_info['sub_dir'], sub_file=json.dumps(sub_file))
        # Update file
        self.connect.query(self.config.template.PUTFILE, file_path=file_path, file_name=file_name,
                           file_hash=file_hash, sub_chunk=json.dumps(chunk_info))
        return file_path

    def getfile(self, remote_path, local_path='.'):
        remote_path = os.path.normpath(remote_path)
        local_path = os.path.normpath(local_path)
        file_exist, file_info = self.__file_exist__(remote_path)
        if not file_exist:
            print('file is not exist, [{}]'.format(remote_path))
            return

        file_info = file_info[0]
        # Download chunks
        chunk_info = json.loads(file_info['sub_chunk'])
        if not self.__fetch_chunk__(chunk_info):
            print('failed to fetch chunks of file [{}]'.format(remote_path))
            return
        # Combine chunks
        file_path = self.file_util.combine(
            file_info['file_name'], chunk_info, local_path)
        file_hash = self.file_util.file_hash(file_path)
        if file_hash != file_info['file_hash']:
            print('check file hash failed, [{}] was broken.'.format(
                remote_path))
            return
        return file_path

    def __rmfile_from_directory__(self, parent_path, file_name):
        exist, dir_info = self.__dir_exist__(parent_path)
        if not exist:
            return
        dir_info = dir_info[0]
        sub_file = json.loads(dir_info['sub_file'])
        if file_name in sub_file:
            sub_file.remove(file_name)
            self.connect.query(self.config.template.SETDIR, dir_path=parent_path,
                               sub_file=json.dumps(sub_file), sub_dir=dir_info['sub_dir'])

    def __rmfile_all_chunks__(self, file_path, chunk_info):
        for chunk_name in chunk_info['chunk_set']:
            self.connect.query(self.config.template.RMCHUNK, chunk_name=chunk_name)

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
        self.connect.query(self.config.template.RMFILE, file_path=file_path)

    def __store_chunk__(self, file_path, chunk_info):
        for chunk_name in chunk_info['chunk_set']:
            retval = self.chunk_service.put(
                os.path.join(self.config.TMP_PATH, chunk_name), chunk_name)
            if not retval:
                print('failed to store chunk [{}]'.format(chunk_name))
                return False

        for chunk_name in chunk_info['chunk_set']:
            tmp_chunk_path = os.path.join(self.config.TMP_PATH, chunk_name)
            chunk_hash = self.file_util.file_hash(tmp_chunk_path)
            self.connect.query(self.config.template.PUTCHUNK, chunk_name=chunk_name,
                               chunk_source=self.config.BAIDU, chunk_hash=chunk_hash)
        return True

    def __fetch_chunk__(self, chunk_info):
        print(chunk_info)
        for chunk_name in chunk_info['chunk_set']:
            retval = self.chunk_service.get(self.config.TMP_PATH, chunk_name)
            if not retval:
                print('failed to fetch remote chunk [{}]'.format(chunk_name))
                return False
        return True


    def copyfile(self, src_file, dst_file):
        pass


class UnitTest(object):
    def __init__(self):
        self.fvr = Iron()
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
        self.fvr.getfile('/bar/bin.tar.xz')
        self.fvr.getfile('/bar/bin.tar.xz', 'binary_data.xz')


if '__main__' == __name__:
    test = UnitTest()
    test.unittest_0()
    test.unittest_1()
