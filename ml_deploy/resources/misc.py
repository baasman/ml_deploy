from flask_restful import Resource

class Home(Resource):
    def get(self):
        return 'Welcome!. Have fun deploying your models!'


class About(Resource):
    def get(self):
        return {'creator': 'Boudewijn Aasman',
                'email': 'boudeyz@gmail.com',
                'github': 'https://github.com/baasman/ml_deploy'}