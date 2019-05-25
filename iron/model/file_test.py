#!/usr/bin/env python3

import unittest
import records

from iron.model.file import File, FileMapper
from iron.service.config_service import ConfigService

class FileTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()

    def setUp(self):
        self.connect = records.Database(self.config.SQLITE_URI)
        with open(self.config.TABLE_SCHEMA, 'r') as schema:
            cmds = schema.read().split(';')
            for cmd in cmds:
                self.connect.query(cmd)

        self.mapper = FileMapper(self.connect)

    def test_exist(self):
        f = File()
        f.base_name = 'x.cpp'
        f.full_path = '/tmp/x.cpp'
        f.filehash = 'filehash'
        f.chunks = ['c1', 'c2']
        self.assertFalse(self.mapper.exist(f))
        self.mapper.add(f)
        self.assertTrue(self.mapper.exist(f))

    def test_fetch(self):
        f = File()
        f.base_name = 'x.cpp'
        f.full_path = '/tmp/x.cpp'
        f.filehash = 'filehash'
        f.chunks = ['c1', 'c2']
        self.mapper.add(f)
        x_cpp = self.mapper.fetch('/tmp/x.cpp')
        self.assertEqual(f.base_name, x_cpp.base_name)
        self.assertEqual(f.full_path, x_cpp.full_path)
        self.assertEqual(f.filehash, x_cpp.filehash)
        self.assertEqual(f.chunks, x_cpp.chunks)
        self.assertIsNone(self.mapper.fetch('/tmp/notexist.cpp'))

    def test_delete(self):
        f = File()
        f.base_name = 'x.cpp'
        f.full_path = '/tmp/x.cpp'
        f.filehash = 'filehash'
        f.chunks = ['c1', 'c2']
        self.mapper.add(f)
        self.mapper.delete(f)
        self.assertFalse(self.mapper.exist(f))



