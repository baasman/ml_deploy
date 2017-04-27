from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, mapper
from ml_deploy.config import ENGINE
import datetime
from ml_deploy.resources.common.database import User, Model, Project, load_session, session
from ml_deploy.resources.common.database import User_Project
from ml_deploy.config import ENGINE

engine = create_engine(ENGINE, echo=True)

def get_user(username):
    return session.query(User).filter_by(username=username).first()

def get_all_usernames():
    names = session.query(User.username).all()
    return [i[0] for i in names]


def add_sample_data():
    from sklearn import svm, datasets
    import pandas as pd
    import pickle
    clf = svm.SVC()
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    clf.fit(X, y)
    s = load_session(engine)
    u1 = User(username='boudey')
    u1.hash_password('thebest')
    u2 = User(username='boudey2')
    u2.hash_password('thebest2')
    
    print(u1, u2)
    project1 = Project(project_name='testProject', date_added=datetime.datetime.now())
    project2 = Project(project_name='testProject2', date_added=datetime.datetime.now())
    print(project1, project2)
    session.add_all([project1, project2])

    project1.add_users([u1, u2])
    project2.add_users([u1])

    mod = Model(model_name='testmod', model=pickle.dumps(clf),
                date_added=datetime.datetime.now(), model_source='sklearn',
                project=project1)
    print(mod)
    session.add(mod)

    session.commit()
    # # print(mod)
    # # print(mod.project)
    # s.add(u)
    # s.add(mod)
    # s.add(project)
    # s.commit()


if __name__ == '__main__':
    # add_sample_data()
    n = get_all_usernames()
    print(n)
