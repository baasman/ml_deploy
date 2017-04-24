from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import PickleType, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from config import ENGINE, SECRET_KEY
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

engine = create_engine(ENGINE, echo=True)

Base = declarative_base(engine)


def load_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


session = load_session(engine)


class User_Project(Base):
    __tablename__ = 'user_project'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))

    user = relationship("User", backref=backref("user_project", cascade="all, delete-orphan" ))
    project = relationship("Project", backref=backref("user_products", cascade="all, delete-orphan" ))

    def __init__(self, user=None, project=None):
        self.user = user
        self.project = project

    def __repr__(self):
        return 'User_Project(test)'


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password_hash = Column(String(128))
    # models = relationship('Model', back_populates='user')
    projects = relationship('Project', secondary='user_project', viewonly=True)

    def __init__(self, username):
        self.username = username
        self.projects = []

    def __repr__(self):
        return '<User(username:%s)>' % (self.username)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=1000):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        _s = Serializer(SECRET_KEY)
        try:
            data = _s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = session.query(User).filter_by(id=data['id'])
        return user


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    project_name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=True)
    models = relationship('Model', back_populates='project')
    users = relationship('User', secondary='user_project', viewonly=True)

    def __init__(self, project_name, date_added):
        self.project_name = project_name
        self.date_added = date_added
        self.users = []

    def add_users(self, items):
        for user in items:
            self.users.append(User_Project(user=user, project=self))

    def __repr__(self):
        return '<Project(project_name: %s, date_added: %s)>' % (self.project_name, self.date_added) # noqa


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    model_name = Column(String, nullable=False)
    model_source = Column(String, nullable=True)
    model = Column(PickleType, nullable=False)
    date_added = Column(DateTime, nullable=True)
    # user = relationship('User', back_populates='models')
    project = relationship('Project', back_populates='models')

    def __repr__(self):
        return '<Model(model_name:%s, model_source:%s, date_added:%s' % (self.model_name, self.model_source, self.date_added)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
