#!/usr/bin/env python3

import os
import configparser

class ConfigService(object):
    def __init__(self, **kws):
        # TODO: parse config path from commandline
        self.CONFIG_PATH = './iron/resource'
        self.parse(**kws)

        # Const Variabes
        self.XXHASH_CHUNK_SIZE = 2 * 1024 * 1024
        self.DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024  # 4M
        self.TMP_PATH = self.parser['Default']['TmpPath']
        self.DATA_PATH = self.parser['Default']['DataPath']

        # Baidu
        self.BAIDU = 'baidu'
        self.BAIDU_NO_ERR = 0
        self.BAIDU_DIR_NOT_EXIST = -9
        self.BAIDU_USR_NAME = self.parser['Baidu']['User']
        self.BAIDU_USR_PASSWD = self.parser['Baidu']['Password']
        self.BAIDU_DL_CHUNK_SIZE = 1024

        # SQL
        self.SQLITE_URI = 'sqlite://'
        self.TABLE_SCHEMA = os.path.join(self.CONFIG_PATH, 'table_schema.sql')

    def parse(self, **kw):
        self.parser = configparser.ConfigParser()
        self.parser.read(os.path.join(self.CONFIG_PATH, 'iron.conf'))
        self.parser.sections()


