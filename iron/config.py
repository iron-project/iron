#!/usr/bin/env python3

import configparser
config = configparser.ConfigParser()
config.read('iron.ini')
config.sections()

# Const Variabes

XXHASH_CHUNK_SIZE = 2 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024  # 4M
TMP_PATH = config['Default']['TmpPath']
DATA_PATH = config['Default']['DataPath']

# Baidu
BAIDU = 'baidu'
BAIDU_NO_ERR = 0
BAIDU_DIR_NOT_EXIST = -9
BAIDU_USR_NAME = config['Baidu']['User']
BAIDU_USR_PASSWD = config['Baidu']['Password']
BAIDU_DL_CHUNK_SIZE = 1024

# SQL template

class SQLTemplate(object):
    def __init__(self):
        self.SQLITE_PATH = 'sqlite://'
        self.TABLE_SCHEMA = 'schema.sql'
        self.SETDIR = 'UPDATE directory SET sub_dir = :sub_dir, sub_file = :sub_file WHERE dir_path = :dir_path'
        self.PUTDIR = 'INSERT INTO directory (dir_path, dir_name, sub_dir, sub_file) VALUES (:dir_path, :dir_name, :sub_dir, :sub_file)'
        self.PUTFILE = 'INSERT INTO file (file_path, file_name, file_hash, sub_chunk) VALUES (:file_path, :file_name, :file_hash, :sub_chunk)'
        self.PUTCHUNK = 'INSERT INTO chunk (chunk_name, chunk_source, chunk_hash) VALUES (:chunk_name, :chunk_source, :chunk_hash)'
        self.GETDIR = 'SELECT * FROM directory WHERE dir_path = :dir_path'
        self.GETFILE = 'SELECT * FROM file WHERE file_path = :file_path'
        self.RMCHUNK = 'DELETE FROM chunk WHERE chunk_name = :chunk_name'
        self.RMDIR = 'DELETE FROM directory WHERE dir_path = :dir_path'
        self.RMFILE = 'DELETE FROM file WHERE file_path = :file_path'

template = SQLTemplate()
