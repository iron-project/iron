#!/usr/bin/env python3

import sys
import os
import xxhash
from iron.service.config_service import ConfigService

class FileUtil(object):
    def __init__(self, chunk_size, workdir):
        self.config = ConfigService()
        self.workdir = workdir
        self.chunk_size = chunk_size
        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

    @staticmethod
    def signature(file_path, config = ConfigService()):
        x = xxhash.xxh64()
        with open(file_path, 'rb') as infile:
            chunk = infile.read(config.XXHASH_CHUNK_SIZE)
            while chunk:
                x.update(chunk)
                chunk = infile.read(config.XXHASH_CHUNK_SIZE)
        return x.hexdigest()

    def chunk_signature(self, chunk_name):
        x = xxhash.xxh64()
        with open(os.path.join(self.workdir, chunk_name), 'rb') as infile:
            chunk = infile.read(self.config.XXHASH_CHUNK_SIZE)
            while chunk:
                x.update(chunk)
                chunk = infile.read(self.config.XXHASH_CHUNK_SIZE)
        return x.hexdigest()

    def split(self, file_path, signature=None, chunk_size=0):
        if not os.path.exists(file_path):
            print('{} is not exist.'.format(file_path))
            return
        if not chunk_size:
            chunk_size = self.chunk_size
        if not signature:
            signature = self.signature(file_path)

        basename = signature
        chunk_idx, chunk_set = 0, []
        with open(file_path, 'rb') as infile:
            chunk = infile.read(chunk_size)
            while chunk:
                chunk_name = '{}.{}'.format(basename, chunk_idx)
                chunk_path = os.path.join(self.workdir, chunk_name)
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk)

                chunk_set.append(chunk_name)
                chunk_idx += 1
                chunk = infile.read(chunk_size)
        return {'chunk_set': chunk_set, 'chunk_size': chunk_size}

    def merge(self, file_name, chunk_info, workdir):
        if os.path.isdir(workdir):
            file_path = os.path.join(workdir, file_name)
        else:
            raise Exception('{} is not exists.'.format(workdir))

        chunk_set = chunk_info['chunk_set']
        # chunk.0, chunk.1, ... , chunk.n
        chunk_set.sort(key=lambda element: int(element.split('.')[-1]))
        open(file_path, 'wb').close()
        with open(file_path, 'ab') as outfile:
            for chunk_name in chunk_set:
                chunk_path = os.path.join(workdir, chunk_name)
                with open(chunk_path, 'rb') as infile:
                    chunk = infile.read(chunk_info['chunk_size'])
                    outfile.write(chunk)
        return file_path

    def clear(self, chunk_info, workdir):
        if not os.path.isdir(workdir):
            return False
        chunk_set = chunk_info['chunk_set']
        for chunk in chunk_set:
            os.unlink(os.path.join(workdir, chunk))
        return True

