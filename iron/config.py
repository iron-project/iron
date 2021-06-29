#!/usr/bin/env python3


class Config:
    def __init__(self, *args, **kwargs):
        self.DEFAULT_CHUNK_SIZE = 1 * 1024 * 1024  # 1M

        self.chunk_maker_workspace = '/tmp/iron/chunks'
        self.iron_upload = '/tmp/iron/upload'
        self.iron_download = '/tmp/iron/download'

        # Baidu
        self.BAIDU = 'baidu'
        self.BAIDU_NO_ERR = 0
        self.BAIDU_DIR_NOT_EXIST = -9
        self.BAIDU_USR_NAME = 'xxx'
        self.BAIDU_USR_PASSWD = 'xxx'
        self.BAIDU_DL_CHUNK_SIZE = 1024  # 1024Bytes
