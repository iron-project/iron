#!/usr/bin/python

import random
import pysnooper

def generate(l, r):
    return random.choice(range(l, r))

# @pysnooper.snoop()
def generate_n(n, l, r):
    seq = [*range(l, r)]
    random.shuffle(seq)
    return seq[:n]

