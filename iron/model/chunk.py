#!/usr/bin/env python3

from template import SQLTemplate

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

    def is_exist(self, c):
        record = self.connect.query(self.template.GETCHUNK_BYPKEY,
                                    chunk_name=c.chunk_name,
                                    storage=c.storage).as_dict()
        return len(record)

    def fetch(self, chunk_name, storage):
        record = self.connect.query(self.template.GETCHUNK_BYPKEY,
                                    chunk_name=chunk_name,
                                    storage=storage).as_dict()
        chunk = Chunk()
        if len(record) > 0:
            chunk.load(record[0])
        return chunk

    def fetch(self, chunk_name):
        record = self.connect.query(self.template.GETCHUNK_BYNAME,
                                    chunk_name=chunk_name).as_dict()
        chunk_list = []
        for x in record:
            chunk = Chunk()
            chunk.load(x)
            chunk_list.append(chunk)
        return chunk_list

    def add(self, c):
        self.connect.query(self.template.PUTCHUNK,
                           chunk_name=c.chunk_name,
                           storage=c.storage).as_dict()

    def delete(self, c):
        self.connect.query(self.template.RMCHUNK_BYPKEY,
                           chunk_name=c.chunk_name,
                           storage=c.storage)
