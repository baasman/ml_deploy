from flask_restful import Resource, reqparse
from flask import abort, jsonify

import pickle
import json

from ml_deploy.resources.common.database import Model, User, session
from ml_deploy.resources.common.utils import read_data


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
        
        model = pickle.loads(model.model)

        try:
            data = read_data(file, skipheader, delimiter)
        except OSError as ose:
            abort(404, {'message': str(ose)})

        predictions = model.predict(data).tolist()
        predictions = json.dumps(predictions)

        return {'model': model.get_params(), 'file': file,
                'predictions': predictions}
