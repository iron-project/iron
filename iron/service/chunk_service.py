#!/usr/bin/env python3

import os

from iron.model import db
from iron.model.file import File
from iron.model.chunk import ChunkOperator
from iron.service.chunk_server import ChunkServer


class ChunkService:
    def __init__(self) -> None:
        self.chunk_servers: dict[str, ChunkServer] = {}
        self.idx: int = 0
        self.replica: int = 3

    def register_chunk_server(self, chunk_server: ChunkServer) -> bool:
        self.chunk_servers[chunk_server.name] = chunk_server

    def select_chunk_server(self, replica: int) -> list[ChunkServer]:
        server = list(self.chunk_servers.values())
        select = [server[(i + self.idx) % len(server)]
                  for i in range(0, replica)]
        self.idx += replica
        return select

    def put(self, f: File, path: str) -> bool:
        for server in self.select_chunk_server(self.replica):
            for chunk_name in f.chunks:
                if server.put(os.path.join(path, chunk_name)):
                    chunk = ChunkOperator.create(chunk_name)
                    chunk.server = server.name
                    db.session.add(chunk)

        db.session.commit()
        return True

    def get(self, f: File) -> list[str]:
        chunks_path = []
        for chunk_name in f.chunks:
            for chunk in ChunkOperator.gets(chunk_name):
                path = self.chunk_servers[chunk.server].get(chunk_name)
                if path and len(path):
                    chunks_path.append(path)
                    break

        return chunks_path
