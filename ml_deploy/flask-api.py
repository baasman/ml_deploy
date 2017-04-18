from flask import Flask, request, abort, jsonify, url_for
from flask_restful import Resource, Api, reqparse
from database import User, Model, engine, load_session, session
from sqlalchemy.orm import exc as orm_exc
from flask_httpauth import HTTPBasicAuth
from config import VERSION, PORT, HOST
from db_utils import get_user
import pickle

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
        user = get_user(username)
        try:
            models = [str(i.model_name) for i in user.models]
        except AttributeError:
            abort(404)
        return jsonify({'user': username, 'number_models': len(models),
                'models': models})

    @auth.login_required
    def delete(self, username):
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
        user = get_user(username)
        try:
            token = user.generate_auth_token(600)
        except AttributeError:
            abort(404)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})


class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='Username of account')
        parser.add_argument('password', type=str, help='Password of account')
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        if username is None or password is None:
            abort(404)

        user = User(username=username)
        user.hash_password(password)

        try:
            session.add(user)
            session.commit()
        except Exception as e:
            print(str(e))
            return print('Unable to register user: %s' % username)
        return jsonify({'Username': username}, 201, 
                       {'Location': 'http://localhost:8005/user/%s' % username})


class _Model(Resource):
    def get(self, username, model_name):
        # result = session.query(User).join(Model).\
        #              filter(User.username==username).\
        #              filter(Model.model_name==model_name).all()
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
        return jsonify({'model_name': result.model_name,
                        'date_added': result.date_added,
                        'model_source': result.model_source,
                        'user': username,
                        'model_attributes': model_attributes})


class Home(Resource):
    def get(self):
        return 'Welcome!. Have fun deploying your models!', 200


class About(Resource):
    def get(self):
        return {'creator': 'Boudewijn Aasman',
                'email': 'boudeyz@gmail.com',
                'github': 'https://github.com/baasman'}, 200


api.add_resource(Home, '/', '/home')
api.add_resource(About, '/about')
api.add_resource(_User, '/user/<string:username>')
api.add_resource(CreateUser, '/account')
api.add_resource(Authentication, '/token/<string:username>')
api.add_resource(_Model, '/user/<string:username>/model/<string:model_name>')


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=int(PORT))
