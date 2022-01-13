import json
import time

import pytest

from Models import DNORFunctions
from Models.Config import Config
from Models.RemoteUtil import RemoteUtil
from Models.RestAPIUtil import RestAPIUtil

dockerDNOR = 'dn40'
deploymentDNOR = 'dn0607'
config = Config(dnor=dockerDNOR)
configDeployment = Config(dnor=deploymentDNOR)
url = f'https://{configDeployment.primaryDNOR}.dev.drivenets.net/api/nce-management/deploy'
request = open('inputs/Scale/DeployScale.json')
data = json.load(request)
site = 'miami'
candidateStack = 'TestDeployment'

clusterType=''

def test01_getting_authorizationToken_siteID_groupID():
    global authorizationToken
    print('getting authorizationToken')
    jsonfile = open('Requests/V15/loginRequestBody.json')
    loginrequest = json.load(jsonfile)
    print(f"login request = {loginrequest}")
    url = f'https://{configDeployment.primaryDNOR}/api/login'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']

    groupId=DNORFunctions.get_groupid_from_DNOR(configDeployment.primaryDNOR)
    siteId=DNORFunctions.get_siteid_from_DNOR(configDeployment.primaryDNOR,site)

    assert (authorizationToken)
    assert (groupId)
    assert (siteId)

    data['groupId'] = groupId
    data['siteId'] = siteId
    data['candidateStack'] = candidateStack

@pytest.mark.skipif((clusterType!='CL-16') and (clusterType!=''), reason="CL-16 not requested by user")
def test02_get_NCC0_for_all_clusters_Type_CL_16():
    cmd = 'docker ps --format "{{.Names}}" | grep CL-16'
    global NCC0CL16
    NCC0CL16 = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.primaryDNOR, config).strip()

@pytest.mark.skipif((clusterType!='CL-16') and (clusterType!=''), reason="CL-16 not requested by user")
def test03_send_deplyoment_request_for_CL_16():
    if (NCC0CL16=='There was no output for this command'):
        pytest.skip('There is No Clusters Type CL-16 was found')
    i=0
    for ncc in NCC0CL16.split():
        time.sleep(60)
        clusterName = f'Cluster{i}-CL16'
        data['name'] = clusterName
        data['formation']['specific'] = 'CL-16'
        data['nccs'][0]['serialNumber'] = ncc
        data['nccs'][0]['hostName'] = ncc
        data['oobIpv4Address'] = f'1.1.1.{i}'
        i += 1
        try:
            RestAPIUtil.postAPIrequest(url, data, authorizationToken)
        except:
            continue


@pytest.mark.skipif((clusterType!='CL-96') and (clusterType!=''), reason="CL-16 not requested by user")
def test04_get_NCC0_for_all_clusters_Type_CL_96():
    cmd = 'docker ps --format "{{.Names}}" | grep CL-96'
    global NCC0CL96
    NCC0CL96 = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.primaryDNOR, config).strip()

@pytest.mark.skipif((clusterType!='CL-96') and (clusterType!=''), reason="CL-16 not requested by user")
def test05_send_deplyoment_request_for_CL_96():
    if (NCC0CL96=='There was no output for this command'):
        pytest.skip('There is No Clusters cype CL-96')
    i = 0
    for ncc in NCC0CL96.split():
        time.sleep(60)
        clusterName = f'Cluster{i}-CL96'
        data['name'] = clusterName
        data['formation']['specific'] = 'CL-96'
        data['nccs'][0]['serialNumber'] = ncc
        data['nccs'][0]['hostName'] = ncc
        data['oobIpv4Address'] = f'2.2.2.{i}'
        i += 1
        try:
            RestAPIUtil.postAPIrequest(url, data, authorizationToken)
        except:
            continue

@pytest.mark.skipif((clusterType!='CL-192') and (clusterType!=''), reason="CL-192 not requested by user")
def test06_get_NCC0_for_all_clusters_Type_CL_192():
    cmd = 'docker ps --format "{{.Names}}" | grep CL-192'
    global NCC0CL192
    NCC0CL192 = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.primaryDNOR, config).strip()

@pytest.mark.skipif((clusterType!='CL-192') and (clusterType!=''), reason="CL-192 not requested by user")
def test07_send_deplyoment_request_for_CL_192():
    if (NCC0CL192=='There was no output for this command'):
        pytest.skip('There is No Clusters type CL-196')
    i = 1
    for ncc in NCC0CL192.split():
        time.sleep(60)
        clusterName = f'Cluster{i}-CL192'
        data['name'] = clusterName
        data['formation']['specific'] = 'CL-192'
        data['nccs'][0]['serialNumber'] = ncc
        data['nccs'][0]['hostName'] = ncc
        data['oobIpv4Address'] = f'3.3.3.{i}'
        i += 1
        try:
            RestAPIUtil.postAPIrequest(url, data, authorizationToken)
        except:
            continue