#!/usr/bin/env python3

import os
import unittest
import records
import pysnooper

from iron.service.config_service import ConfigService
from iron.util.file_operator import FileUtil
from iron.service.chunk_service import ChunkServiceFactory

class ChunkServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()

    def setUp(self):
        self.data_name = 'bin.tar.xz'
        self.testdata = 'testdata/bin.tar.xz'
        self.tmp_path = self.config.TMP_PATH
        self.tmp_data = os.path.join(self.tmp_path, self.data_name)
        self.baidu = ChunkServiceFactory.create(self.config.BAIDU)
        self.splitter = FileUtil(self.config.DEFAULT_CHUNK_SIZE, self.config.TMP_PATH)
        os.system('cp {} {}'.format(self.testdata, self.tmp_path))
        self.chunk_info = self.splitter.split(self.tmp_data)

    def tearDown(self):
        os.system('rm -rf {}'.format(self.tmp_path))

    # @pysnooper.snoop()
    def test_simple(self):
        response = self.baidu.get(self.tmp_path, 'notexist')
        print(response)

        for x in self.chunk_info['chunk_set'][:2]:
            chunk_file = os.path.join(self.tmp_path, x)
            self.baidu.put(chunk_file, x)

        self.tearDown()
        os.makedirs(self.tmp_path)
        for x in self.chunk_info['chunk_set'][:2]:
            self.baidu.get(self.tmp_path, x)

    def test_quota(self):
        quota = self.baidu.quota();
        print(quota)
