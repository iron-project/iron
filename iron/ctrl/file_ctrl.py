#!/usr/bin/env python3

import os
from flask_restx import Resource
from flask import send_from_directory
from werkzeug.datastructures import FileStorage

from iron.config import Config
from iron.ctrl import api
from iron.ctrl.model import file_model
from iron.service import fs
from iron.model.file import FileOperator
from iron.util.hash import Hash

file_namespace = api.namespace('files',
                               description='file operations')

file_argument = api.parser()
file_argument.add_argument('path', required=True, help='file path')

upload_argument = api.parser()
upload_argument.add_argument('path', required=True)
upload_argument.add_argument('file', location='files',
                             type=FileStorage, required=True)


@file_namespace.route('/put')
@file_namespace.expect(upload_argument)
class PutFile(Resource):
    def __init__(self, api, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.config = Config()
        if not os.path.exists(self.config.iron_upload):
            os.makedirs(self.config.iron_upload)

    @file_namespace.marshal_with(file_model, envelope='data')
    def post(self):
        args = upload_argument.parse_args()
        path = os.path.normpath(args['path'])
        tmp = self.save_file(args['file'], path)
        f = fs.putfile(tmp, path)
        if f is None:
            return None, 404
        else:
            return FileOperator.marshal(f)

    def save_file(self, stream: FileStorage, path: str):
        name = Hash.str_hash(path)
        fpath = os.path.join(self.config.iron_upload, name)
        with open(fpath, 'wb') as f:
            chunk = stream.read(self.config.DEFAULT_CHUNK_SIZE)
            if chunk:
                f.write(chunk)
        return fpath


@file_namespace.route('/get')
@file_namespace.expect(file_argument)
class GetFile(Resource):
    def __init__(self, api, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.config = Config()
        if not os.path.exists(self.config.iron_download):
            os.makedirs(self.config.iron_download)

    def get(self):
        args = file_argument.parse_args()
        path = os.path.normpath(args['path'])
        name = Hash.str_hash(path)
        if fs.getfile(path, os.path.join(self.config.iron_download, name)):
            return send_from_directory(self.config.iron_download, name)
        return None, 404
