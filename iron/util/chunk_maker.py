#!/usr/bin/env python3

import os
import shutil
from iron.config import Config
from iron.util.log import get_logger


class ChunkMaker:
    def __init__(self, config: Config) -> None:
        self.log = get_logger(__name__)
        self.config = config
        self.init()

    def init(self) -> None:
        if not os.path.exists(self.config.chunk_maker_workspace):
            os.makedirs(self.config.chunk_maker_workspace)

    def make(self, path: str, basename: str) -> list[str]:
        if not os.path.exists(path):
            self.log.error(f'{path} is not exist.')
            return None

        i, chunks = 0, []
        with open(path, 'rb') as inf:
            chunk = inf.read(self.config.DEFAULT_CHUNK_SIZE)
            while chunk:
                chunk_name = f'{basename}.{i}'
                chunk_path = os.path.join(
                    self.config.chunk_maker_workspace, chunk_name)
                with open(chunk_path, 'wb') as outf:
                    outf.write(chunk)

                chunks.append(chunk_name)
                i += 1
                chunk = inf.read(self.config.DEFAULT_CHUNK_SIZE)
        return chunks

    def combine(self, path: str, chunks: list[str]) -> None:
        # chunk.0, chunk.1, ... , chunk.n
        chunks.sort(key=lambda element: int(element.split('.')[-1]))
        open(path, 'wb').close()
        with open(path, 'ab') as outf:
            for chunk_name in chunks:
                chunk_path = os.path.join(
                    self.config.chunk_maker_workspace, chunk_name)
                with open(chunk_path, 'rb') as inf:
                    chunk = inf.read(self.config.DEFAULT_CHUNK_SIZE)
                    outf.write(chunk)

    def clear(self) -> None:
        shutil.rmtree(self.config.chunk_maker_workspace)
        self.init()
