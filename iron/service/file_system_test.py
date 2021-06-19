import unittest

from iron.model import db
from iron.service.file_system import FileSystemService


class IronServiceTest(unittest.TestCase):
    def setUp(self):
        db.create_all()
        self.fs = FileSystemService()

    def tearDown(self):
        db.drop_all()

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
