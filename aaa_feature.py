import json
import time

import pytest
import yaml
from Models.RestAPIUtil import *
from Models.Config import Config

config = Config(dnor='dn060607')
dnorVersion = "V17"

def test01_load_yamls_files_api_urls():
    global apiurls
    with open(f'API_URLS/{dnorVersion}/API_urls.yaml') as file:
        apiurls = yaml.load(file,Loader=yaml.FullLoader)
    assert (apiurls)

def test02_get_authorization_token():
    global authorizationToken
    print('getting authorizationToken')
    jsonfile = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    loginrequest = json.load(jsonfile)
    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)
    assert response.status_code == 200

def test03_add_5_DNOR_users_with_different_rules_to_Primary_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)
        assert response.status_code == 200
        time.sleep(5)

def test04_login_test_for_all_new_users_Primary_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    data = json.load(users)
    login = json.load(loginRequest)
    for user in data['dnorusers']:
        print(f'orginal request = {user}')
        login['username'] = user['username']
        login['password'] = user['password']
        print(f'sent request = {login}')
        response = RestAPIUtil.postAPIrequest(url, login,authorizationToken)
        assert (response['success'] == True)
        time.sleep(5)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test05_login_test_for_all_new_users_Secondary_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.secondaryDNOR}{apiurls.get("login_request_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    data = json.load(users)
    login = json.load(loginRequest)
    for user in data['dnorusers']:
        print(f'orginal request = {user}')
        login['username'] = user['username']
        login['password'] = user['password']
        print(f'sent request = {login}')
        response = RestAPIUtil.postAPIrequest(url, login,authorizationToken)
        assert (response['success'] == True)
        time.sleep(5)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test06_add_5_DNOR_users_with_different_rules_to_Secondary_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.secondaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)
    for user in data['dnorusers']:
        user['username'] = f"{user['username']}Secondary"
        print(f'request user = {user["username"]}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)
        time.sleep(5)

def test07_Negative_test_user_not_Exist():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.secondaryDNOR}{apiurls.get("login_request_url")}'
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    data = json.load(loginRequest)
    data['username'] = 'NotExist'
    response = RestAPIUtil.postAPIrequest(url, data,authorizationToken)
    assert (response['success'] == False)
    assert (response.status_code != 200)

def test08_Negative_test_inputs_validation():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.secondaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)
    user = data['dnorusers'][0]
    user['username'] = 'test'
    user['email'] = 'mmm'

    print('Testing user with Not valid Email')
    response = RestAPIUtil.postAPIrequest(url, user, authorizationToken)
    assert (response['success'] == False)

    print('Testing user with Empty Email')
    user['email'] = ''
    response = RestAPIUtil.postAPIrequest(url, user, authorizationToken)
    assert (response['success'] == False)

    print('Testing user with Not Vaild username')
    user['email'] = 'mmmmm.com'
    user['username'] = 'mmm_'
    response = RestAPIUtil.postAPIrequest(url, user, authorizationToken)
    assert (response['success'] == False)

    print('Adding user that alreadyExist')
    user['username'] = 'AdminUser'
    response = RestAPIUtil.postAPIrequest(url, user, authorizationToken)
    assert (response['success'] == False)

def test08_Permissions_validations_swithc_over():
    print('getting authorizationToken For viewer user')
    jsonfile = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    loginrequest = json.load(jsonfile)

    sofile = open(f'Requests/{dnorVersion}/switchOverRequest.json')
    sorequest = json.load(sofile)

    print("Testing Viewer user can't perform Switch over")
    loginrequest['username'] = 'ViewerUser'
    loginrequest['password'] = 'password123!'

    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)

    url = f'https://{config.primaryDNOR}{apiurls.get("swtich_over")}'
    response = RestAPIUtil.putAPIrequest(url, sorequest, authorizationToken)
    print(response.status_code)
    assert (response.status_code != 200)

    print("Testing Operator user can't perform Switch over")
    loginrequest['username'] = 'OperatorUser'
    loginrequest['password'] = 'password123!'

    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)

    url = f'https://{config.primaryDNOR}{apiurls.get("swtich_over")}'
    response = RestAPIUtil.putAPIrequest(url, sorequest, authorizationToken)
    print(response.status_code)
    assert (response.status_code != 200)


    print("Testing SuperAdmin user can perform Switch over")
    loginrequest['username'] = 'SuperAdminUser'
    loginrequest['password'] = 'password123!'

    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)

    url = f'https://{config.primaryDNOR}{apiurls.get("swtich_over")}'
    response = RestAPIUtil.putAPIrequest(url, sorequest, authorizationToken)
    assert (response.status_code == 200)

    time.sleep(240)

    print("Testing Admin user can perform Switch over")
    loginrequest['username'] = 'AdminUser'
    loginrequest['password'] = 'password123!'

    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)

    url = f'https://{config.primaryDNOR}{apiurls.get("swtich_over")}'
    response = RestAPIUtil.putAPIrequest(url, sorequest, authorizationToken)
    assert (response.status_code == 200)

