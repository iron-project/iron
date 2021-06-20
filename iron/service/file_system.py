#!/usr/bin/env python3

from iron.util.log import get_logger
from iron.model.directory import Directory, DirectoryOperator


class FileSystemService:
    def __init__(self, db):
        self.log = get_logger('fs')
        self.db = db

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
