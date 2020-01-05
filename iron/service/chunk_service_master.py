#!/usr/bin/env python3

import os, math
import requests
import shutil
import random
import pysnooper

import iron.util.random_util as ru
from iron.service.config_service import ConfigService
from iron.util.task_executor import TaskExecutorService, Task


class ChunkServiceMaster:
    def __init__(self, chunks_path):
        self.chunks_path = chunks_path
        self.load_slave()
        self.task_pool = TaskExecutorService(4)

    def __del__(self):
        self.task_pool.shutdown()

    def load_slave(self):
        self.slave = (
            ('chunk_server_1',  'http://127.0.0.1:10011'),
            ('chunk_server_2',  'http://127.0.0.1:10012'),
            ('chunk_server_3',  'http://127.0.0.1:10013'),
        )
        self.replica = 2

    def select_chunk_server(self):
        seq = ru.generate_n(self.replica, 0, len(self.slave))
        return [self.slave[i] for i in seq]

    def chunk_server_put(self, thread_local_data, chunk_server, chunk_name):
        uri = '{}/v1/chunks?name={}'.format(chunk_server, chunk_name)
          with open(os.path.join(self.chunks_path, chunk_name), 'rb') as fd:
              r = requests.put(uri, files={'file': fd})
              print(r.status_code, r.text)

    def chunks_put(self, chunks_info):
        for server in self.select_chunk_server():
          for chunk in chunks_info['chunk_set']:
              task_id = ru.generate(0, 8)
              task = Task(task_id, self.chunk_server_put, server[1] chunk)
              self.task_pool.submit(task)

    def chunk_server_get(self, thread_local_data, chunk_server, chunk_name, target_dir):
        pass

    def chunks_get(self, chunks_info, target_dir):
        print(chunks_info)
        for x in chunks_info['chunk_set']:
            src = os.path.join(self.config.TMP_PATH, x)
            dst = os.path.join(target_dir, x)
            shutil.copyfile(src, dst)

    def chunks_status(self, chunks_info):
        print(chunks_info)
