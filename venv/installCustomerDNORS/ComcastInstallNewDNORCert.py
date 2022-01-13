import configparser
import pytest
import time
from Models import Functions, DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config
from Models.RestAPIUtil import *
from datetime import datetime, timedelta
from Models.postgresUtil import postgresUtil


versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-14.2.0/dnor_release.14.2.0.5-6e872b3468.tar'
config = Config(dnor='dn120-rnd1')

def test01_Validate_prerequisites_VMs_are_up_and_reachable_Primary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.primaryDNOR, config)

@pytest.mark.timeout(300)
def test02_Delete_Old_DNOR_on_Primary_VM():
    DNORFunctions.deleteDNOR(config.primaryDNOR, config)

def test03_Delete_data_folder_primaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.primaryDNOR, config)

@pytest.mark.dependency()
def test04_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.primaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.primaryDNOR,config)

def test05_reboot_Primary_DNOR_VM():
    assert Functions.rebootVM(config.primaryDNOR,config.primaryHost,config)

def test06_waiting_2_minutes_after_rebooting_VMS():
    time.sleep(120)

@pytest.mark.dependency(depends=['test04_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR'])
def test07_Generating_DNORcfg_File_for_Primary_DNOR():
    global primaryDNORIP
    primaryDNORIP = Functions.getDNORIP(config.primaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ComcastCert/dnor.cfg')
    cfgfile.set('CFGFILE','name',primaryDNORIP)
    cfgfile.set('CFGFILE', 'addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'primary')
    content=''
    for key in cfgfile['CFGFILE']:
        content+=f"{key}={cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.primaryDNOR,config,content)

@pytest.mark.timeout(300)
def test08_Delete_Old_DNOR_on_Primary_VM():
    DNORFunctions.deleteDNOR(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test07_Generating_DNORcfg_File_for_Primary_DNOR'])
def test09_Installing_The_Primary_DNOR():
    DNORFunctions.install_dnor(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
def test10_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
def test11_Enable_browser_certification_for_Primary_DNOR():
    DNORFunctions.enable_browser_certification(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
def test12_Enable_NGINX_for_Primary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs1
def test13_getting_authorizationToken():
    global authorizationToken
    print('getting authorizationToken')
    jsonfile = open('Requests/loginRequestBody.json')
    loginrequest = json.load(jsonfile)
    print(f"login request = {loginrequest}")
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/login'
    response = RestAPIUtil.postAPIrequest(url, loginrequest)
    assert (response['success'] == True)
    authorizationToken = response['token']
    assert (authorizationToken)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs
def test14_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/users/dnorUser'
    users = open('inputs/users/NCEusers.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs
def test15_add_images_to_DNOR():
    global authorizationToken
    images = open('venv/installCustomerDNORS/CustomerFiles/ComcastCert/images/images.json')
    data = json.load(images)
    dowloadimages = open('venv/installCustomerDNORS/CustomerFiles/ATTFFA/dowloadimage.json')
    downloadimagedata = json.load(dowloadimages)

    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/image-management'
    urlDowload = f'https://{config.primaryDNOR}.dev.drivenets.net/api/image-management/download-image'
    for image in data['dnos_images']:
        print(f'request1 = {image}')
        print(f'request2 = {downloadimagedata}')
        responseaddImage = RestAPIUtil.postAPIrequest(url, image, authorizationToken)
        downloadimagedata['id'] = responseaddImage['id']
        print(f'request3 = {downloadimagedata}')
        #responseaddImagelast = RestAPIUtil.postAPIrequestNew(urlDowload, downloadimagedata, authorizationToken)
        try:
            RestAPIUtil.postAPIrequest(urlDowload,downloadimagedata,authorizationToken)
        except Exception as e:
            continue

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs1
def test16_add_Tacacs_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Tacacs'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    tacacsServiceID = response1[0][0]
    print(f"Service id for type Tacacs = {tacacsServiceID}")
    global authorizationToken
    tacacs = open('inputs/tacacs/tacacs.json')
    data = json.load(tacacs)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/aaa/aaaConfiguration'
    for tacacs in data['tacacs']:
        tacacs['serviceId'] = tacacsServiceID
        print(f'request = {tacacs}')
        RestAPIUtil.postAPIrequest(url, tacacs, authorizationToken)
        #RestAPIUtil.postAPIrequest(url, tacacs)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs
def test17_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open('inputs/syslogs/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/syslog/settings'
    for syslogs in data['syslogs']:
        print(f'request = {syslogs}')
        RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs
def test18_add_sites_to_DNOR():
    global authorizationToken
    sites = open('inputs/sites/sites.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/sites'
    for site in data['sites']:
        print(f'request = {site}')
        RestAPIUtil.postAPIrequest(url, site, authorizationToken)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
@pytest.mark.addinputs
def test19_add_Radius_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Radius'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    radiusServiceID = response1[0][0]
    print(f"Service id for type Radius = {radiusServiceID}")
    global authorizationToken
    radius = open('inputs/radius/radius.json')
    data = json.load(radius)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/aaa/aaaConfiguration'
    for radius in data['radius']:
        radius['serviceId'] = radiusServiceID
        print(f'request = {radius}')
        RestAPIUtil.postAPIrequest(url, radius, authorizationToken)

@pytest.mark.dependency(depends=['test09_Installing_The_Primary_DNOR'])
def test20_Change_Yang_Version_Control_Date():
    query = 'select "createdAt" from yangs_version_control.yangs_version_control_db_models LIMIT 1'
    response = postgresUtil.execQueryPS(query, config.primaryDNOR)
    dateMinus = response[0][0] + timedelta(days=-14)
    queryupdateCreatedAt = f'UPDATE yangs_version_control.yangs_version_control_db_models '\
             f'SET "createdAt" = '+f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateCreatedAt,config.primaryDNOR)
    queryupdateUpdateddAt = f'UPDATE yangs_version_control.yangs_version_control_db_models ' \
                  f'SET "updatedAt" = ' + f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateUpdateddAt, config.primaryDNOR)