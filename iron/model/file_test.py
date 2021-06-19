#!/usr/bin/env python3

import unittest

from iron.model import db
from iron.model.file import File, FileOperator


class FileTest(unittest.TestCase):
    def setUp(self):
        db.create_all()
        f = FileOperator.create('/tmp/x')
        f.chunks = ['1', '2']
        db.session.add(f)
        db.session.commit()

    def tearDown(self):
        db.session.commit()
        db.drop_all()

    def test_exist(self):
        f2 = FileOperator.get('/tmp/x')
        self.assertIsNotNone(f2)
        self.assertEqual(['1', '2'], f2.chunks)
        f3 = FileOperator.get('xxx')
        self.assertIsNone(f3)

    def test_delete(self):
        f2 = FileOperator.get('/tmp/x')
        self.assertIsNotNone(f2)
        db.session.delete(f2)
        db.session.commit()
        f3 = FileOperator.get('/tmp/x')
        self.assertIsNone(f3)

    def test_modify_chunks(self):
        f2 = FileOperator.get('/tmp/x')
        self.assertIsNotNone(f2)
        self.assertEqual(['1', '2'], f2.chunks)
        f2.chunks.append('3')
        f3 = FileOperator.get('/tmp/x')
        self.assertIsNotNone(f3)
        self.assertEqual(['1', '2', '3'], f3.chunks)
