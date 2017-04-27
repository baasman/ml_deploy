from flask_restful import Resource, reqparse
from flask import abort, jsonify

import datetime

from ml_deploy.resources.common.database import Project, session
from ml_deploy.resources.common.db_utils import get_all_usernames, get_user
from ml_deploy.config import HOST, PORT

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