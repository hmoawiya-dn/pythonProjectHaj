import configparser
import pytest
import time
from Models import Functions, DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config
from Models.RestAPIUtil import *
from datetime import datetime, timedelta
from Models.postgresUtil import postgresUtil

versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-14.1.1/dnor_release.14.1.1.9-2f386f3993.tar'
config = Config(dnor='dn4349')

def test01_Validate_prerequisites_VMs_are_up_and_reachable_Primary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.primaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test02_Validate_prerequisites_VMs_are_up_and_reachable_Secondary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test03_Validate_prerequisites_VMs_are_up_and_reachable_Tertiary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.tertiaryDNOR, config)

def test04_Delete_data_folder_primaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.primaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test05_Delete_data_folder_secondaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test06_Delete_data_folder_tertiaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.tertiaryDNOR, config)

def test07_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.primaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test08_Downloading_TAR_file_and_Extract_it_to_The_Secondary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.secondaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test09_Downloading_TAR_file_and_Extract_it_to_The_Tertiary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.tertiaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.tertiaryDNOR,config)

@pytest.mark.timeout(300)
def test10_Delete_Old_DNOR_on_Primary_VM():
    DNORFunctions.deleteDNOR(config.primaryDNOR, config)

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test11_Delete_Old_DNOR_on_Secondary_VM():
    DNORFunctions.deleteDNOR(config.secondaryDNOR, config)

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test12_Delete_Old_DNOR_on_Tertiary_VM():
    DNORFunctions.deleteDNOR(config.tertiaryDNOR, config)

def test13_reboot_Primary_DNOR_VM():
    assert Functions.rebootVM(config.primaryDNOR,config.primaryHost,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test14_reboot_Secondary_DNOR_VM():
    assert Functions.rebootVM(config.secondaryDNOR,config.secondaryHost,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test15_reboot_Tertiary_DNOR_VM():
    assert Functions.rebootVM(config.tertiaryDNOR,config.tertiaryHost,config)

def test16_waiting_2_minutes_after_rebooting_VMS():
    time.sleep(120)

def test17_Generating_DNORcfg_File_for_Primary_DNOR():
    global primaryDNORIP
    primaryDNORIP = Functions.getDNORIP(config.primaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ComcastProduction/dnor.cfg')
    cfgfile.set('CFGFILE','name',primaryDNORIP)
    cfgfile.set('CFGFILE', 'addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'primary')
    content=''
    for key in cfgfile['CFGFILE']:
        content+=f"{key}={cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.primaryDNOR,config,content)

@pytest.mark.timeout(300)
def test18_Delete_Old_DNOR_on_Primary_VM():
    DNORFunctions.deleteDNOR(config.primaryDNOR, config)

def test19_Installing_The_Primary_DNOR():
    DNORFunctions.install_dnor(config.primaryDNOR, config)

def test20_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.addinputs
def test21_getting_authorizationToken():
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

@pytest.mark.addinputs
def test22_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/users/dnorUser'
    users = open('inputs/users/BulkClusters.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)

@pytest.mark.addinputs
def test23_add_images_to_DNOR():
    global authorizationToken
    images = open('venv/installCustomerDNORS/CustomerFiles/ATTFFA/images/images.json')
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

@pytest.mark.addinputs1
def test24_add_Tacacs_servers_to_DNOR():
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

@pytest.mark.addinputs
def test25_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open('inputs/syslogs/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/syslog/settings'
    for syslogs in data['syslogs']:
        print(f'request = {syslogs}')
        RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)

@pytest.mark.addinputs
def test26_add_sites_to_DNOR():
    global authorizationToken
    sites = open('inputs/sites/SiteGroups.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/sites'
    for site in data['sites']:
        print(f'request = {site}')
        RestAPIUtil.postAPIrequest(url, site, authorizationToken)

@pytest.mark.addinputs
def test27_add_Radius_servers_to_DNOR():
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

def test28_Change_Yang_Version_Control_Date():
    query = 'select "createdAt" from yangs_version_control.yangs_version_control_db_models LIMIT 1'
    response = postgresUtil.execQueryPS(query, config.primaryDNOR)
    dateMinus = response[0][0] + timedelta(days=-14)
    queryupdateCreatedAt = f'UPDATE yangs_version_control.yangs_version_control_db_models '\
             f'SET "createdAt" = '+f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateCreatedAt,config.primaryDNOR)
    queryupdateUpdateddAt = f'UPDATE yangs_version_control.yangs_version_control_db_models ' \
                  f'SET "updatedAt" = ' + f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateUpdateddAt, config.primaryDNOR)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test29_Generating_DNORcfg_File_for_Secondary_DNOR():
    global secondaryDNORIP
    secondaryDNORIP = Functions.getDNORIP(config.secondaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ComcastProduction/dnor.cfg')
    cfgfile.set('CFGFILE', 'name', secondaryDNORIP)
    cfgfile.set('CFGFILE', 'addr', secondaryDNORIP)
    cfgfile.set('CFGFILE', 'primary_addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'secondary')
    content = ''
    for key in cfgfile['CFGFILE']:
        content += f"{key}={cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.secondaryDNOR, config, content)

@pytest.mark.timeout(300)
def test30_Delete_Old_DNOR_on_Secondary_VM():
    DNORFunctions.deleteDNOR(config.secondaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test31_Installing_The_Secondary_DNOR():
    DNORFunctions.install_dnor(config.secondaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test32_Validate_all_services_are_UP_SecondaryDNOR():
    assert Functions.waitingforservices(config.secondaryDNOR,config)

def test33_Enable_browser_certification_for_Primary_DNOR():
    DNORFunctions.enable_browser_certification(config.primaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test34_Enable_browser_certification_for_Secondary_DNOR():
    DNORFunctions.enable_browser_certification(config.secondaryDNOR, config)

def test35_Enable_NGINX_for_Primary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.primaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test36_Enable_NGINX_for_Secondary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.secondaryDNOR, config)