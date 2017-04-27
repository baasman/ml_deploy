from flask_restful import Api
from flask import Flask

from ml_deploy.resources.misc import Home, About
from ml_deploy.resources.user import _User, CreateUser, Authentication
from ml_deploy.resources.predict import BatchPredict
from ml_deploy.resources.model import _Model
from resources.project import _Project

from config import HOST, PORT, DEBUG


app = Flask(__name__)
api = Api(app)


api.add_resource(Home, '/', '/home')
api.add_resource(About, '/about')
api.add_resource(_User, '/user/<string:username>')
api.add_resource(CreateUser, '/account')
api.add_resource(Authentication, '/token/<string:username>')
api.add_resource(_Model, '/user/<string:username>/model/<string:model_name>')
api.add_resource(BatchPredict, '/user/<string:username>/model/<string:model_name>/batch_predict')
api.add_resource(_Project, '/project', endpoint='create_project')
api.add_resource(_Project, '/project/<string:project_name>', endpoint='project')


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=int(PORT))
