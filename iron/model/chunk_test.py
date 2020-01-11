#!/usr/bin/env python3

import unittest
import records

from iron.model.chunk import Chunk, ChunkMapper
from iron.model.connect import Connect
from iron.service.config_service import ConfigService

class ChunkTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()
        self.config.SQLITE_URI = 'sqlite:///:memory:'

    def setUp(self):
        self.connect = Connect(self.config)
        self.connection = self.connect.connection()
        with open(self.config.TABLE_SCHEMA, 'r') as schema:
            cmds = schema.read().split(';')
            for cmd in cmds:
                self.connection.query(cmd)

        self.mapper = ChunkMapper(self.connect)

    def test_exist(self):
        c = Chunk()
        c.chunk_name = 'notexist'
        c.signature = 'hash'
        c.storage = 'baidu'
        self.assertFalse(self.mapper.exist(c))
        self.mapper.add(c)
        self.assertTrue(self.mapper.exist(c))

    def test_fetch(self):
        c = Chunk()
        c.chunk_name = 'xxx'
        c.signature = 'hash'
        c.storage = 'baidu'
        self.mapper.add(c)
        chunk_list = self.mapper.fetch('xxx')
        self.assertEqual(1, len(chunk_list))
        ck = chunk_list[0]
        self.assertEqual(c.chunk_name, ck.chunk_name)
        self.assertEqual(c.storage, ck.storage)
        self.assertEqual(c.signature, ck.signature)

        c.storage = 'local'
        self.mapper.add(c)
        chunk_list = self.mapper.fetch('xxx')
        self.assertEqual(2, len(chunk_list))

        chunk_list = self.mapper.fetch('xxx_notexist')
        self.assertEqual(0, len(chunk_list))

        ck = self.mapper.fetchone('xxx', 'local')
        self.assertEqual(c.chunk_name, ck.chunk_name)
        self.assertEqual('local', ck.storage)
        self.assertEqual(c.signature, ck.signature)

    def test_delete(self):
        c = Chunk()
        c.chunk_name = 'xxx'
        c.signature = 'hash'
        c.storage = 'baidu'
        self.mapper.add(c)
        self.mapper.delete(c)
        self.assertFalse(self.mapper.exist(c))

    def test_update_status(self):
        c = Chunk()
        c.chunk_name = 'foo'
        c.signature = 'hash'
        c.storage = 'chunk_server_0'
        c.status = 'uploading'
        self.mapper.add(c)
        ck = self.mapper.fetchone('foo', 'chunk_server_0')
        self.assertEqual('uploading', ck.status)
        c.status = 'success'
        self.mapper.update_status(c)
        ck = self.mapper.fetchone('foo', 'chunk_server_0')
        self.assertEqual('success', ck.status)




