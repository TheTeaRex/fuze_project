from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm.exc
 
from setup import Base, User, Recording, Viewer
import constant
db = 'sqlite:///{}'.format(constant.DATABASE)
 
engine = create_engine(db)
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

def check_auth(auth):
    try:
        user = session.query(User).filter(User.email == auth.username).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
    if user.password != auth.password:
        return None
    return user.id

def list_users():
    users = session.query(User).all()
    result = []
    for user in users:
        result.append({'user_id': user.id, 'email': user.email})
    return result

def list_recording(host_id):
    recordings = session.query(Recording).filter(Recording.host_id == host_id).all()
    return [recording.id for recording in recordings]

def add_recording(host_id, private, url):
    new_recording = Recording(host_id=host_id, private=private, url=url)
    session.add(new_recording)
    session.commit()

def make_private(host_id, recording_id):
    # once made private, need to clean up viewers
    try:
        recording = session.query(Recording).filter(Recording.id == recording_id).filter(Recording.host_id == host_id).one()
        recording.private = 1
        session.commit()
    except sqlalchemy.orm.exc.NoResultFound:
        return 'No recording found with id - {}'.format(recording_id)
    remove_all_viewers(recording_id)
    return 'Successful'

def make_public(host_id, recording_id):
    try:
        recording = session.query(Recording).filter(Recording.id == recording_id).filter(Recording.host_id == host_id).one()
        recording.private = 0
        session.commit()
    except sqlalchemy.orm.exc.NoResultFound:
        return 'No recording found with id - {}'.format(recording_id)
    return 'Successful'

def delete_recording(host_id, recording_id):
    try:
        recording = session.query(Recording).filter(Recording.id == recording_id).one()
        if recording.host_id != host_id:
            return 'You do not own this recording, cannot delete'
        session.delete(recording)
        session.commit()
    except sqlalchemy.orm.exc.NoResultFound:
        return 'Deletion failed, no recording found with id - {}'.format(recording_id)
    return 'Deletetion successful'

def share_recording(host_id, recording_id, users):
    if not is_owner(host_id, recording_id):
        return 'You do not own this recording, cannot share it'
    if is_recording_private(recording_id):
        return 'Recording is private, cannot be shared'
    users = users.split(',')
    emails = []
    for user_id in users:
        # do not add the host as part of the viewer
        if int(user_id) is not host_id:
            emails.append(add_viewer(int(user_id), recording_id))
    emails = filter(None, emails)
    if len(emails) == 0:
        return 'None added due to either users added already or users do not exist'
    return emails

def list_viewers(host_id, recording_id):
    if not is_owner(host_id, recording_id):
        return 'You do not have permission to list the viewers of this recording'
    viewers = session.query(Viewer).filter(Viewer.recording_id == recording_id).all()
    result = []
    for viewer in viewers:
        result.append(viewer.email)
    return result

def add_viewer(user_id, recording_id):
    email = get_user_email(int(user_id))
    if not viewer_already(email, recording_id):
        new_viewer = Viewer(recording_id=recording_id, email=email)
        session.add(new_viewer)
        session.commit()
        return email

def remove_all_viewers(recording_id):
    try:
        viewers = session.query(Viewer).filter(Viewer.recording_id == recording_id).all()
    except sqlalchemy.orm.exc.NoResultFound:
        pass
    for viewer in viewers:
        session.delete(viewer)
    session.commit()

def remove_viewers(host_id, recording_id, users):
    if not is_owner(host_id, recording_id):
        return 'You do not own this recording, cannot remove viewer'
    users = users.split(',')
    emails = [get_user_email(int(user_id)) for user_id in users]
    emails = filter(None, emails)
    try:
        viewers = session.query(Viewer).filter(Viewer.recording_id == recording_id).all()
    except sqlalchemy.orm.exc.NoResultFound:
        return 'Successful'
    for viewer in viewers:
        if viewer.email in emails:
            session.delete(viewer)
    session.commit()
    return 'Successful'

def viewer_already(email, recording_id):
    try:
        session.query(Viewer).filter(Viewer.email == email).filter(Viewer.recording_id == recording_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return False
    return True

def is_owner(host_id, recording_id):
    try:
        recording = session.query(Recording).filter(Recording.host_id == host_id).filter(Recording.id == recording_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return False
    return True

def is_recording_private(recording_id):
    recording = session.query(Recording).filter(Recording.id == recording_id).one()
    if recording.private == 0:
        return False
    return True

def get_user_email(user_id):
    user = session.query(User).filter(User.id == user_id).one()
    return user.email
