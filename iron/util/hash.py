#!/usr/bin/env python3

import xxhash

XXHASH_CHUNK_SIZE: int = 512 * 1024  # 512K


class Hash:
    @staticmethod
    def str_hash(s: str) -> str:
        x = xxhash.xxh64()
        x.update(s.encode())
        return x.hexdigest()

    @staticmethod
    def file_hash(path: str) -> str:
        x = xxhash.xxh64()
        with open(path, 'rb') as inf:
            chunk = inf.read(XXHASH_CHUNK_SIZE)
            while chunk:
                x.update(chunk)
                chunk = inf.read(XXHASH_CHUNK_SIZE)
        return x.hexdigest()
