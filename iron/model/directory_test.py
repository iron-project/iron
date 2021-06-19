#!/usr/bin/env python3

import unittest

from iron.model import db
from iron.model.directory import DirectoryOperator


class DirectoryTest(unittest.TestCase):
    def setUp(self):
        db.create_all()
        d = DirectoryOperator.create('/tmp')
        d.dirs.append('2')
        d.files.append('1')
        db.session.add(d)
        db.session.commit()

    def tearDown(self):
        db.session.commit()
        db.drop_all()

    def test_exist(self):
        d = DirectoryOperator.get('/tmp')
        self.assertIsNotNone(d)
        self.assertEqual(['2'], d.dirs)
        d2 = DirectoryOperator.get('xxx')
        self.assertIsNone(d2)

    def test_update(self):
        d = DirectoryOperator.get('/tmp')
        self.assertIsNotNone(d)
        d.dirs.append('3')
        d.files.append('4')
        d2 = DirectoryOperator.get('/tmp')
        self.assertIsNotNone(d2)
        self.assertEqual(['2', '3'], d.dirs)
        self.assertEqual(['1', '4'], d.files)
