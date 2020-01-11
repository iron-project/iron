#!/usr/bin/env python3

import os
import unittest
import records

from iron.service.config_service import ConfigService
from iron.util.file_operator import FileUtil

class FileUtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()

    def setUp(self):
        self.data_name = 'bin.tar.xz'
        self.testdata = 'testdata/bin.tar.xz'
        self.tmp_path = self.config.TMP_PATH
        self.tmp_data = os.path.join(self.tmp_path, self.data_name)
        self.file_util = FileUtil(self.config.DEFAULT_CHUNK_SIZE, self.tmp_path)

    def tearDown(self):
        os.system('rm -rf {}'.format(self.tmp_path))

    def test_simple(self):
        os.system('cp {} {}'.format(self.testdata, self.tmp_path))
        chunk_info = self.file_util.split(self.tmp_data)
        os.system('rm -rf {}'.format(self.tmp_data))

        file_path = self.file_util.merge(self.data_name, chunk_info, self.tmp_path)
        os.system('rm -rf {}'.format(self.tmp_data))
        self.assertEqual('/tmp/iron/bin.tar.xz', file_path)

