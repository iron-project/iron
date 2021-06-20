#!/usr/bin/env python3

from iron.ctrl import app
from iron.model import db

# import ctrl impl to bind to flask-restx
from iron.ctrl.directory_ctrl import *


def main():
    db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()
