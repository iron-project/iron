#!/usr/bin/env python3

import os
import requests

from iron.util.log import get_logger
from iron.service.chunk_server import ChunkServer


class HttpChunkServer(ChunkServer):
    def __init__(self, name: str, workspace: str, endpoint: str) -> None:
        super().__init__(name, workspace)
        self.log = get_logger(__name__)
        self.endpoint = endpoint

    def get(self, chunk_name: str) -> bool:
        path = os.path.join(self.workspace, chunk_name)
        uri = f'{self.endpoint}/v1/chunks?name={chunk_name}'
        response = requests.get(uri)
        if not self._validate(response):
            return False
        with open(path, 'wb') as f:
            f.write(response.content)
        self.log.info(f'get chunk {chunk_name} from {self.name}')
        return True

    def put(self, path: str) -> bool:
        chunk_name = os.path.basename(path)
        uri = f'{self.endpoint}/v1/chunks?name={chunk_name}'
        with open(path, 'rb') as f:
            files = {'file': f}
            response = requests.put(uri, files=files)
            if not self._validate(response):
                return False
        self.log.info(f'put chunk {path} to {self.name}')
        return True

    def _validate(self, r: requests.Response) -> bool:
        if 200 != r.status_code:
            self.log.info(
                f'fail to request {r.request.url}, status code {r.status_code}')
            return False
        self.log.info(r.headers.get('content-type'))
        return True

    def quota(self) -> int:
        return super().quota()
