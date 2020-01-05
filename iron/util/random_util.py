#!/usr/bin/python

import random

def generate(l, r):
    return random.choice(range(l, r))

def generate_n(n, l, r):
    seq = ramdom.shuffle(range(l, r))
    return seq[:n]

