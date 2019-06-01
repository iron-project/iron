#!/usr/bin/env python3

import pysnooper
from iron.model.template import SQLTemplate

class Chunk(object):
    def __init__(self):
        self.chunk_name = ''
        self.storage = ''
        self.chunk_hash = ''

    def load(self, database_data):
        self.chunk_name = database_data['chunk_name']
        self.storage = database_data['storage']
        self.chunk_hash = database_data['chunk_hash']

class ChunkMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def create(self, chunk_name, storage, chunk_hash):
        c = Chunk()
        c.chunk_name = chunk_name
        c.chunk_hash = chunk_hash
        c.storage = storage
        return c

    # @pysnooper.snoop()
    def exist(self, c):
        record = self.connect.query(
            self.template.GETCHUNK_BYPKEY,
            chunk_name=c.chunk_name,
            storage=c.storage).as_dict()
        return len(record) > 0

    # @pysnooper.snoop()
    def fetchone(self, chunk_name, storage):
        record = self.connect.query(
            self.template.GETCHUNK_BYPKEY,
            chunk_name=chunk_name,
            storage=storage).as_dict()
        if len(record) > 0:
            chunk = Chunk()
            chunk.load(record[0])
            return chunk
        return None

    # @pysnooper.snoop()
    def fetch(self, chunk_name):
        record = self.connect.query(
            self.template.GETCHUNK_BYNAME,
            chunk_name=chunk_name).as_dict()
        chunks = []
        for x in record:
            chunk = Chunk()
            chunk.load(x)
            chunks.append(chunk)
        return chunks

    # @pysnooper.snoop()
    def add(self, c):
        self.connect.query(
            self.template.PUTCHUNK,
            chunk_name=c.chunk_name,
            storage=c.storage,
            chunk_hash=c.chunk_hash)

    # @pysnooper.snoop()
    def deleteone(self, c):
        self.connect.query(
            self.template.RMCHUNK_BYPKEY,
            chunk_name=c.chunk_name,
            storage=c.storage)

    def delete(self, c):
        self.connect.query(
            self.template.RMCHUNK_BYNAME,
            chunk_name=c.chunk_name)
