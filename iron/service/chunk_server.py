#!/usr/bin/env python3


class ChunkServer:
    def __init__(self, name: str, workspace: str) -> None:
        self.workspace = workspace
        self.name = name

    def get(self, chunk: str) -> bool:
        return None

    def put(self, path: str) -> bool:
        return False

    def quota(self) -> int:
        return 0
