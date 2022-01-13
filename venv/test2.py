import json

from Models.Config import Config
config = Config('dn40')

authorizationToken=''

def test33_add_users_to_DNOR():
    print('getting authorizationToken')
    loginrequest = json.load('Requests/loginRequestBody.json')
    print(loginrequest)