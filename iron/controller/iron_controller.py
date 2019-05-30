from flask import Flask
from flask_restplus import Resource, Api

app = Flask(__name__)
api = Api(app, version='1.0', title='Iron API',
          description='The Iron API',
)

@api.route('/iron')
class IronCtrl(Resource):
    def get(self):
        return {'response': 'iron'}

if __name__ == '__main__':
    app.run(debug=True)
