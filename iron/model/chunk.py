#!/usr/bin/env python3

from iron.model import db


class Chunk(db.Model):
    name = db.Column(db.String(), primary_key=True)
    server = db.Column(db.String(), primary_key=True)
    sig = db.Column(db.String())


class ChunkOperator:
    @staticmethod
    def create(name: str) -> Chunk:
        return Chunk(name=name)

    @staticmethod
    def get(name: str, server: str) -> Chunk:
        return Chunk.query.get({'name': name, 'server': server})

    @staticmethod
    def gets(name: str) -> list[Chunk]:
        return Chunk.query.filter_by(name=name).all()
