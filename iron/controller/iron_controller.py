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
iron.mkdir('/foo')
iron.mkdir('/bar')
iron.mkdir('/bar/xxx')

# directory controller
directory_ns = api.namespace('directories', description='directory operations')
directory_model = api.model(
    'DirectoryModel',
    {
        'directories': fields.List(fields.String),
        'files': fields.List(fields.String)
    })

directory_args = api.parser()
directory_args.add_argument('path', required=True, help='directory absolute path')

@directory_ns.route('/readdir')
@directory_ns.expect(directory_args)
class Directory(Resource):
    @directory_ns.marshal_with(directory_model, envelope='data')
    def get(self):
        args = directory_args.parse_args()
        return iron.lsdir(args['path'])

# file controller

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
