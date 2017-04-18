from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, mapper
from config import ENGINE
import datetime
from database import User, Model, load_session, session
import sqlite3


engine = create_engine(ENGINE, echo=True)

def get_user(username):
    return session.query(User).filter_by(username=username).first()


def add_sample_data():
    from sklearn import svm, datasets
    import pandas as pd
    import pickle
    clf = svm.SVC()
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    clf.fit(X, y)
    s = load_session(engine)
    u = User(username='leah3')
    u.hash_password('ginsky')
    mod = Model(user=u, model_name='testmod', model=pickle.dumps(clf),
                date_added=datetime.datetime.now(), model_source='sklearn')
    s.add(u)
    s.add(mod)
    s.commit()


if __name__ == '__main__':
    add_sample_data()

