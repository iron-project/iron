#!/usr/bin/env python3

from iron.model import db


class Chunk(db.Model):
    name = db.Column(db.String())
    server = db.Column(db.String())
    sig = db.Column(db.String())
