#!/usr/bin/env python3

import os, math
import config
import requests
from tqdm import tqdm as progressbar
from baidupcsapi import baidupcsapi


class Progressbar(object):
    def __init__(self, title):
        self.title = title
        self.first = True
        self.last_progress = 0

    def __call__(self, *args, **kwargs):
        if self.first:
            self.first = False
            self.bar = progressbar(
                total=kwargs['size'], desc=self.title, leave=False, ascii='#')

        if kwargs['progress'] <= kwargs['size']:
            self.bar.update(kwargs['progress'] - self.last_progress)
            self.last_progress = kwargs['progress']

    def close(self):
        self.bar.close()


class ChunkService(object):
    def __init__(self, source):
        self.source = source

    def put(self, chunk_path, chunk_name):
        return False

    def get(self, local_path, chunk_name):
        return False

    def quota(self):
        return 0


class BaiduService(ChunkService):
    def __init__(self):
        super().__init__(config.BAIDU)
        self.pcs = baidupcsapi.PCS(
            config.BAIDU_USR_NAME, config.BAIDU_USR_PASSWD)
        self.__check_data_path__()

    def quota(self):
        r = self.pcs.quota()
        if 200 != r.status_code:
            print('failed to request baidu service. [status code {}]'.format(
                r.status_code))
            return 0
        json_data = r.json()
        if config.BAIDU_NO_ERR == json_data['errno']:
            return json_data['total'] - json_data['used']
        else:
            print('unknow error from baidu service [errno {}]'.format(
                json_data['errno']))
            return 0

    def __check_data_path__(self):
        r = self.pcs.list_files(config.DATA_PATH)
        if 200 != r.status_code:
            print('failed to check data path exist. [status code {}]'.format(
                r.status_code))
            return False
        json_data = r.json()
        if config.BAIDU_DIR_NOT_EXIST == json_data['errno']:
            return self.__mkdir__(config.DATA_PATH)
        return True

    def __mkdir__(self, dir_path):
        r = self.pcs.mkdir(dir_path)
        if 200 != r.status_code:
            print('failed to create data path. [status code {}]'.format(
                r.status_code))
            return False
        json_data = r.json()
        if config.BAIDU_NO_ERR != json_data['errno']:
            return False
        return True

    def exist(self, chunk_name):
        r = self.pcs.meta(os.path.join(config.DATA_PATH, chunk_name))
        if 200 != r.status_code:
            print('failed to fetch chunk meta info. [{}]'.format(chunk_name))
            return False
        json_data = r.json()
        if config.BAIDU_NO_ERR != json_data['errno']:
            return False
        return True

    def put(self, chunk_path, chunk_name):
        if not os.path.isfile(chunk_path):
            return False
        if self.exist(chunk_name):
            return True
        # TODO: encrypt chunk
        with open(chunk_path, 'rb') as infile:
            bar = Progressbar('Upload [{}]'.format(chunk_name))
            r = self.pcs.upload(config.DATA_PATH, file_handler=infile,
                                filename=chunk_name, callback=bar)
            bar.close()
            if 200 != r.status_code:
                print('failed to upload chunk {} [status code {}]'.format(
                    chunk_name, r.status_code))
                return False
            json_data = r.json()
            expect_path = os.path.join(config.DATA_PATH, chunk_name)
            if json_data['path'] != expect_path:
                print('it is same to fail to upload chunk {}'.format(chunk_name))
                return False
        return True

    def get(self, local_path, chunk_name):
        if not self.exist(chunk_name):
            return False
        url = os.path.join(config.DATA_PATH, chunk_name)
        dlink = self.pcs.download_url(url)
        if not len(dlink) > 0:
            print('failed to get chunk info, chunkname {}'.format(chunk_name))
            return False

        r = requests.get(dlink[0], stream=True)
        if 200 != r.status_code:
            print('faild to download chunk {} [status_code {}, message {}]'.format(
                chunk_name, r.status_code, r.content))
            return False

        chunk_file = os.path.join(local_path, chunk_name)
        # Total size in bytes.
        wrote = 0
        total_size = int(r.headers.get('Content-Length', 0))
        with open(chunk_file, 'wb') as outfile:
            ceil = math.ceil(total_size / config.BAIDU_DL_CHUNK_SIZE)
            desc = 'Download {}'.format(chunk_name)
            bar = progressbar(r.iter_content(config.BAIDU_DL_CHUNK_SIZE),
                              total=ceil, unit='KB', ascii='#', desc=desc)
            for chunk in bar:
                if not chunk:
                    break
                outfile.write(chunk)
                wrote += len(chunk)
        if total_size != 0 and wrote != total_size:
            print('oops, file download failed. {}'.format(chunk_name))
        return True


class ChunkServiceFactory(object):
    @staticmethod
    def create(service):
        if config.BAIDU == service:
            return BaiduService()


if '__main__' == __name__:
    service = ChunkServiceFactory.create(config.BAIDU)
    # service.put('../testdata/bin.tar.xz', 'data.txz')
    service.get('.', 'not exist')
    service.get('.', 'c45dcecfb262d59f_61e4adead7c1fc24_1')
