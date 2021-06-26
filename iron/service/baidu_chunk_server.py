#!/usr/bin/env python3

import os
import requests

from iron.config import Config
from iron.service.baidupcsapi import baidupcsapi
from iron.service.chunk_server import ChunkServer


class Progressbar:
    def __init__(self, title):
        self.title = title
        print('{} ...'.format(self.title))

    def __call__(self, *args, **kwargs):
        if kwargs['progress'] >= kwargs['size']:
            print('{} done'.format(self.title))


class BaiduChunkServer(ChunkServer):
    def __init__(self, name: str, workspace: str) -> None:
        super().__init__(name, workspace)
        import urllib3
        urllib3.disable_warnings()
        self.config = Config()
        super().__init__(self.config.BAIDU)
        self.pcs = baidupcsapi.PCS(
            self.config.BAIDU_USR_NAME, self.config.BAIDU_USR_PASSWD)
        self._check_data_path()

    def __del__(self):
        self.pcs.session.close()

    def quota(self) -> int:
        r = self.pcs.quota()
        if 200 != r.status_code:
            print('failed to request baidu service. [status code {}]'.format(
                r.status_code))
            return 0
        json_data = r.json()
        if self.config.BAIDU_NO_ERR == json_data['errno']:
            return json_data['total'] - json_data['used']
        else:
            print('unknow error from baidu service [errno {}]'.format(
                json_data['errno']))
            return 0

    def _check_data_path(self):
        r = self.pcs.list_files(self.config.DATA_PATH)
        if 200 != r.status_code:
            print('failed to check data path exist. [status code {}]'.format(
                r.status_code))
            return False
        json_data = r.json()
        if self.config.BAIDU_DIR_NOT_EXIST == json_data['errno']:
            return self._mkdir(self.config.DATA_PATH)
        return True

    def _mkdir(self, dir_path):
        r = self.pcs.mkdir(dir_path)
        if 200 != r.status_code:
            print('failed to create data path. [status code {}]'.format(
                r.status_code))
            return False
        json_data = r.json()
        if self.config.BAIDU_NO_ERR != json_data['errno']:
            return False
        return True

    def exist(self, chunk_name):
        r = self.pcs.meta(os.path.join(self.config.DATA_PATH, chunk_name))
        if 200 != r.status_code:
            print('failed to fetch chunk meta info. [{}]'.format(chunk_name))
            return False
        json_data = r.json()
        if self.config.BAIDU_NO_ERR != json_data['errno']:
            return False
        return True

    def put(self, chunk_path: str) -> bool:
        if not os.path.isfile(chunk_path):
            return False
        _, chunk_name = os.path.split(chunk_path)
        if self.exist(chunk_name):
            print('chunk [{}] is exist, skip upload it.'.format(chunk_name))
            return True
        # TODO: encrypt chunk
        with open(chunk_path, 'rb') as infile:
            bar = Progressbar('Upload {}'.format(chunk_name))
            r = self.pcs.upload(self.config.DATA_PATH, file_handler=infile,
                                filename=chunk_name, callback=bar)
            if 200 != r.status_code:
                print('failed to upload chunk {} [status code {}]'.format(
                    chunk_name, r.status_code))
                return False
            json_data = r.json()
            expect_path = os.path.join(self.config.DATA_PATH, chunk_name)
            if json_data['path'] != expect_path:
                print('it is same to fail to upload chunk {}'.format(chunk_name))
                return False
        return True

    def get(self, chunk_name: str) -> str:
        if not self.exist(chunk_name):
            print(
                'failed to get chunk info, [{}] is not exist'.format(chunk_name))
            return False
        url = os.path.join(self.config.DATA_PATH, chunk_name)
        dlink = self.pcs.download_url(url)
        if not len(dlink) > 0:
            print('failed to get chunk info, chunkname {}'.format(chunk_name))
            return False

        r = requests.get(dlink[0], stream=True)
        if 200 != r.status_code:
            print('faild to download chunk {} [status_code {}, message {}]'.format(
                chunk_name, r.status_code, r.content))
            return False

        chunk_file = os.path.join(self.workspace, chunk_name)
        # Total size in bytes.
        wrote = 0
        total_size = int(r.headers.get('Content-Length', 0))
        with open(chunk_file, 'wb') as outfile:
            bar = Progressbar('Download {}'.format(chunk_name))
            for chunk in r.iter_content(self.config.BAIDU_DL_CHUNK_SIZE):
                if not chunk:
                    break
                outfile.write(chunk)
                wrote += len(chunk)
                bar(size=total_size, progress=wrote)

        if total_size != 0 and wrote != total_size:
            print('oops, file download failed. {}'.format(chunk_name))
        return True
