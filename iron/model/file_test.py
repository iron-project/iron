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
        f.file_name = 'x.cpp'
        f.path = '/tmp/x.cpp'
        f.file_hash = 'file_hash'
        f.chunks = {'chunk_set': ['1', '2'], 'chunk_size': 1}
        self.assertFalse(self.mapper.exist(f))
        self.mapper.add(f)
        self.assertTrue(self.mapper.exist(f))

    def test_fetch(self):
        f = File()
        f.file_name = 'x.cpp'
        f.path = '/tmp/x.cpp'
        f.file_hash = 'file_hash'
        f.chunks = {'chunk_set': ['1', '2'], 'chunk_size': 1}
        self.mapper.add(f)
        x_cpp = self.mapper.fetch('/tmp/x.cpp')
        self.assertEqual(f.file_name, x_cpp.file_name)
        self.assertEqual(f.path, x_cpp.path)
        self.assertEqual(f.file_hash, x_cpp.file_hash)
        self.assertEqual(f.chunks, x_cpp.chunks)
        self.assertIsNone(self.mapper.fetch('/tmp/notexist.cpp'))

    def test_delete(self):
        f = File()
        f.file_name = 'x.cpp'
        f.path = '/tmp/x.cpp'
        f.file_hash = 'file_hash'
        f.chunks = {'chunk_set': ['1', '2'], 'chunk_size': 1}
        self.mapper.add(f)
        self.mapper.delete(f)
        self.assertFalse(self.mapper.exist(f))



