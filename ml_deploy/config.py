import configparser
import os

file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
config = configparser.ConfigParser()
config.read(file)
db = config['databases']
ENGINE = db['ENGINE']

VERSION = '0.0.1'
