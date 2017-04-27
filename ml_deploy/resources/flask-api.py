import json
import pickle
import datetime

from flask import Flask, abort, jsonify, request, url_for
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm import exc as orm_exc

from utils import read_data
from config import HOST, PORT, VERSION
from database import Model, User, Project, engine, load_session, session
from db_utils import get_user, get_all_usernames

auth = HTTPBasicAuth()


app = Flask(__name__)
api = Api(app)


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = get_user(username_or_token)
        if not user or not user.verify_password(password):
            return False
    return True


class _User(Resource):
    @auth.login_required
    def get(self, username):
        '''Gets users attributes
        Attributes:
            username    Username of user
        '''
        user = get_user(username)
        projects = user.projects
        mods_per_project = {}
        for project in projects:
            mods_per_project[project.project_name] = [str(i.model_name) for i in project.models]
        return jsonify({'user': username, 'projects': mods_per_project})

    @auth.login_required
    def delete(self, username):
        '''Deletes a user and all 
        Attributes:
            username    Username of user
        '''
        user = get_user(username)
        try:
            session.delete(user)
            session.commit()
        except orm_exc.UnmappedInstanceError:
            return 'Unable to delete user: %s' % username
        return 204


class Authentication(Resource):
    @auth.login_required
    def get(self, username):
        '''Generates token for user
        Attributes:
            username    Username of user
        '''
        user = get_user(username)
        try:
            token = user.generate_auth_token(600)
        except AttributeError:
            abort(404)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})


class CreateUser(Resource):
    '''Resource that handles accounts'''
    def post(self):
        '''
        Attributes:
        username    Username, string
        password    Password, string
        '''

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='Username of account')
        parser.add_argument('password', type=str, help='Password of account')
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        if username in [i[0] for i in session.query(User.username).all()]:
            abort(404, {'message': 'Username %s already exists' % username})

        if username is None or password is None:
            abort(404, 'Must supply both username and password')

        user = User(username=username)
        user.hash_password(password)

        try:
            session.add(user)
            session.commit()
        except Exception as e:
            print(str(e))
            session.rollback()
            abort(404, {'message': str(e)})
        return jsonify({'Username': username,
                        'location': 'http://%s:%s/user/%s' % (HOST, PORT, username)})


class _Model(Resource):
    '''Resource for accessing model attributes'''
    def get(self, username, model_name):
        '''
        Attributes:
            username    Username of user
            model_name  Name of model to explore
        '''
        result = session.query(Model).join(User).\
                         filter(User.username==username).all()
        if len(result) > 1:
            return jsonify({'error': 'Multiple models under this name: %s' % result.model_name})
        else:
            try:
                result = result[0]
            except IndexError:
                abort(404)

        model = pickle.loads(result.model)
        try:
            model_attributes = model.get_params() if result.model_source == 'sklearn' else 'NA'
        except:
            model_attributes = 'NA'

        try:
            part_of = result.project.project_name
        except Exception as e:
            abort(404, {'error': str(e)})

        return jsonify({'model_name': result.model_name,
                        'date_added': result.date_added,
                        'model_source': result.model_source,
                        'user': username,
                        'model_attributes': model_attributes,
                        'part_of': part_of})


class BatchPredict(Resource):
    '''Resource for batch prediction'''
    
    def get(self, username, model_name):
        ''' Make a batch prediction from a file
        Attributes:
            username    The user's username
            model_name  The user's model to be used for prediction
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=str, help='Filepath to data')
        parser.add_argument('skipheader', type=bool, help='Should header be skipped?')
        parser.add_argument('delimiter', type=str, help='What delimiter is used in data?')

        args = parser.parse_args()

        file = args['file']
        skipheader = args['skipheader']
        delimiter = args['delimiter']

        model = session.query(Model).join(User).\
                         filter(User.username==username).first()
        # try:
        model = pickle.loads(model.model)
        # except OSError as io:
        #     abort(404, {'message': str(io)})

        try:
            data = read_data(file, skipheader, delimiter)
        except OSError as ose:
            abort(404, {'message': str(ose)})

        predictions = model.predict(data).tolist()
        predictions = json.dumps(predictions)

        return {'model': model.get_params(), 'file': file,
                'predictions': predictions}


class _Project(Resource):
    '''Handles projects'''
    def get(self, project_name):
        '''
        Attributes:
        project     Project name
        '''
        # project = session.query(Project).filter(Project.project_name==project_name)
        # users = project.users
        # projects = session.query(Project).get(user.id)
        # print(projects)
        # models_per_project = {}
        # for i in projects:
        #     models_per_project[i.project_name] = [[str(i.model_name) for i in project.models]]
        # print(project.models)
        return jsonify({'project': {'hmm': 'hello'},
                        'date_added': 'ayo',
                        'users': 'hello'})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('project_name', type=str,
                            required=True, help='Name of project')
        parser.add_argument('users', type=str, action='append')
        args = parser.parse_args()

        project_name = args['project_name']
        all_users = args['users']

        project = Project(project_name=project_name,
                          date_added=datetime.datetime.now())
        session.add(project)

        all_names = get_all_usernames()
        user_objects = []
        for name in all_users:
            if name in all_names:
                user_objects.append(get_user(name))
            else:
                abort(404, {'message': 'Username %s does not exist' % name})
        project.add_users(user_objects)

        try:
            session.commit()
        except Exception as project_exception:
            session.rollback()
            abort(404, {'message': str(project_exception)})

        return jsonify({'project': 'http://%s:%s/project/%s' % (HOST, PORT, project_name),
                        'users': all_users})


class Home(Resource):
    def get(self):
        return 'Welcome!. Have fun deploying your models!'


class About(Resource):
    def get(self):
        return {'creator': 'Boudewijn Aasman',
                'email': 'boudeyz@gmail.com',
                'github': 'https://github.com/baasman/ml_deploy'}


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
    app.run(debug=True, host=HOST, port=int(PORT))
