#!/usr/bin/env python3

import os, math
import requests
import shutil
import pysnooper

from iron.service.config_service import ConfigService


class ChunkServiceMaster(object):
    def __init__(self):
        self.config = ConfigService()

    def chunks_put(self, chunks_info):
        print(chunks_info)

    def chunks_get(self, chunks_info, target_dir):
        print(chunks_info)
        for x in chunks_info['chunk_set']:
            src = os.path.join(self.config.TMP_PATH, x)
            dst = os.path.join(target_dir, x)
            shutil.copyfile(src, dst)

    def chunks_status(self, chunks_info):
        print(chunks_info)
