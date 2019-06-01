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
from iron.service.chunk_service import ChunkServiceFactory


class IronService(object):
    def __init__(self, config=ConfigService()):
        self.config = config
        self.connect = Connect(self.config)
        self.chunk_mapper = ChunkMapper(self.connect)
        self.file_mapper = FileMapper(self.connect)
        self.directory_mapper = DirectoryMapper(self.connect)
        self.file_util = FileUtil(self.config.DEFAULT_CHUNK_SIZE, self.config.TMP_PATH)
        self.chunk_service = ChunkServiceFactory.create(self.config.BAIDU)

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

    # @pysnooper.snoop()
    def putfile(self, local_path, remote_path):
        d = self.directory_mapper.create(remote_path)
        if not self.directory_mapper.exist(d):
            print('remote path [{}] is not exist.'.format(d.path))
            return
        if not os.path.isfile(local_path):
            print('local path [{}] is not file.'.format(local_path))
            return

        # If file hash is equal, don't put again.
        # If file hash is not equal, just delete old file.
        file_name = os.path.split(local_path)[-1]
        file_path = os.path.join(remote_path, file_name)
        file_hash = self.file_util.file_hash(local_path)
        f = self.file_mapper.create(file_path)
        if self.file_mapper.exist(f):
            f = self.file_mapper.fetch(file_path)
            if file_hash == f.file_hash:
                print('{} is exist, skip it.'.format(file_path))
                return
            else:
                print('{} is change, override it.'.format(file_path))
                self.rmfile(file_path)

        # Update chunks
        chunk_info = self.file_util.split(local_path)
        if not self._store_chunk(file_path, chunk_info):
            return

        f.file_hash = file_hash
        f.file_name = file_name
        f.chunks = chunk_info
        self.file_mapper.add(f)
        d = self.directory_mapper.fetch(remote_path)
        self.directory_mapper.update(d.add_file(f))
        return file_path

    # @pysnooper.snoop()
    def getfile(self, remote_path, local_path='.'):
        remote_path = os.path.normpath(remote_path)
        local_path = os.path.normpath(local_path)
        if not self.file_mapper.exist(self.file_mapper.create(remote_path)):
            print('file is not exist, [{}]'.format(remote_path))
            return

        f = self.file_mapper.fetch(remote_path)
        if not self._fetch_chunk(f.chunks):
            print('failed to fetch chunks of file [{}]'.format(remote_path))
            return

        # combine chunks
        file_path = self.file_util.combine(f.file_name, f.chunks, local_path)
        file_hash = self.file_util.file_hash(file_path)
        if file_hash != f.file_hash:
            print('check file hash failed, [{}] was broken.'.format(
                remote_path))
            return
        return file_path

    # @pysnooper.snoop()
    def rmfile(self, file_path):
        file_path = os.path.normpath(file_path)
        if not self.file_mapper.exist(self.file_mapper.create(file_path)):
            return

        f = self.file_mapper.fetch(file_path)
        # chunks
        for chunk_name in f.chunks['chunk_set']:
            self.chunk_mapper.delete(self.chunk_mapper.create(chunk_name, '*', '*'))

        # delete file from parent path
        d = self.directory_mapper.fetch(f.pardir())
        self.directory_mapper.update(d.rm_file(f))
        self.file_mapper.delete(f)

    def _store_chunk(self, file_path, chunk_info):
        # TODO: put chunks into different chunk service
        for chunk_name in chunk_info['chunk_set']:
            chunk_path = os.path.join(self.config.TMP_PATH, chunk_name)
            if not self.chunk_service.put(chunk_path, chunk_name):
                print('failed to store chunk [{}]'.format(chunk_name))
                return False

        for chunk_name in chunk_info['chunk_set']:
            chunk_path = os.path.join(self.config.TMP_PATH, chunk_name)
            chunk_hash = self.file_util.file_hash(chunk_path)
            self.chunk_mapper.add(self.chunk_mapper.create(chunk_name, self.config.BAIDU, chunk_hash))
        return True

    def _fetch_chunk(self, chunk_info):
        # TODO: check chunks hash, fetch chunks from different chunk service
        for chunk_name in chunk_info['chunk_set']:
            if not self.chunk_service.get(self.config.TMP_PATH, chunk_name):
                print('failed to fetch remote chunk [{}]'.format(chunk_name))
                return False
        return True

