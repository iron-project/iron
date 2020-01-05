#!/usr/bin/env python3

import sys
import os
import json
import xxhash
import pysnooper

from iron.model.chunk import Chunk, ChunkMapper
from iron.model.file import File, FileMapper
from iron.model.directory import Directory, DirectoryMapper
from iron.model.connect import Connect
from iron.util.file_operator import FileUtil
from iron.service.config_service import ConfigService
# from iron.service.chunk_service import ChunkServiceFactory
from iron.service.chunk_service_master import ChunkServiceMaster


class IronService(object):
    def __init__(self, config=ConfigService()):
        self.config = config
        self.connect = Connect(self.config)
        self.chunk_mapper = ChunkMapper(self.connect)
        self.file_mapper = FileMapper(self.connect)
        self.directory_mapper = DirectoryMapper(self.connect)
        self.file_operator = FileUtil(self.config.DEFAULT_CHUNK_SIZE, self.config.TMP_PATH)
        # self.chunk_service = ChunkServiceFactory.create(self.config.BAIDU)
        self.chunk_server_master = ChunkServiceMaster(self.config.TMP_PATH)

    def init_records(self):
        connect = self.connect.connection()
        with open(self.config.TABLE_SCHEMA) as inf:
            for q in inf.read().split(';'):
                connect.query(q)

    # @pysnooper.snoop()
    def mkdir(self, dir_path, root_path=False):
        d = self.directory_mapper.create(dir_path)
        if self.directory_mapper.exist(d):
            return True

        if root_path:
            self.directory_mapper.add(d)
            return True

        p = self.directory_mapper.fetch(d.pardir())
        if p is None:
            print('{} is not exist.'.format(p.path))
            return False

        self.directory_mapper.add(d)
        self.directory_mapper.update(p.add_directory(d))
        return True

    # @pysnooper.snoop()
    def lsdir(self, dir_path):
        d = self.directory_mapper.create(dir_path)
        if self.directory_mapper.exist(d):
            d = self.directory_mapper.fetch(d.path)
            print(d.directories, d.files)
            return d

        print('{} is not exist.'.format(dir_path))

    def rmdir(self, dir_path):
        d = self.directory_mapper.create(dir_path)
        if not self.directory_mapper.exist(d):
            print('{} is not exist.'.format(d.path))
            return False

        d = self.directory_mapper.fetch(d.path)
        if len(d.directories) or len(d.files):
            print('{} is not empty.'.format(d.path))
            return False

        p = self.directory_mapper.fetch(d.pardir())
        assert(p is not None)
        self.directory_mapper.update(p.rm_directory(d))
        self.directory_mapper.delete(d)
        return True

    # @pysnooper.snoop()
    def putfile(self, local_path, remote_path):
        d = self.directory_mapper.create(remote_path)
        if not self.directory_mapper.exist(d):
            print('remote path [{}] is not exist.'.format(d.path))
            return False
        if not os.path.isfile(local_path):
            print('local path [{}] is not file.'.format(local_path))
            return False

        file_name = os.path.basename(local_path)
        file_path = os.path.join(remote_path, file_name)
        signature = self.file_operator.signature(local_path)
        f = self.file_mapper.create(file_path)
        if self.file_mapper.exist(f):
            f = self.file_mapper.fetch(file_path)
            if signature == f.file_hash:
                print('{} is exist, skip it.'.format(file_path))
                return True
            else:
                print('{} is change, override it.'.format(file_path))
                self.rmfile(file_path)

        chunk_info = self.file_operator.split(local_path, signature)
        self.chunk_server_master.chunks_put(chunk_info)

        f.file_hash = signature
        f.file_name = file_name
        f.chunks = chunk_info
        self.file_mapper.add(f)
        d = self.directory_mapper.fetch(remote_path)
        self.directory_mapper.update(d.add_file(f))
        return True

    # @pysnooper.snoop()
    def getfile(self, remote_path, target_dir='.'):
        remote_path = os.path.normpath(remote_path)
        target_dir = os.path.normpath(target_dir)
        if not self.file_mapper.exist(self.file_mapper.create(remote_path)):
            print('file is not exist, [{}]'.format(remote_path))
            return False

        f = self.file_mapper.fetch(remote_path)
        self.chunk_server_master.chunks_get(f.chunks, target_dir)

        file_path = self.file_operator.merge(f.file_name, f.chunks, target_dir)
        self.file_operator.clear(f.chunks, target_dir)
        signature = self.file_operator.signature(file_path)
        if signature != f.file_hash:
            print('check file hash failed, [{}] was broken.'.format(
                remote_path))
            return False
        return True

    # @pysnooper.snoop()
    def rmfile(self, file_path):
        file_path = os.path.normpath(file_path)
        if not self.file_mapper.exist(self.file_mapper.create(file_path)):
            return False

        f = self.file_mapper.fetch(file_path)
        # chunks
        for chunk_name in f.chunks['chunk_set']:
            self.chunk_mapper.delete(self.chunk_mapper.create(chunk_name, '*', '*'))

        # delete file from parent path
        d = self.directory_mapper.fetch(f.pardir())
        self.directory_mapper.update(d.rm_file(f))
        self.file_mapper.delete(f)
        return True

