import configparser
import json

import pytest
import time
from Models import Functions
from Models import DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config
from Models.RestAPIUtil import *
from Models.postgresUtil import postgresUtil
import yaml

versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-14.1.2/dnor_release.14.1.2.25-e874db7b47.tar'
dnorVersion = "V17"
config = Config(dnor='dn06')
usersAmount = 1000
sitesAmount = 1000

@pytest.mark.addinputs1
def test01_load_yamls_files():
    global apiurls
    with open(f'API_URLS/{dnorVersion}/API_urls.yaml') as file:
        apiurls = yaml.load(file,Loader=yaml.FullLoader)
    assert (apiurls)

@pytest.mark.addinputs1
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

@pytest.mark.addinputs
def test03_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/Scale/{dnorVersion}/users/users.json')
    data = json.load(users)
    for i in range(usersAmount):
        for user in data['dnorusers']:
            #print('%03d' % i)
            newReq = user.copy()
            print('%03d' % i)
            userNew = (f"{user['username']}"+'%03d' % i)
            newReq['username'] = userNew
            print(f'request = {newReq}')
            #print(f'request = {user}')
            response = RestAPIUtil.postAPIrequest(url, newReq,authorizationToken)
            assert (response['success'] == True)
            time.sleep(5)

@pytest.mark.addinputs
def test04_add_images_to_DNOR():
    global authorizationToken
    images = open(f'inputs/ATTMigration/images.json')
    data = json.load(images)
    dowmloadrequest = open('inputs/images/imagesDownload.json')
    dowloadjson = json.load(dowmloadrequest)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net{apiurls.get("add_images_url")}'
    if apiurls.get("download-image"):
        downloadurl = f'https://{config.primaryDNOR}.dev.drivenets.net{apiurls.get("download-image")}'
    for image in data['dnos_images']:
        try:
            response = RestAPIUtil.postAPIrequest(url, image, authorizationToken)
            if apiurls.get("download-image"):
                dowloadjson['id'] = response["id"]
                RestAPIUtil.postAPIrequest(downloadurl, dowloadjson, authorizationToken)
        except:
            continue
        time.sleep(5)

