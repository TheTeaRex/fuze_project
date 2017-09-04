from constant import BASE_URL
import json
import requests

'''
We are using the following list of users with their password for testing.
To create the following users, run setup_db.py and create_users.py.
To run this file, you will need to have the service up and running, which you can simply run python server.py.
Remember to change the BASE_URL in constant.py for testing.

id | email                  | password
1  | mthurn@live.com        | hello1
2  | fangorn@hotmail.com    | hello2
3  | euice@outlook.com      | hello3
4  | rgarcia@optonline.net  | hello4
5  | mxiao@yahoo.com        | hello5
6  | firstpr@att.net        | hello6
7  | webdragon@comcast.net  | hello7
8  | jguyer@aol.com         | hello8
9  | sakusha@yahoo.ca       | hello9
10 | crandall@sbcglobal.net | hello10
11 | drezet@me.com          | hello11
12 | miyop@icloud.com       | hello12
'''

USERS = [
    {'email': 'mthurn@live.com', 'password': 'hello1'},
    {'email': 'fangorn@hotmail.com', 'password': 'hello2'},
    {'email': 'euice@outlook.com', 'password': 'hello3'},
    {'email': 'rgarcia@optonline.net', 'password': 'hello4'},
    {'email': 'mxiao@yahoo.com', 'password': 'hello5'},
    {'email': 'firstpr@att.net', 'password': 'hello6'},
    {'email': 'webdragon@comcast.net', 'password': 'hello7'},
    {'email': 'jguyer@aol.com', 'password': 'hello8'},
    {'email': 'sakusha@yahoo.ca', 'password': 'hello9'},
    {'email': 'crandall@sbcglobal.net', 'password': 'hello10'},
    {'email': 'drezet@me.com', 'password': 'hello11'},
    {'email': 'miyop@icloud.com', 'password': 'hello12'}
]

def get_auth(user):
    return requests.auth.HTTPBasicAuth(user['email'], user['password'])

# getting the list of users, no auth required
expected = [
    {'email': 'mthurn@live.com', 'user_id': 1},
    {'email': 'fangorn@hotmail.com', 'user_id': 2},
    {'email': 'euice@outlook.com', 'user_id': 3},
    {'email': 'rgarcia@optonline.net', 'user_id': 4},
    {'email': 'mxiao@yahoo.com', 'user_id': 5},
    {'email': 'firstpr@att.net', 'user_id': 6},
    {'email': 'webdragon@comcast.net', 'user_id': 7},
    {'email': 'jguyer@aol.com', 'user_id': 8},
    {'email': 'sakusha@yahoo.ca', 'user_id': 9},
    {'email': 'crandall@sbcglobal.net', 'user_id': 10},
    {'email': 'drezet@me.com', 'user_id': 11},
    {'email': 'miyop@icloud.com', 'user_id': 12}
]
res = requests.get(BASE_URL + '/users')
assert res.status_code == 200
assert json.loads(res.text) == expected

# trying to get a list of recordings without basic auth
res = requests.get(BASE_URL + '/recordings/')
result = json.loads(res.text)
assert res.status_code == 401

# currently there is no recording in the db at all
# so if we list the recording for user 1, it would be a empty list
expected = {'host_id': 1, 'recording_id': []}
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recordings/', auth=auth)
result = json.loads(res.text)
assert result == expected
assert len(result['recording_id']) == 0

# create a recording without basic auth
res = requests.get(BASE_URL + '/create/')
result = json.loads(res.text)
assert res.status_code == 401

# create a recording for user 1, default public
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/create/', auth=auth)
# create a recording for user 1, set as private
auth = get_auth(USERS[0])
params = {'private': True}
res = requests.get(BASE_URL + '/create/', auth=auth, params=params)
# create a recording for user 1, default public
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/create/', auth=auth)
# create a recording for user 3, default public
auth = get_auth(USERS[2])
res = requests.get(BASE_URL + '/create/', auth=auth)
# create a recording for user 12, default public
auth = get_auth(USERS[11])
res = requests.get(BASE_URL + '/create/', auth=auth)
# create a recording for user 1, default public
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/create/', auth=auth)

