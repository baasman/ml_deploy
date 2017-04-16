from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, mapper
from config import ENGINE
import datetime
from database import User, Model
from sqlalchemy.orm.exc import NoResultFound
import sqlite3


engine = create_engine(ENGINE, echo=True)


def load_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_sample_data():
    from sklearn import svm, datasets
    import pandas as pd
    import pickle
    clf = svm.SVC()
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    clf.fit(X, y)
    s = load_session(engine)
    u = User(username='pippa')
    u.hash_password('nerd')
    mod = Model(user=u, model_name='testsvm2', model=pickle.dumps(clf))
    s.add(u)
    s.add(mod)
    s.commit()


if __name__ == '__main__':
    add_sample_data()