def test09_get_user_info_primary_DNOR():
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    login = json.load(loginRequest)

    url = f'https://{config.primaryDNOR}{apiurls.get("login_request_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)

    for user in data['dnorusers']:
        login['username'] = user['username']
        login['password'] = user['password']
        print(f'sent request = {login}')
        response = RestAPIUtil.postAPIrequest(url, login)
        assert (response['success'] == True)
        authorizationToken = response['token']
        assert (authorizationToken)
        print({authorizationToken})
        getuser_url = f'https://{config.primaryDNOR}{apiurls.get("get_user")}/{user["username"]}'
        response_getuser = RestAPIUtil.getAPIrequest(getuser_url, "{}",authorizationToken)

        get_version_url = (f'https://{config.primaryDNOR}{apiurls.get("get_version")}')
        response_get_version = RestAPIUtil.getAPIrequest(get_version_url, "{}", authorizationToken)
        assert response_get_version.text
        assert (response_getuser.status_code == 200)
        assert response_getuser.json()['username'] == user['username']
        assert response_getuser.json()['firstName'] == user['firstName']
        assert response_getuser.json()['email'] == user['email']
        assert response_getuser.json()['lastName'] == user['lastName']
        assert response_getuser.json()['role'] == user['role']
        assert response_getuser.json()['userType'] == user['userType']
        assert response_getuser.json()['organizationId'] == user['organizationId']

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test10_get_user_info_secondary_DNOR():
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    login = json.load(loginRequest)

    url = f'https://{config.secondaryDNOR}{apiurls.get("login_request_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)

    for user in data['dnorusers']:
        login['username'] = user['username']
        login['password'] = user['password']
        print(f'sent request = {login}')
        response = RestAPIUtil.postAPIrequest(url, login)
        assert (response['success'] == True)
        authorizationToken = response['token']
        assert (authorizationToken)
        print({authorizationToken})
        getuser_url = f'https://{config.secondaryDNOR}{apiurls.get("get_user")}/{user["username"]}'
        response_getuser = RestAPIUtil.getAPIrequest(getuser_url, "{}",authorizationToken)

        get_version_url = (f'https://{config.secondaryDNOR}{apiurls.get("get_version")}')
        response_get_version = RestAPIUtil.getAPIrequest(get_version_url, "{}", authorizationToken)
        assert response_get_version.text
        assert (response_getuser.status_code == 200)
        assert response_getuser.json()['username'] == user['username']
        assert response_getuser.json()['firstName'] == user['firstName']
        assert response_getuser.json()['email'] == user['email']
        assert response_getuser.json()['lastName'] == user['lastName']
        assert response_getuser.json()['role'] == user['role']
        assert response_getuser.json()['userType'] == user['userType']
        assert response_getuser.json()['organizationId'] == user['organizationId']


def test10_delete_user():
    print("Validate user cannot delete it self and superadminuser")
    loginRequest = open(f'Requests/{dnorVersion}/loginRequestBody.json')
    login = json.load(loginRequest)

    url = f'https://{config.secondaryDNOR}{apiurls.get("login_request_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)

    for user in data['dnorusers']:
        login['username'] = user['username']
        login['password'] = user['password']
        print(f'sent request = {login}')
        response = RestAPIUtil.postAPIrequest(url, login)
        assert (response['success'] == True)
        authorizationToken = response['token']
        assert (authorizationToken)

        delet_user_url = f'https://{config.secondaryDNOR}{apiurls.get("delete_user")}'
        delet_user_url.replace("userName", f"{user['username']}")
        print (delet_user_url)
        #response_getuser = RestAPIUtil.getAPIrequest(getuser_url, "{}", authorizationToken)

        # get_version_url = (f'https://{config.secondaryDNOR}{apiurls.get("get_version")}')
        # response_get_version = RestAPIUtil.getAPIrequest(get_version_url, "{}", authorizationToken)
        # assert response_get_version.text
        # assert (response_getuser.status_code == 200)
        # assert response_getuser.json()['username'] == user['username']
        # assert response_getuser.json()['firstName'] == user['firstName']
        # assert response_getuser.json()['email'] == user['email']
        # assert response_getuser.json()['lastName'] == user['lastName']
        # assert response_getuser.json()['role'] == user['role']
        # assert response_getuser.json()['userType'] == user['userType']
        # assert response_getuser.json()['organizationId'] == user['organizationId']