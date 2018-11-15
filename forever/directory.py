#!/usr/bin/env python3

import records

ROOT_PATH = '/'

class Directory(object):
    def __init__(self, dir_path = ROOT_PATH, dir_name = ROOT_PATH):
        self.create_time = time.asctime()
        self.dir_path = dir_path
        self.dir_name = dir_name
        self.sub_file = []
        self.sub_dir = []

    def mkdir(self, dir_name):

