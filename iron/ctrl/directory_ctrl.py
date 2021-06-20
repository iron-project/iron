#!/usr/bin/env python3

from flask_restx import Resource, fields

from iron.ctrl import api
from iron.service import fs
from iron.model.directory import DirectoryOperator

directory_namesapce = api.namespace(
    'directories', description='directory operations')

directory_model = api.model(
    'Directory',
    {
        'path': fields.String,
        'name': fields.String,
        'dirs': fields.List(fields.String),
        'files': fields.List(fields.String)
    })

status_model = api.model(
    'Status',
    {
        'status': fields.Boolean,
        'message': fields.String
    })

directory_argument = api.parser()
directory_argument.add_argument('path', required=True,
                                help='directory absolute path')


@directory_namesapce.route('/readdir')
@directory_namesapce.expect(directory_argument)
class GetDirectory(Resource):
    @directory_namesapce.marshal_with(directory_model, envelope='data')
    def get(self):
        args = directory_argument.parse_args()
        directory = fs.lsdir(args['path'])
        if directory is None:
            return None, 404
        else:
            return DirectoryOperator.marshal(directory)


@directory_namesapce.route('/mkdir')
@directory_namesapce.expect(directory_argument)
class CreateDirectory(Resource):
    @directory_namesapce.marshal_with(status_model, envelope='data')
    def post(self):
        args = directory_argument.parse_args()
        status = fs.mkdir(args['path'])
        return {'status': status, 'message': args['path']}


@directory_namesapce.route('/rmdir')
@directory_namesapce.expect(directory_argument)
class DeleteDirectory(Resource):
    @directory_namesapce.marshal_with(status_model, envelope='data')
    def delete(self):
        args = directory_argument.parse_args()
        status = fs.rmdir(args['path'])
        return {'status': status, 'message': args['path']}