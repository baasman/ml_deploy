from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy import PickleType, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship, sessionmaker
from config import ENGINE
from passlib.apps import custom_app_context as pwd_context

engine = create_engine(ENGINE, echo=True)

Base = declarative_base(engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password_hash = Column(String(128))
    models = relationship('Model', back_populates='user')

    def __repr__(self):
        return '<User(username:%s)>' % (self.username)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Model(Base):
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    model_name = Column(String, nullable=False)
    model_source = Column(String, nullable=True)
    model = Column(PickleType, nullable=False)
    date_added = Column(DateTime, nullable=True)
    user = relationship('User', back_populates='models')

    def __repr__(self):
        return '<Model(model_name:%s, model_source:%s, date_added:%s' % (self.model_name, self.model_source, self.date_added)


Base.metadata.create_all(engine)


