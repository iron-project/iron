#!/usr/bin/env python3

import pysnooper
from iron.model.template import SQLTemplate

class Chunk(object):
    def __init__(self):
        self.chunk_name = ''
        self.storage = ''
        self.signature = ''
        self.status = 'new'

    def load(self, database_data):
        self.chunk_name = database_data['chunk_name']
        self.storage = database_data['storage']
        self.signature = database_data['signature']
        self.status = database_data['status']

class ChunkMapper(object):
    def __init__(self, connect):
        self.connect = connect
        self.template = SQLTemplate()

    def create(self, chunk_name, storage, signature):
        c = Chunk()
        c.chunk_name = chunk_name
        c.signature = signature
        c.storage = storage
        return c

    # @pysnooper.snoop()
    def exist(self, c):
        record = self.connect.connection().query(
            self.template.GETCHUNK_BYPKEY,
            chunk_name=c.chunk_name,
            storage=c.storage).as_dict()
        return len(record) > 0

    # @pysnooper.snoop()
    def fetchone(self, chunk_name, storage):
        record = self.connect.connection().query(
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
        record = self.connect.connection().query(
            self.template.GETCHUNK_BYNAME,
            chunk_name=chunk_name).as_dict()
        chunks = []
        for x in record:
            chunk = Chunk()
            chunk.load(x)
            chunks.append(chunk)
        return chunks

    def update_status(self, c):
        self.connect.connection().query(
            self.template.UPDATE_CHUNK_STATUS,
            chunk_name=c.chunk_name,
            storage=c.storage,
            status=c.status)

    # @pysnooper.snoop()
    def add(self, c):
        self.connect.connection().query(
            self.template.PUTCHUNK,
            chunk_name=c.chunk_name,
            storage=c.storage,
            signature=c.signature,
            status=c.status)

    # @pysnooper.snoop()
    def deleteone(self, c):
        self.connect.connection().query(
            self.template.RMCHUNK_BYPKEY,
            chunk_name=c.chunk_name,
            storage=c.storage)

    def delete(self, c):
        self.connect.connection().query(
            self.template.RMCHUNK_BYNAME,
            chunk_name=c.chunk_name)
