#!/usr/bin/env python3

from flask_restx import Resource, Api, fields
from werkzeug.middleware.proxy_fix import ProxyFix

from iron.model import db
from iron.model.directory import DirectoryOperator
from iron.controller import app
from iron.service.file_system import FileSystemService

app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Iron API',
          description='The Iron API')

# iron service
fs = FileSystemService()
db.create_all()

# Response model
directory_ns = api.namespace('directories', description='directory operations')
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

directory_args = api.parser()
directory_args.add_argument('path', required=True,
                            help='directory absolute path')

# Api


@directory_ns.route('/readdir')
@directory_ns.expect(directory_args)
class GetDirectory(Resource):
    @directory_ns.marshal_with(directory_model, envelope='data')
    def get(self):
        args = directory_args.parse_args()
        directory = fs.lsdir(args['path'])
        if directory is None:
            return None, 404
        else:
            return DirectoryOperator.marshal(directory)


@directory_ns.route('/mkdir')
@directory_ns.expect(directory_args)
class CreateDirectory(Resource):
    @directory_ns.marshal_with(status_model, envelope='data')
    def post(self):
        args = directory_args.parse_args()
        status = fs.mkdir(args['path'])
        return {'status': status, 'message': args['path']}


@directory_ns.route('/rmdir')
@directory_ns.expect(directory_args)
class DeleteDirectory(Resource):
    @directory_ns.marshal_with(status_model, envelope='data')
    def delete(self):
        args = directory_args.parse_args()
        status = fs.rmdir(args['path'])
        return {'status': status, 'message': args['path']}


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
