#!/usr/bin/env python3

import config
import baidupcsapi


class ChunkService(object):
    def __init__(self, source):
        self.source = source

    def put(self, chunk_path):
        pass

    def get(self, file_path, chunk_info):
        pass

    def quota(self):
        return 0


class BaiduService(ChunkService):
    def __init__(self):
        super().__init__(config.BAIDU)
        self.pcs = self.login(config.BAIDU_USR_NAME)
        self.__check_data_path__()

    def login(self, username):
        password = input('input password of {} >>'.format(username))
        return baidupcsapi.PCS(username, password)

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


class ChunkServiceFactory(object):
    @staticmethod
    def get_service(service_provider):
        if config.BAIDU == service_provider:
            return BaiduService()


if '__main__' == __name__:
    service = ChunkServiceFactory.get_service(config.BAIDU)
    quota = service.quota()
    print(quota)
