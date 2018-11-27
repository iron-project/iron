#!/usr/bin/env python3

import sys
import os
import xxhash
import config


class FileUtil(object):
    def __init__(self, chunk_size, work_path):
        self.work_path = work_path
        self.chunk_size = chunk_size
        if not os.path.exists(self.work_path):
            os.mkdir(self.work_path)

    @staticmethod
    def file_hash(file_path):
        x = xxhash.xxh64()
        with open(file_path, 'rb') as infile:
            chunk = infile.read(config.XXHASH_CHUNK_SIZE)
            while chunk:
                x.update(chunk)
                chunk = infile.read(config.XXHASH_CHUNK_SIZE)
        return x.hexdigest()

    def split(self, file_path, chunk_size=0):
        if not os.path.exists(file_path):
            print('{} is not exist.'.format(file_path))
            return
        if not chunk_size:
            chunk_size = self.chunk_size
        file_path_hash = xxhash.xxh64(file_path).hexdigest()
        basename = self.file_hash(file_path)
        chunk_idx, chunk_set = 0, []
        with open(file_path, 'rb') as infile:
            chunk = infile.read(chunk_size)
            while chunk:
                chunk_name = '{}_{}_{}'.format(
                    file_path_hash, basename, chunk_idx)
                chunk_path = os.path.join(self.work_path, chunk_name)
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk)
                chunk_set.append(chunk_name)
                chunk_idx += 1
                chunk = infile.read(chunk_size)
        return {'chunk_set': chunk_set, 'chunk_size': chunk_size}

    def combine(self, file_name, chunk_info, file_path):
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, file_name)
        chunk_set = chunk_info['chunk_set']
        chunk_set.sort()  # chunk_0, chunk_1, ... , chunk_n
        open(file_path, 'wb').close()
        with open(file_path, 'ab') as outfile:
            for chunk_name in chunk_set:
                chunk_path = os.path.join(self.work_path, chunk_name)
                with open(chunk_path, 'rb') as infile:
                    chunk = infile.read(chunk_info['chunk_size'])
                    outfile.write(chunk)
        return file_path


if '__main__' == __name__:
    data_name = 'bin.tar.xz'
    testdata = '../testdata/bin.tar.xz'
    tmp_path = config.TMP_PATH
    tmp_data = os.path.join(tmp_path, data_name)
    file_util = FileUtil(config.DEFAULT_CHUNK_SIZE, tmp_path)
    os.system('cp {} {}'.format(testdata, tmp_path))
    chunk_info = file_util.split(tmp_data)
    os.system('rm -rf {}'.format(tmp_data))
    file_path = file_util.combine(data_name, chunk_info, tmp_path)
    os.system('rm -rf {}'.format(tmp_data))
    file_path = file_util.combine(data_name, chunk_info, tmp_data)
    print(file_path)
