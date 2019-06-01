#!/usr/bin/env python3

import records
import threading


def synchronized(func):
    func.__lock__ = threading.Lock()
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

class Connect():
    def __init__(self, config):
        self.config = config
        self.thread_connects = {}

    @synchronized
    def connection(self):
        connect = self.thread_connects.get(threading.get_ident(), None)
        if connect is None:
            connect = records.Database(self.config.SQLITE_URI)
            self.thread_connects[threading.get_ident()] = connect
        return connect
