#!/usr/bin/env python3

# Const Variabes

XXHASH_CHUNK_SIZE = 2 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 64M
SQLITE_PATH = 'sqlite://'
TABLE_SCHEMA = 'schema.sql'
TMP_PATH = '/tmp/forever'

# Cloud Disk
DATA_PATH = '/forever_data'
BAIDU = 'baidu'
BAIDU_USR_NAME = 'C语言大菜'
BAIDU_DIR_NOT_EXIST = -9
BAIDU_NO_ERR = 0

# SQL template

SQL_MKDIR = '''
INSERT INTO directory (dir_path, dir_name, sub_dir, sub_file) VALUES (:dir_path, :dir_name, :sub_dir, :sub_file)
'''
SQL_LSDIR = '''
SELECT * FROM directory WHERE dir_path = :dir_path
'''
SQL_UPDATE_DIR = '''
UPDATE directory SET sub_dir = :sub_dir, sub_file = :sub_file WHERE dir_path = :dir_path
'''
SQL_RMDIR = '''
DELETE FROM directory WHERE dir_path = :dir_path
'''
SQL_GETFILE = '''
SELECT * FROM file WHERE file_path = :file_path
'''
SQL_RMFILE = '''
DELETE FROM file WHERE file_path = :file_path
'''
SQL_PUTFILE = '''
INSERT INTO file (file_path, file_name, file_hash, sub_chunk) VALUES (:file_path, :file_name, :file_hash, :sub_chunk)
'''
SQL_PUTCHUNK = '''
INSERT INTO chunk (chunk_id, chunk_source, chunk_hash) VALUES (:chunk_id, :chunk_source, :chunk_hash)
'''
SQL_RMCHUNK = '''
DELETE FROM chunk WHERE chunk_id = :chunk_id
'''
