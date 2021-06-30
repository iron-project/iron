#!/usr/bin/env python3

from flask_cors import CORS
from iron.model import db
from iron.ctrl import app, api
from iron.ctrl.file_ctrl import file_namespace
from iron.ctrl.directory_ctrl import directory_namespace
from iron.service import fs
from iron.service.chunk_server import ChunkServer


def register_chunk_server():
    fs.chunk_service.register_chunk_server(ChunkServer('fake1', None))
    fs.chunk_service.register_chunk_server(ChunkServer('fake2', None))
    fs.chunk_service.register_chunk_server(ChunkServer('fake3', None))
    fs.chunk_service.register_chunk_server(ChunkServer('fake4', None))


def register_namespace():
    api.add_namespace(file_namespace)
    api.add_namespace(directory_namespace)


def main():
    db.create_all()
    register_chunk_server()
    register_namespace()
    CORS(app)
    app.run(debug=True)


if __name__ == '__main__':
    main()
