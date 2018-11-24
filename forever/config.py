#!/usr/bin/env python3

# Const Variabes

XXHASH_CHUNK_SIZE = 2 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 64 * 1024 * 1024  # 64M
SQLITE_PATH = 'sqlite://'
TABLE_SCHEMA = 'schema.sql'
TMP_PATH = '/tmp/forever'

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
SQL_LSFILE = '''
SELECT * FROM file WHERE file_path = :file_path
'''
