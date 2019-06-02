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

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
