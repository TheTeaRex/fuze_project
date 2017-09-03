import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import constant
db = 'sqlite:///{}'.format(constant.DATABASE)
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)

class Recording(Base):
    __tablename__ = 'recording'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    private = Column(Integer, nullable=False)
    url = Column(String(128), nullable=True)

class Viewer(Base):
    __tablename__ = 'viewer'
    id = Column(Integer, primary_key=True)
    recording_id = Column(Integer, ForeignKey('recording.id'), nullable=False)
    email = Column(String(250), ForeignKey('user.email'), nullable=False)

engine = create_engine(db)
Base.metadata.create_all(engine)
