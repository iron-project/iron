#!/usr/bin/env python3

import os, sys

class FileUtil(object):
    def __init__(self, chunk_size, work_path):
        self.work_path = work_path
        self.chunk_size = chunk_size

    def split(self, local_path, chunk_size = 0):
        if not chunk_size:
            chunk_size = self.chunk_size
        pass

    def combine(self, file_name, chunk_set, local_path):
        pass

if '__main__' == __name__:
    file_util = FileUtil(1024, '/tmp')