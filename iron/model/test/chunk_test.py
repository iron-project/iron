#!/usr/bin/env python3

import unittest

from iron.model import db
from iron.model.chunk import ChunkOperator


class ChunkTest(unittest.TestCase):
    def setUp(self):
        db.create_all()
        chunk = ChunkOperator.create('c1')
        chunk.server = 's1'
        chunk.sig = 'sig1'
        db.session.add(chunk)
        db.session.commit()

    def tearDown(self):
        db.session.commit()
        db.drop_all()

    def test_exist(self):
        chunk2 = ChunkOperator.get('c1', 's1')
        self.assertIsNotNone(chunk2)
        self.assertEqual('sig1', chunk2.sig)
        chunk3 = ChunkOperator.get('xxx', 'xx')
        self.assertIsNone(chunk3)

    def test_gets(self):
        chunk2 = ChunkOperator.create('c1')
        chunk2.server = 's2'
        chunk2.sig = 'sig1'
        db.session.add(chunk2)
        db.session.commit()
        chunk2 = ChunkOperator.get('c1', 's2')
        self.assertIsNotNone(chunk2)
        self.assertEqual('sig1', chunk2.sig)
        chunks = ChunkOperator.gets('c1')
        self.assertIsNotNone(chunks)
        self.assertEqual(2, len(chunks))
        self.assertEqual(chunks[0].sig, chunks[1].sig)
        self.assertNotEqual(chunks[0].server, chunks[1].server)
