#!/usr/bin/env python3

from flask_restx import fields
from iron.ctrl import api

status_model = api.model('Status', {
    'status': fields.Boolean,
    'message': fields.String
})

file_model = api.model(
    'File', {
        'path': fields.String,
        'name': fields.String,
        'chunks': fields.List(fields.String),
    })

directory_model = api.model(
    'Directory', {
        'path': fields.String,
        'name': fields.String,
        'dirs': fields.List(fields.String),
        'files': fields.List(fields.String)
    })
