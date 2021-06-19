#!/usr/bin/env python3

from os import pardir
from iron.model import db
from iron.model.directory import Directory, DirectoryOperator


class FileSystemService(object):
    def __init__(self):
        pass

    def mkdir(self, path: str) -> bool:
        d = DirectoryOperator.get(path)
        if d:
            print('{} already exist.'.format(path))
            return True

        d = DirectoryOperator.create(path)
        if path == '/':
            db.session.add(d)
            db.session.commit()
            return True

        pardir = DirectoryOperator.pardir(d)
        p = DirectoryOperator.get(pardir)
        if not p:
            print('{} not exist.'.format(pardir))
            return False

        db.session.add(d)
        p.dirs.append(d.name)
        db.session.commit()
        return True

    def lsdir(self, path: str) -> Directory:
        d = DirectoryOperator.get(path)
        if not d:
            print('{} not exist.'.format(path))
            return None
        print(DirectoryOperator.marshal(d))
        return d

    def rmdir(self, path: str) -> bool:
        d = DirectoryOperator.get(path)
        if not d:
            print('{} not exist.'.format(path))
            return True

        if len(d.files) > 0 or len(d.dirs) > 0:
            print('{} not empty.'.format(path))
            return False

        if path != '/':
            p = DirectoryOperator.get(DirectoryOperator.pardir(d))
            assert p is not None
            p.dirs.remove(d.name)

        db.session.delete(d)
        db.session.commit()
        return True
