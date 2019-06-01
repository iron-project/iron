#!/usr/bin/env python3

import unittest
import records

from iron.model.file import File
from iron.model.directory import Directory, DirectoryMapper
from iron.service.config_service import ConfigService

class DirectoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()

    def setUp(self):
        self.connect = records.Database(self.config.SQLITE_URI)
        with open(self.config.TABLE_SCHEMA, 'r') as schema:
            cmds = schema.read().split(';')
            for cmd in cmds:
                self.connect.query(cmd)

        self.mapper = DirectoryMapper(self.connect)

    def test_exist(self):
        d = Directory()
        d.path = '/tmp'
        d.dir_name = 'tmp'
        d.files = ['xxx']
        d.directories = ['foo', 'bar']
        self.assertFalse(self.mapper.exist(d))
        self.mapper.add(d)
        self.assertTrue(self.mapper.exist(d))

    def test_fetch(self):
        d = Directory()
        d.path = '/tmp'
        d.dir_name = 'tmp'
        d.files = ['xxx']
        d.directories = ['foo', 'bar']
        self.mapper.add(d)
        tmp = self.mapper.fetch('/tmp')
        self.assertEqual(d.dir_name, tmp.dir_name)
        self.assertEqual(d.path, tmp.path)
        self.assertEqual(d.files, tmp.files)
        self.assertEqual(d.directories, tmp.directories)
        self.assertIsNone(self.mapper.fetch('notexist'))

    def test_delete(self):
        d = Directory()
        d.path = '/tmp'
        d.dir_name = 'tmp'
        d.files = ['xxx']
        d.directories = ['foo', 'bar']
        self.mapper.add(d)
        self.mapper.delete(d)
        self.assertFalse(self.mapper.exist(d))

    def test_update(self):
        d = Directory()
        d.path = '/tmp'
        d.dir_name = 'tmp'
        d.files = ['xxx']
        d.directories = ['foo', 'bar']
        self.mapper.add(d)
        f = File()
        f.file_name = 'f'
        d2 = Directory()
        d2.dir_name = 'd2'
        d.add_file(f)
        d.add_directory(d2)
        self.mapper.update(d)
        tmp = self.mapper.fetch('/tmp')
        self.assertEqual(d.dir_name, tmp.dir_name)
        self.assertEqual(d.path, tmp.path)
        self.assertEqual(['xxx', 'f'], tmp.files)
        self.assertEqual(['foo', 'bar', 'd2'], tmp.directories)



