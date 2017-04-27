from flask_restful import Resource, reqparse
from flask import abort, jsonify

import pickle

from ml_deploy.resources.common.database import Model, User, session


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