import configparser
import os

file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
config = configparser.ConfigParser()
config.read(file)
db = config['databases']
url = config['url']
keys = config['keys']
misc = config['misc_settings']

ENGINE = db['ENGINE']
HOST = url['HOST']
PORT = url['PORT']

SECRET_KEY = keys['SECRETKEY']
VERSION = '0.0.1'

DEBUG = True if misc['DEBUG'] == 'True' else False
