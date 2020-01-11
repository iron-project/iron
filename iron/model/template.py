#!/usr/bin/env python3

class SQLTemplate(object):
    def __init__(self):
        self.GETDIR = 'SELECT * FROM directory WHERE id = :id'
        self.PUTDIR = 'INSERT INTO directory (id, dir_name, directories, files) VALUES (:id, :dir_name, :directories, :files)'
        self.SETDIR = 'UPDATE directory SET directories = :directories, files = :files WHERE id = :id'
        self.RMDIR = 'DELETE FROM directory WHERE id = :id'

        self.GETFILE = 'SELECT * FROM file WHERE id = :id'
        self.PUTFILE = 'INSERT INTO file (id, file_name, file_hash, chunks) VALUES (:id, :file_name, :file_hash, :chunks)'
        self.RMFILE = 'DELETE FROM file WHERE id = :id'

        self.GETCHUNK_BYNAME = 'SELECT * FROM chunk WHERE chunk_name = :chunk_name'
        self.GETCHUNK_BYPKEY = 'SELECT * FROM chunk WHERE chunk_name = :chunk_name AND storage = :storage'
        self.PUTCHUNK = 'INSERT INTO chunk (chunk_name, storage, signature, status) VALUES (:chunk_name, :storage, :signature, :status)'
        self.RMCHUNK_BYNAME = 'DELETE FROM chunk WHERE chunk_name = :chunk_name'
        self.RMCHUNK_BYPKEY= 'DELETE FROM chunk WHERE chunk_name = :chunk_name AND storage = :storage'
        self.UPDATE_CHUNK_STATUS = 'UPDATE chunk SET status = :status WHERE chunk_name = :chunk_name AND storage = :storage'
