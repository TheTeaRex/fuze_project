from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from setup_db import Base, User
import constant
db = 'sqlite:///{}'.format(constant.DATABASE)
 
engine = create_engine(db)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

users = [
    {'email': 'mthurn@live.com', 'pw': 'hello1'},
    {'email': 'fangorn@hotmail.com', 'pw': 'hello2'},
    {'email': 'euice@outlook.com', 'pw': 'hello3'},
    {'email': 'rgarcia@optonline.net', 'pw': 'hello4'},
    {'email': 'mxiao@yahoo.com', 'pw': 'hello5'},
    {'email': 'firstpr@att.net', 'pw': 'hello6'},
    {'email': 'webdragon@comcast.net', 'pw': 'hello7'},
    {'email': 'jguyer@aol.com', 'pw': 'hello8'},
    {'email': 'sakusha@yahoo.ca', 'pw': 'hello9'},
    {'email': 'crandall@sbcglobal.net', 'pw': 'hello10'},
    {'email': 'drezet@me.com', 'pw': 'hello11'},
    {'email': 'miyop@icloud.com', 'pw': 'hello12'},
]

for user in users:
    new_user = User(email=user['email'], password=user['pw'])
    session.add(new_user)
    session.commit()