@pytest.mark.addinputs1
def test05_add_sites_to_DNOR():
    global authorizationToken
    sites = open(f'inputs/Scale/{dnorVersion}/sites/sites.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_sites_url")}'
    if (apiurls.get("site_group")):
        print("getting group id")
        cmd = "select id from nce_management.site_groups where "+ '"companyName" = '+ "'DRIVENETS'"
        response = postgresUtil.execQueryPS(cmd, config.primaryDNOR)
        groupID = response[0][0]

    for i in range(100):
        for site in data['sites']:
            newname = "SiteTestATTMigration"+str(i)
            site['name'] = newname
            response = RestAPIUtil.postAPIrequest(url, site, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test06_add_Tacacs_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Tacacs'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    tacacsServiceID = response1[0][0]
    global authorizationToken
    tacacs = open(f'inputs/ATTMigration/tacacs.json')
    data = json.load(tacacs)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_tacacs_url")}'

    for i in range(5):
        for tacacs in data['tacacs']:
            print(f'request = {tacacs}')
            tacacs['serviceId'] = tacacsServiceID
            newname = "TacacsServer" + str(i)
            tacacs['description']= newname
            response = RestAPIUtil.postAPIrequest(url, tacacs, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test07_add_Radius_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Radius'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    radiusServiceID = response1[0][0]
    global authorizationToken
    radius = open(f'inputs/ATTMigration/radius.json')
    data = json.load(radius)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_radius_url")}'
    for i in range(5):
        for radius in data['radius']:
            print(f'request = {radius}')
            radius['serviceId'] = radiusServiceID
            newname = "RadiusServer" + str(i)
            radius['description'] = newname
            response = RestAPIUtil.postAPIrequest(url, radius, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test08_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open(f'inputs/ATTMigration/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_syslog_servers_url")}'
    for i in range(10):
        for syslogs in data['syslogs']:
            print(f'request = {syslogs}')
            newip = f"{str(i)}.{str(i)}.{str(i)}.{str(i)}"
            syslogs['ip'] = newip
            response = RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)
            time.sleep(10)

@pytest.mark.addinputs
def test09_add_NCE_users_group_to_DNOR():
    global authorizationToken
    ncegroup = open(f'inputs/ATTMigration/NCEusers.json')
    data = json.load(ncegroup)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_nce_user_group")}'
    for i in range(100):
        for group in data['ncegroups']:
            name = "NewNCEUsersGroup"+str(i)
            print(f'request = {group}')
            group['name'] = name
            response = RestAPIUtil.postAPIrequest(url, group, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test10_generate_tech_supports_to_DNOR():
    global authorizationToken
    tss = open(f'inputs/ATTMigration/techSupports.json')
    data = json.load(tss)
    url = f'https://{config.primaryDNOR}{apiurls.get("generate_dnor_techSupport")}'
    for i in range(50):
        for ts in data['dnortss']:

            name = "DNORTechSupportAutomated"+str(i)
            ts['fileName']=name
            print(f'request Haj = {ts}')
            response = RestAPIUtil.postAPIrequest(url, ts, authorizationToken)
            time.sleep(12)

@pytest.mark.addinputs
def test11_perform_DNOR_backup():
    global authorizationToken
    for i in range(50):
        url = f'https://{config.primaryDNOR}{apiurls.get("dnor_back_up")}'
        RestAPIUtil.postAPIrequest(url, "", authorizationToken)
        time.sleep(10)

@pytest.mark.addinputs
def test12_Change_AAA_settings():
    global authorizationToken
    alarms = open(f'inputs/ATTMigration/aaaSettings.json')
    data = json.load(alarms)
    url = f'https://{config.primaryDNOR}{apiurls.get("aaa_settings")}'
    for alarm in data['alarms']:
        response = RestAPIUtil.postAPIrequest(url, alarm, authorizationToken)

@pytest.mark.addinputs
def test13_Enable_gNMI_configuration():
    global authorizationToken
    alarms = open(f'inputs/ATTMigration/EnablegNMIConfiguration.json')
    data = json.load(alarms)
    for con in data['configs']:
        urls = ["secured_Gnmi", "enable_gNMI", "enable_Counters"]
        for url in urls:
            full_url = f'https://{config.primaryDNOR}{apiurls.get(f"{url}")}'
            response = RestAPIUtil.postAPIrequest(full_url, con, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test14_Change_DNOR_TimeoutConfiguration():
    global authorizationToken
    alarms = open(f'inputs/ATTMigration/DNOSTimeout.json')
    data = json.load(alarms)
    for con in data['configs']:
        urls = ["swarmTimeout", "downloadImagesTimeout", "installImagesTimeout"]
        for url in urls:
            full_url = f'https://{config.primaryDNOR}{apiurls.get(f"{url}")}'
            response = RestAPIUtil.postAPIrequest(full_url, con, authorizationToken)
            time.sleep(5)

@pytest.mark.addinputs
def test15_Change_DNOR_BackupConfiguration():
    global authorizationToken
    alarms = open(f'inputs/ATTMigration/BackupConfig.json')
    data = json.load(alarms)
    url = f'https://{config.primaryDNOR}{apiurls.get("dnor_backup_Settings")}'
    for con in data['configs']:
        response = RestAPIUtil.postAPIrequest(url, con, authorizationToken)

@pytest.mark.addinputs
def test15_Change_Network_BackupConfiguration():
    global authorizationToken
    alarms = open(f'inputs/ATTMigration/NetworkBackupConfig.json')
    data = json.load(alarms)
    url = f'https://{config.primaryDNOR}{apiurls.get("NCE_backup_Settings")}'
    for con in data['configs']:
        response = RestAPIUtil.postAPIrequest(url, con, authorizationToken)

def test16_check_if_all_containers_are_stable_primary_DNOR():
    DNORFunctions.check_containers_stability(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test17_check_if_all_containers_are_stable_secondary_DNOR():
    DNORFunctions.check_containers_stability(config.secondaryDNOR,config)
