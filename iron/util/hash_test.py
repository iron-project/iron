#!/usr/bin/env python3

import unittest
from iron.util.hash import Hash


class HashTest(unittest.TestCase):
    def test_str_hash(self):
        self.assertEqual('44bc2cf5ad770999', Hash.str_hash('abc'))

    def test_file_hash(self):
        f = '/tmp/hash_test'
        with open(f, 'wb') as of:
            of.write(b'abc')

        self.assertEqual('44bc2cf5ad770999', Hash.file_hash(f))
