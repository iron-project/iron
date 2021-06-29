#!/usr/bin/env python3

import os
from flask_restx import Resource

from iron.service import fs
from iron.model.directory import DirectoryOperator
from iron.ctrl import api
from iron.ctrl.model import status_model, directory_model

directory_namespace = api.namespace('directories',
                                    description='directory operations')
directory_argument = api.parser()
directory_argument.add_argument('path',
                                required=True,
                                help='directory path')


@directory_namespace.route('/readdir')
@directory_namespace.expect(directory_argument)
class GetDirectory(Resource):
    @directory_namespace.marshal_with(directory_model, envelope='data')
    def get(self):
        args = directory_argument.parse_args()
        path = os.path.normpath(args['path'])
        directory = fs.lsdir(path)
        if directory is None:
            return None, 404
        else:
            return DirectoryOperator.marshal(directory)


@directory_namespace.route('/mkdir')
@directory_namespace.expect(directory_argument)
class CreateDirectory(Resource):
    @directory_namespace.marshal_with(status_model, envelope='data')
    def post(self):
        args = directory_argument.parse_args()
        path = os.path.normpath(args['path'])
        status = fs.mkdir(path)
        return {'status': status, 'message': args['path']}


@directory_namespace.route('/rmdir')
@directory_namespace.expect(directory_argument)
class DeleteDirectory(Resource):
    @directory_namespace.marshal_with(status_model, envelope='data')
    def delete(self):
        args = directory_argument.parse_args()
        path = os.path.normpath(args['path'])
        status = fs.rmdir(path)
        return {'status': status, 'message': args['path']}
