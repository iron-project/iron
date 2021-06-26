#!/usr/bin/env python3

import unittest
from iron.config import Config
from iron.util.hash import Hash
from iron.util.log import get_logger
from iron.util.chunk_maker import ChunkMaker


class ChunkMakerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.log = get_logger()
        self.config = Config()
        self.maker = ChunkMaker(self.config)

        self.path = '/tmp/chunk_maker_test'
        with open(self.path, 'wb') as of:
            for i in range(0, 1024 * 1204 * 3 + 512):
                of.write(b'a')

        self.sig = Hash.file_hash(self.path)

    def tearDown(self) -> None:
        self.maker.clear()

    def test_make_combine(self):
        chunks = self.maker.make(self.path, Hash.str_hash('/x/test_file'))
        self.log.info(chunks)

        replica = '/tmp/chunk_maker_test_replica'
        self.maker.combine(replica, chunks)
        self.assertEqual(self.sig, Hash.file_hash(replica))
