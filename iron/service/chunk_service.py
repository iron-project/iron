#!/usr/bin/env python3

import os
from typing import Any
from concurrent.futures._base import Future
from concurrent.futures.thread import ThreadPoolExecutor

from iron.model import db
from iron.model.file import File
from iron.model.chunk import ChunkOperator
from iron.util.log import get_logger
from iron.service.chunk_server import ChunkServer


class ChunkService:
    def __init__(self) -> None:
        self.log = get_logger(__name__)
        self.chunk_servers: dict[str, ChunkServer] = {}
        self.idx: int = 0
        self.replica: int = 3
        self.executor = ThreadPoolExecutor(12)

    def register_chunk_server(self, chunk_server: ChunkServer) -> bool:
        self.chunk_servers[chunk_server.name] = chunk_server

    def select_chunk_server(self, replica: int) -> list[ChunkServer]:
        server = list(self.chunk_servers.values())
        select = [
            server[(i + self.idx) % len(server)] for i in range(0, replica)
        ]
        self.idx += replica
        return select

    def put(self, f: File, path: str) -> bool:
        if len(self.chunk_servers) < self.replica:
            self.log.error(f'chunk server less than replica {self.replica}')
            return False
        defer = list()
        futures = list()
        for server in self.select_chunk_server(self.replica):
            for chunk_name in f.chunks:
                futures.append(self.executor.submit(
                    self._put, defer, chunk_name, server, path))
        r = self.when_all(futures)
        if r:
            self.apply(defer)
        return r

    def apply(self, defer: list) -> Any:
        return [f() for f in defer]

    def get(self, f: File) -> bool:
        futures = [self.executor.submit(self._get, name) for name in f.chunks]
        return self.when_all(futures)

    def _add_chunk(self, chunk_name: str, server: ChunkServer) -> None:
        chunk = ChunkOperator.create(chunk_name)
        chunk.server = server.name
        db.session.add(chunk)
        db.session.commit()

    def _put(self, defer: list, chunk_name: str, server: ChunkServer, path: str) -> bool:
        if server.put(os.path.join(path, chunk_name)):
            defer.append(lambda: self._add_chunk(chunk_name, server))
            return True
        self.log.error(f'fail to put chunk {chunk_name} to {server.name}')
        return False

    def _get(self, chunk_name: str) -> bool:
        success = False
        for chunk in ChunkOperator.gets(chunk_name):
            if self.chunk_servers[chunk.server].get(chunk_name):
                success = True
                break
            self.log.warning(
                f'get chunk {chunk.name} from {chunk.server} fail')
        if not success:
            self.log.error(f'fail to get chunk {chunk_name}')
        return success

    def when_all(self, futures: list[Future]) -> bool:
        for fut in futures:
            try:
                if not fut.result():
                    return False
            except Exception as e:
                self.log.error(e)
                return False
        return True
