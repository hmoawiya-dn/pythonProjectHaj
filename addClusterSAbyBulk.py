import configparser
import pytest
import time
from Models import Functions
from Models import DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config
from Models.RestAPIUtil import *
from Models.postgresUtil import postgresUtil
import yaml

config = Config(dnor='dn07')
dnorVersion = "V16"
remote_vm = "dn36-dnor-swarmless"
amount = 150

def test01_load_yamls_files():
    global apiurls
    with open(f'API_URLS/{dnorVersion}/API_urls.yaml') as file:
        apiurls = yaml.load(file,Loader=yaml.FullLoader)
    assert (apiurls)

def test02_getting_authorizationToken():
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

def test03_add_bulks_clusters_by10_every_7minutes():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("add_bulk_clusters")}'
    clusters = open(f'inputs/bulk/{dnorVersion}/BulkClusters.json')
    data = json.load(clusters)
    data['bulks'][0]['hostRemoteDeploy'] = remote_vm
    #print(f"here= {data['hostRemoteDeploy']}")
    print(f"data= {data['bulks'][0]['hostRemoteDeploy']}")
    #data['bulks'].put['hostRemoteDeploy'] = "remote_vm"
    #print(amount//10)
    request = data["bulks"][0]
    for i in range(amount//10):
        time.sleep(1000)
        print(i)
        print(f'request = {data["bulks"][0]}')
        try:
            response = RestAPIUtil.postAPIrequest(url,request,authorizationToken)
        except:
            continue
        #assert (response['success'] == True)

