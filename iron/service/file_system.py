#!/usr/bin/env python3

import os
from iron.util.hash import Hash
from iron.config import Config
from iron.util.chunk_maker import ChunkMaker
from iron.util.log import get_logger
from iron.model.directory import Directory, DirectoryOperator
from iron.model.file import File, FileOperator
from iron.service.chunk_service import ChunkService


class FileSystemService:
    def __init__(self, db):
        self.log = get_logger('fs')
        self.db = db
        self.chunk_service = ChunkService()
        self.set_config(Config())

    def set_config(self, config: Config) -> None:
        self.config = config
        self.maker = ChunkMaker(self.config)

    def mkdir(self, path: str) -> bool:
        d = DirectoryOperator.get(path)
        if d:
            self.log.warning(f'{path} already exist.')
            return True

        d = DirectoryOperator.create(path)
        if path == '/':
            self.db.session.add(d)
            self.db.session.commit()
            return True

        pardir = DirectoryOperator.pardir(d)
        p = DirectoryOperator.get(pardir)
        if not p:
            self.log.error(f'{pardir} not exist.')
            return False

        self.db.session.add(d)
        p.dirs.append(d.name)
        self.db.session.commit()
        return True

    def lsdir(self, path: str) -> Directory:
        d = DirectoryOperator.get(path)
        if not d:
            self.log.error(f'{path} not exist.')
            return None
        self.log.info(DirectoryOperator.marshal(d))
        return d

    def rmdir(self, path: str) -> bool:
        d = DirectoryOperator.get(path)
        if not d:
            self.log.warning(f'{path} not exist.')
            return True

        if len(d.files) > 0 or len(d.dirs) > 0:
            self.log.error(f'{path} not empty.')
            return False

        if path != '/':
            p = DirectoryOperator.get(DirectoryOperator.pardir(d))
            assert p is not None
            p.dirs.remove(d.name)

        self.db.session.delete(d)
        self.db.session.commit()
        return True

    def putfile(self, src: str, dst: str) -> File:
        f = FileOperator.get(dst)
        if f:
            self.log.warning(f'{dst} already exist')
            return None

        parent = os.path.split(dst)[0]
        d = DirectoryOperator.get(parent)
        if not d:
            self.log.error(f'{parent} is not exist')
            return None

        f = FileOperator.create(dst)
        f.chunks = self.maker.make(src, Hash.str_hash(dst))
        if not f.chunks:
            self.log.error(f'put file [{src}] to {[dst]} fail')
            return None

        if not self.chunk_service.put(f,
                                      self.maker.config.chunk_maker_workspace):
            self.log.error(f'put file [{src}] to {[dst]} fail')
            return None

        self.db.session.add(f)
        d.files.append(f.name)
        self.db.session.commit()
        return f

    def getfile(self, src: str, dst: str) -> bool:
        f = FileOperator.get(src)
        if not f:
            self.log.error(f'{src} not exist')
            return False

        if not self.chunk_service.get(f):
            self.log.error(f'fail to get file {src}')
            return False

        self.maker.combine(dst, f.chunks)
        return True
