#!/usr/bin/env python3

import os
import unittest
from iron.util.log import get_logger
from iron.model import db
from iron.model.file import FileOperator
from iron.service.chunk_server import ChunkServer
from iron.service.chunk_service import ChunkService


class MockChunkServer(ChunkServer):
    def __init__(self, name: str, workspace: str) -> None:
        super().__init__(name, workspace)
        self.log = get_logger(__name__)

    def get(self, chunk: str) -> bool:
        path = os.path.join(self.workspace, chunk)
        self.log.info(f'get chunk {path} from {self.name}')
        return True

    def put(self, path: str) -> bool:
        self.log.info(f'put chunk {path} to {self.name}')
        return True

    def quota(self) -> int:
        return super().quota()


class ChunkServiceTest(unittest.TestCase):
    def setUp(self):
        self.log = get_logger()
        db.create_all()
        self.service = ChunkService()
        self.service.register_chunk_server(MockChunkServer('s1', "/tmp"))
        self.service.register_chunk_server(MockChunkServer('s2', "/tmp"))
        self.service.register_chunk_server(MockChunkServer('s3', "/tmp"))
        self.service.register_chunk_server(MockChunkServer('s4', "/tmp"))

    def tearDown(self):
        db.session.commit()
        db.drop_all()

    def test_select_server(self):
        servers = self.service.select_chunk_server(2)
        self.assertEqual(['s1', 's2'], [x.name for x in servers])
        servers_3 = self.service.select_chunk_server(3)
        self.assertEqual(['s3', 's4', 's1'], [x.name for x in servers_3])

    def test_put_get(self):
        f = FileOperator.create('f1')
        f.chunks = ['c1', 'c2']
        self.assertTrue(self.service.put(f, '/tmp'))
        db.session.add(f)
        db.session.commit()

        self.assertTrue(self.service.get(f))