# verifying the recording creation
# user 1 should have 4 recordings
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recordings/', auth=auth)
result = json.loads(res.text)
assert len(result['recording_id']) == 4
# user 3 should have 1 recording
auth = get_auth(USERS[2])
res = requests.get(BASE_URL + '/recordings/', auth=auth)
result = json.loads(res.text)
assert len(result['recording_id']) == 1
# user 12 should have 1 recording
auth = get_auth(USERS[11])
res = requests.get(BASE_URL + '/recordings/', auth=auth)
result = json.loads(res.text)
assert len(result['recording_id']) == 1

# user 1 recording 2 is private, but the rest is public
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recording/1', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 0
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recording/2', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 1
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recording/3', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 0
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recording/6', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 0

# user 1 cannot access user 12's recording info
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/recording/5', auth=auth)
result = json.loads(res.text)
assert result['result'] == 'No recording found with id - 5'

# user 1 is making recording 1 to be private
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/make_private/1', auth=auth)
res = requests.get(BASE_URL + '/recording/1', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 1

# user 1 is making recording 1 to be public again
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/make_public/1', auth=auth)
res = requests.get(BASE_URL + '/recording/1', auth=auth)
result = json.loads(res.text)
assert result['result']['private'] == 0

# user 1 is deleting recording 3
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/delete/3', auth=auth)
res = requests.get(BASE_URL + '/recordings', auth=auth)
result = json.loads(res.text)
assert len(result['recording_id']) == 3
res = requests.get(BASE_URL + '/recording/3', auth=auth)
result = json.loads(res.text)
assert result['result'] == 'No recording found with id - 3'

# listing the available viewers for recording 1
# currently no viewer, since none added yet
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/viewers/1', auth=auth)
result = json.loads(res.text)
assert len(result['result']) == 0

# adding some viewers to recording 1
# host will not be added as part of the list viewers
expected = [USERS[i]['email'] for i in range(1,7)]
auth = get_auth(USERS[0])
params = {'users': '1,2,3,4,5,6,7'}
res = requests.get(BASE_URL + '/share/1', auth=auth, params=params)
res = requests.get(BASE_URL + '/viewers/1', auth=auth)
result = json.loads(res.text)
assert len(result['result']) ==  6 #  it's 6 but not 7, because host is not part of the viewers
assert result['result'] == expected

# removing user 4 and 5 as viewers from recording 1
auth = get_auth(USERS[0])
params = {'users': '4,5'}
res = requests.get(BASE_URL + '/remove_viewers/1', auth=auth, params=params)
res = requests.get(BASE_URL + '/viewers/1', auth=auth)
result = json.loads(res.text)
assert len(result['result']) == 4 

# check if a user has access to the recording, no auth required
res = requests.get(BASE_URL + '/viewable/2/1')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
res = requests.get(BASE_URL + '/viewable/7/1')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
res = requests.get(BASE_URL + '/viewable/12/1')
result = json.loads(res.text)
assert result['result'] == 'Not Viewable'
res = requests.get(BASE_URL + '/viewable/9/3')
result = json.loads(res.text)
assert result['result'] == 'Not Viewable'
# recording is private, but host is viewable
res = requests.get(BASE_URL + '/viewable/12/2')
result = json.loads(res.text)
assert result['result'] == 'Not Viewable'
res = requests.get(BASE_URL + '/viewable/1/2')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
# hosts can always view their own recordings
res = requests.get(BASE_URL + '/viewable/1/1')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
res = requests.get(BASE_URL + '/viewable/3/4')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
res = requests.get(BASE_URL + '/viewable/12/5')
result = json.loads(res.text)
assert result['result'] == 'Viewable'
res = requests.get(BASE_URL + '/viewable/1/6')
result = json.loads(res.text)
assert result['result'] == 'Viewable'

# making a recording private will remove all the viewers access
auth = get_auth(USERS[0])
res = requests.get(BASE_URL + '/viewers/1', auth=auth)
result = json.loads(res.text)
assert len(result['result']) == 4 
res = requests.get(BASE_URL + '/make_private/1', auth=auth)
res = requests.get(BASE_URL + '/viewers/1', auth=auth)
result = json.loads(res.text)
assert len(result['result']) == 0  # all the viewers have been removed
