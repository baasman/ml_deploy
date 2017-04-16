from flask import Flask, request, abort, jsonify
from flask_restful import Resource, Api, reqparse
from db_utils import load_session
from database import User, Model, engine
from sqlalchemy.orm import exc as orm_exc
from flask_httpauth import HTTPBasicAuth
from config import VERSION

session = load_session(engine)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    return True

app = Flask(__name__)
api = Api(app)


class Home(Resource):
    @auth.login_required
    def get(self):
        return 'Welcome!. Have fun deploying your models!', 200


class About(Resource):
    def get(self):
        return {'creator': 'Boudewijn Aasman',
                'email': 'boudeyz@gmail.com',
                'github': 'https://github.com/baasman'}, 200


class _User(Resource):
    @auth.login_required
    def get(self, username):
        user = session.query(User).filter_by(username=username).first()
        try:
            models = [i.model_name for i in user.models]
        except AttributeError:
            return 'Could not find user: %s' % username, 404
        return {'user': username, 'number_models': len(models),
                'models': models}, 200

    @auth.login_required
    def delete(self, username):
        user = session.query(User).filter_by(username=username).first()
        try:
            session.delete(user)
            session.commit()
        except orm_exc.UnmappedInstanceError:
            return 'Unable to delete user: %s' % username
        return 204


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


api.add_resource(Home, '/', '/home', endpoint='home')
api.add_resource(About, '/about')
api.add_resource(_User, '/user/<string:username>')
api.add_resource(CreateUser, '/account')


if __name__ == '__main__':
    app.run(debug=True, port=8005)