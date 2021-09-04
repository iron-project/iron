#!/usr/bin/env python3

import os
from flask_cors import CORS

from iron.model import db
from iron.config import Config
from iron.ctrl import app, api
from iron.ctrl.file_ctrl import file_namespace
from iron.ctrl.directory_ctrl import directory_namespace
from iron.service import fs
from iron.service.http_chunk_server import HttpChunkServer


def register_chunk_server(config: Config):
    fs.chunk_service.register_chunk_server(
        HttpChunkServer('http-1', config.chunk_maker_workspace, 'http://127.0.0.1:1111'))
    fs.chunk_service.register_chunk_server(
        HttpChunkServer('http-2', config.chunk_maker_workspace, 'http://127.0.0.1:2222'))
    fs.chunk_service.register_chunk_server(
        HttpChunkServer('http-3', config.chunk_maker_workspace, 'http://127.0.0.1:3333'))
    fs.chunk_service.register_chunk_server(
        HttpChunkServer('http-4', config.chunk_maker_workspace, 'http://127.0.0.1:4444'))


def register_namespace():
    api.add_namespace(file_namespace)
    api.add_namespace(directory_namespace)


def init_config() -> Config:
    config = Config()
    if not os.path.exists(config.iron_download):
        os.makedirs(config.iron_download)
    if not os.path.exists(config.iron_upload):
        os.makedirs(config.iron_upload)
    return config


def main():
    db.create_all()
    config = init_config()
    register_chunk_server(config)
    fs.set_config(config)
    register_namespace()
    CORS(app)
    app.run(debug=True)


if __name__ == '__main__':
    main()
