#!/usr/bin/env python3

import os, math
import requests
import shutil
import random
import pysnooper

from iron.util.random_util import generate_n
from iron.util.task_executor import TaskExecutorService, Task
from iron.util.file_operator import FileUtil
from iron.model.chunk import Chunk, ChunkMapper
# from iron.service.config_service import ConfigService


class ChunkServiceMaster:
    def __init__(self, chunks_path, chunk_mapper, file_operator):
        self.chunks_path = chunks_path
        self.chunk_mapper = chunk_mapper
        self.file_operator = file_operator
        self.task_pool = TaskExecutorService(4)
        self.load_slave()

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
        seq = generate_n(self.replica, 0, len(self.slave))
        return [self.slave[i] for i in seq]

    def chunk_server_put(self, thread_local_data, chunk_server, chunk_name):
        uri = '{}/v1/chunks?name={}'.format(chunk_server, chunk_name)
        chunk = Chunk()
        chunk.load({'chunk_name': chunk_name,
                    'storage': chunk_server,
                    'status': 'waiting',
                    'signature': self.file_operator.chunk_signature(chunk_name)})
        self.chunk_mapper.add(chunk)
        with open(os.path.join(self.chunks_path, chunk_name), 'rb') as fd:
            r = requests.put(uri, files={'file': fd})
            if r.status_code == 200:
                chunk.status = 'success'
            else:
                chunk.status = 'failed'
                print(r.status_code, r.text)

            self.chunk_mapper.update_status(chunk)

    def chunks_put(self, chunks_info):
        for name, server in self.select_chunk_server():
          for chunk in chunks_info['chunk_set']:
              task = Task(self.chunk_server_put, server, chunk)
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
