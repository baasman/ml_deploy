import hug
import os
from klepto.archives import file_archive
from constants import VERSION
from utils import load_archive, read_data
import numpy as np
import pickle
import json

redirect = hug.get(on_invalid=hug.redirect.not_found)


@redirect
@hug.get('/')
def home(): # noqa
    return 'Welcome to the site. Have fun deploying your models!'


@redirect
@hug.post('/predict_from_file', versions=1)
def predict_from_file(file: hug.types.text, model: hug.types.text, # noqa
                      skip_header: hug.types.boolean=True, delimiter: hug.types.text=','):
    """Returns predictions, reading data from file"""
    data = read_data(file, skip_header, delimiter)
    arch = load_archive(model)
    model = pickle.loads(arch['ml_model'])
    if arch['source'] == 'sklearn':
        data = np.array([1, 2, 3, 4])
        preds = model.predict(data)
        return {'result': json.dumps(preds.tolist())}
    else:
        return {'error': 'Model not understood'}

@redirect
@hug.get('/version')
def get_version():
    '''Returns version of ml_api package'''
    return {'ml_deploy version': VERSION}


@redirect
@hug.get('/about')
def about():
    return {'creator': 'Boudewijn Aasman',
            'email': 'boudeyz@gmail.com',
            'github': 'https://github.com/baasman'}


if __name__ == '__main__':
    hug.API(__name__).http.serve(port=8002)
