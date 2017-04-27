from flask_restful import Resource, reqparse
from flask import jsonify, abort
from ml_deploy.resources.auth import auth
from sqlalchemy.orm import exc as orm_exc

from ml_deploy.resources.common.database import User, session
from ml_deploy.resources.common.db_utils import get_user


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