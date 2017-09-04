import random
import string
from flask import Flask, request, abort
from flask_restful import reqparse, Resource, Api

import query

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('private')
parser.add_argument('users')

def string_generator(size=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def check_auth():
    auth = request.authorization
    if not auth:
        abort(401, 'Invalid Authenication')
    user_id = query.check_auth(auth)
    if user_id is None:
        abort(401, 'Invalid Authenication')
    return user_id

class ListUsers(Resource):
    def get(self):
        return query.list_users()

class Recording(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        msg = query.get_recording(host_id, recording_id)
        return {'result': msg}

class ListRecording(Resource):
    def get(self):
        host_id = check_auth()
        return {
            'host_id': host_id,
            'recording_id': query.list_recording(host_id)
        }

class Create(Resource):
    def get(self):
        host_id = check_auth()
        args = parser.parse_args()
        private = 0
        if args['private'] is not None:
            private = 1
        # just generating a random url for fun
        # but it will fetch and return the S3 url for this recording storage
        url = 'http://fuze.com/' + string_generator(32)
        query.add_recording(host_id, private, url)
        return {
            'host_id': host_id,
            'url': url
        }

class MakePrivate(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        msg = query.make_private(host_id, recording_id)
        return {'result': msg}

class MakePublic(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        msg = query.make_public(host_id, recording_id)
        return {'result': msg}

class Delete(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        msg = query.delete_recording(host_id, recording_id)
        return {'result': msg}

class Share(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        args = parser.parse_args()
        if args['users'] is None:
            abort(400, 'no users were provided to share')
        msg = query.share_recording(host_id, recording_id, args['users'])
        return {'result': msg}

class ListViewers(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        return {'result': query.list_viewers(host_id, recording_id)}

class RemoveViewers(Resource):
    def get(self, recording_id):
        host_id = check_auth()
        args = parser.parse_args()
        if args['users'] is None:
            abort(400, 'no users were provided to remove')
        msg = query.remove_viewers(host_id, recording_id, args['users'])
        return {'result': msg}

class Viewable(Resource):
    def get(self, user_id, recording_id):
        return {'result': query.viewable(user_id, recording_id)}
        

api.add_resource(ListUsers, '/users/')
api.add_resource(ListRecording, '/recordings/')
api.add_resource(Recording, '/recording/<int:recording_id>/')
api.add_resource(Create, '/create/')
api.add_resource(MakePrivate, '/make_private/<int:recording_id>/')
api.add_resource(MakePublic, '/make_public/<int:recording_id>/')
api.add_resource(Delete, '/delete/<int:recording_id>/')
api.add_resource(Share, '/share/<int:recording_id>/')
api.add_resource(ListViewers, '/viewers/<int:recording_id>/')
api.add_resource(RemoveViewers, '/remove_viewers/<int:recording_id>/')
api.add_resource(Viewable, '/viewable/<int:user_id>/<int:recording_id>/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
