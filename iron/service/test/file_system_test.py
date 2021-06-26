#!/usr/bin/env python3

from iron.model.directory import DirectoryOperator
from iron.util.log import get_logger
from iron.model.file import FileOperator
from iron.service.test.chunk_service_test import MockChunkServer
from iron.util.hash import Hash
import unittest

from iron.model import db
from iron.service.file_system import FileSystemService


class FileSystemServiceTest(unittest.TestCase):
    def setUp(self):
        self.log = get_logger(__name__)
        db.create_all()
        self.fs = FileSystemService(db)

        self.path = '/tmp/file_system_test'
        with open(self.path, 'wb') as of:
            for i in range(0, 1024 * 1204 * 3 + 512):
                of.write(b'a')

        self.sig = Hash.file_hash(self.path)

    def tearDown(self):
        db.drop_all()
        self.fs.maker.clear()

    def test_directory_operations(self):
        self.assertTrue(self.fs.mkdir('/'))
        self.assertTrue(self.fs.mkdir('/x'))
        self.assertTrue(self.fs.mkdir('/x'))
        self.assertTrue(self.fs.mkdir('/y'))
        self.assertFalse(self.fs.mkdir('/b/a'))
        self.assertTrue(self.fs.rmdir('/b/a'))
        self.assertFalse(self.fs.rmdir('/'))
        self.assertEqual(['x', 'y'], self.fs.lsdir('/').dirs)
        self.assertTrue(self.fs.rmdir('/x'))
        self.assertEqual(['y'], self.fs.lsdir('/').dirs)
        self.assertTrue(self.fs.rmdir('/x'))
        self.assertEqual(['y'], self.fs.lsdir('/').dirs)
        self.assertTrue(self.fs.rmdir('/a'))

    def test_putfile(self):
        self.assertTrue(self.fs.mkdir('/'))
        self.assertTrue(self.fs.mkdir('/x'))
        self.assertIsNone(self.fs.putfile(self.path, '/x/test_file'))
        wp = self.fs.config.chunk_maker_workspace
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s1', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s2', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s3', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s4', wp))
        f = self.fs.putfile(self.path, '/x/test_file')
        self.assertIsNotNone(f)
        self.assertEqual('test_file', f.name)
        self.log.info(FileOperator.marshal(f))
        self.assertIsNone(self.fs.putfile(self.path, '/x/test_file'))
        self.assertIsNotNone(self.fs.putfile(self.path, '/x/test_file_2'))
        d = self.fs.lsdir('/x')
        self.log.info(DirectoryOperator.marshal(d))
        self.assertTrue('test_file_2' in d.files)
        self.assertIsNone(self.fs.putfile(self.path, '/no/test_file'))
        self.assertIsNone(self.fs.putfile('/tmp/nosuchfile', '/test_file'))

    def test_getfile(self):
        self.assertTrue(self.fs.mkdir('/'))
        wp = self.fs.config.chunk_maker_workspace
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s1', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s2', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s3', wp))
        self.fs.chunk_service.register_chunk_server(MockChunkServer('s4', wp))
        f = self.fs.putfile(self.path, '/file')
        self.assertIsNotNone(f)
        f2 = '/tmp/file_system_test_file2'
        r = self.fs.getfile('/file', f2)
        self.assertTrue(r)
        self.assertEqual(self.sig, Hash.file_hash(f2))
        self.assertFalse(self.fs.getfile('/no', '/tmp/2'))
