#!/usr/bin/env python3

import sys
import os
import xxhash


class FileUtil(object):
    def __init__(self, chunk_size, work_path):
        self.work_path = work_path
        self.chunk_size = chunk_size
        if not os.path.exists(self.work_path):
            os.mkdir(self.work_path)

    def __file_hash__(self, file_path):
        XXHASH_CHUNK_SIZE = 2 * 1024 * 1024
        x = xxhash.xxh64()
        with open(file_path, 'rb') as infile:
            chunk = infile.read(XXHASH_CHUNK_SIZE)
            while chunk:
                x.update(chunk)
                chunk = infile.read(XXHASH_CHUNK_SIZE)
        return x.hexdigest()

    def split(self, file_path, chunk_size=0):
        if not os.path.exists(file_path):
            print('{} is not exist.'.format(file_path))
            return
        if not chunk_size:
            chunk_size = self.chunk_size
        basename = self.__file_hash__(file_path)
        chunk_idx, chunk_set = 0, []
        with open(file_path, 'rb') as infile:
            chunk = infile.read(chunk_size)
            while chunk:
                chunk_name = '{}_{}'.format(basename, chunk_idx)
                chunk_path = os.path.join(self.work_path, chunk_name)
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk)
                chunk_set.append(chunk_name)
                chunk_idx += 1
                chunk = infile.read(chunk_size)
        return {'chunk_set': chunk_set, 'chunk_size': chunk_size}

    def combine(self, file_name, chunk_set, file_path):
        pass

if '__main__' == __name__:
    testdata = '../testdata/bin.tar.xz'
    tmp_path = '/tmp/forever'
    tmp_data = '/tmp/forever/bin.tar.xz'
    file_util = FileUtil(8 * 1024 * 1024, tmp_path)
    os.system('cp {} {}'.format(testdata, tmp_path))

    chunk_info = file_util.split(tmp_data)
    print(chunk_info)