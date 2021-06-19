#!/usr/bin/env python3


class ConfigService(object):
    def __init__(self, *args, **kwargs):
        # Const Variabes
        self.XXHASH_CHUNK_SIZE = 512 * 1024  # 512K
        self.DEFAULT_CHUNK_SIZE = 1 * 1024 * 1024  # 1M
        self.TMP_PATH = '/tmp'
        self.DATA_PATH = 'tmp'

        # Baidu
        self.BAIDU = 'baidu'
        self.BAIDU_NO_ERR = 0
        self.BAIDU_DIR_NOT_EXIST = -9
        self.BAIDU_USR_NAME = 'xxx'
        self.BAIDU_USR_PASSWD = 'xxx'
        self.BAIDU_DL_CHUNK_SIZE = 1024  # 1024Bytes
