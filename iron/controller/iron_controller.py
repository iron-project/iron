#!/usr/bin/env python3

from flask import Flask, request
from flask_restplus import Resource, Api, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from iron.service.iron_service import IronService

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Iron API',
          description='The Iron API')

# iron service
iron = IronService()
iron.init_records()
iron.mkdir('/', True)

# Response model
directory_ns = api.namespace('directories', description='directory operations')
directory_model = api.model(
    'Directory',
    {
        'directories': fields.List(fields.String),
        'files': fields.List(fields.String)
    })

status_model = api.model(
    'Status',
    {
        'status': fields.Boolean,
        'message': fields.String
    })

directory_args = api.parser()
directory_args.add_argument('path', required=True, help='directory absolute path')

# Api
@directory_ns.route('/readdir')
@directory_ns.expect(directory_args)
class ReadDirectory(Resource):
    @directory_ns.marshal_with(directory_model, envelope='data')
    def get(self):
        args = directory_args.parse_args()
        return iron.lsdir(args['path'])

@directory_ns.route('/mkdir')
@directory_ns.expect(directory_args)
class MakeDirectory(Resource):
    @directory_ns.marshal_with(status_model, envelope='data')
    def post(self):
        args = directory_args.parse_args()
        status = iron.mkdir(args['path'])
        return {'status': status, 'message': args['path']}

@directory_ns.route('/rmdir')
@directory_ns.expect(directory_args)
class MakeDirectory(Resource):
    @directory_ns.marshal_with(status_model, envelope='data')
    def delete(self):
        args = directory_args.parse_args()
        status = iron.rmdir(args['path'])
        return {'status': status, 'message': args['path']}

# file controller
file_namespace = api.namespace('files', description='file operations')

param_parser_putfile = api.parser()
param_parser_putfile.add_argument('remote_path', required=True, help='absolute path')
param_parser_putfile.add_argument('local_path', required=True, help='absolute path')
@file_namespace.route('/putfile')
@file_namespace.expect(param_parser_putfile)
class PutFile(Resource):
    @file_namespace.marshal_with(status_model, envelope='data')
    def post(self):
        param = param_parser_putfile.parse_args()
        status = iron.putfile(param['local_path'], param['remote_path'])
        return {'status': status, 'message': 'success'}

param_parser_getfile = api.parser()
param_parser_getfile.add_argument('remote_path', required=True, help='absolute path')
param_parser_getfile.add_argument('local_path', required=True, help='absolute path')
@file_namespace.route('/getfile')
@file_namespace.expect(param_parser_getfile)
class GetFile(Resource):
    @file_namespace.marshal_with(status_model, envelope='data')
    def get(self):
        param = param_parser_getfile.parse_args()
        status = iron.getfile(param['remote_path'], param['local_path'])
        return {'status': status, 'message': 'success'}

param_parser_rmfile = api.parser()
param_parser_rmfile.add_argument('remote_path', required=True, help='absolute path')
@file_namespace.route('/rmfile')
@file_namespace.expect(param_parser_rmfile)
class RemoveFile(Resource):
    @file_namespace.marshal_with(status_model, envelope='data')
    def delete(self):
        param = param_parser_rmfile.parse_args()
        status = iron.rmfile(param['remote_path'])
        return {'status': status, 'message': 'success'}

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
