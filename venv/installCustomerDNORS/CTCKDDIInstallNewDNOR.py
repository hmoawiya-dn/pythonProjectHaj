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

# CTC KDDI have 2 nodes of dnor - primary and secondary
versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-14.2.0/dnor_release.14.2.0.5-6e872b3468.tar'
dnorVersion = "V14"
config = Config(dnor='dn0607')

def test01_Validate_prerequisites_VMs_are_up_and_reachable_Primary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test02_Validate_prerequisites_VMs_are_up_and_reachable_Secondary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test03_Validate_prerequisites_VMs_are_up_and_reachable_Tertiary_VM():
    DNORFunctions.validate_prerequisites_VMs_are_up_and_reachable(config.tertiaryDNOR, config)

@pytest.mark.timeout(300)
def test04_Delete_Old_DNOR_on_Primary_VM_current_version():
    DNORFunctions.deleteDNOR(config.primaryDNOR,config)

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
    DNORFunctions.deleteDNOR(config.primaryDNOR,config)

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

@pytest.mark.dependency()
def test17_Generating_DNORcfg_File_for_Primary_DNOR():
    global primaryDNORIP
    primaryDNORIP = Functions.getDNORIP(config.primaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/CTCKDDI/dnor.cfg')
    cfgfile.set('CFGFILE', 'addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'name', config.primaryDNOR)
    content=''
    for key in cfgfile['CFGFILE']:
        content+=f"{key}={cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.primaryDNOR,config,content)

def test18_Installing_The_Primary_DNOR():
    DNORFunctions.install_dnor(config.primaryDNOR,config)

def test19_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test20_Generating_DNORcfg_File_for_Secondary_DNOR():
    global secondaryDNORIP
    secondaryDNORIP = Functions.getDNORIP(config.secondaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/CTCKDDI/dnor.cfg')
    cfgfile.set('CFGFILE', 'name', config.secondaryDNOR)
    cfgfile.set('CFGFILE', 'addr', secondaryDNORIP)
    cfgfile.set('CFGFILE', 'primary_addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'secondary')
    content = ''
    for key in cfgfile['CFGFILE']:
        content += f"{key} = {cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.secondaryDNOR, config, content)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test21_Generating_dnorcfg_file_for_tertiary_DNOR():
        tertiaryDNORIP = Functions.getDNORIP(config.tertiaryDNOR,config)
        cfgfile = configparser.RawConfigParser()
        cfgfile.read('venv/installCustomerDNORS/CustomerFiles/CTCKDDI/dnor.cfg')

        cfgfile.set('CFGFILE', 'name', config.tertiaryDNOR)
        cfgfile.set('CFGFILE', 'addr', tertiaryDNORIP)
        cfgfile.set('CFGFILE', 'primary_addr', primaryDNORIP)
        cfgfile.set('CFGFILE', 'secondary_addr', secondaryDNORIP)
        cfgfile.set('CFGFILE', 'role', 'tertiary')
        content = ''
        for key in cfgfile['CFGFILE']:
            content += f"{key} = {cfgfile['CFGFILE'].get(key)}\n"
        Functions.postFileonDNOR(config.tertiaryDNOR, config, content)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test22_Installing_The_Secondary_DNOR():
    DNORFunctions.install_dnor(config.secondaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test23_Validate_all_services_are_UP_SecondaryDNOR():
    assert Functions.waitingforservices(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test24_Installing_The_Tertiary_DNOR():
    DNORFunctions.install_dnor(config.tertiaryDNOR, config)

def test25_Enable_browser_certification_for_Primary_DNOR():
    DNORFunctions.enable_browser_certification(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test26_Enable_browser_certification_for_Secondary_DNOR():
    DNORFunctions.enable_browser_certification(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test27_Enable_browser_certification_for_Tertiary_DNOR():
    DNORFunctions.enable_browser_certification(config.tertiaryDNOR,config)

def test28_Enable_NGINX_for_Primary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test29_Enable_NGINX_for_Secondary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test30_Enable_NGINX_for_Tertiary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.tertiaryDNOR,config)

@pytest.mark.addinputs
def test31_load_yamls_files():
    global apiurls
    with open(f'API_URLS/{dnorVersion}/API_urls.yaml') as file:
        apiurls = yaml.load(file,Loader=yaml.FullLoader)
    assert (apiurls)

@pytest.mark.addinputs
def test32_getting_authorizationToken():
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
def test33_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user, authorizationToken)
        assert (response['success'] == True)
        time.sleep(5)

@pytest.mark.addinputs
def test34_add_images_to_DNOR():
    global authorizationToken
    images = open(f'venv/installCustomerDNORS/CustomerFiles/CTCKDDI/images/images.json')
    data = json.load(images)
    dowmloadrequest = open('inputs/images/imagesDownload.json')
    dowloadjson = json.load(dowmloadrequest)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net{apiurls.get("add_images_url")}'
    if apiurls.get("download-image"):
        downloadurl = f'https://{config.primaryDNOR}.dev.drivenets.net{apiurls.get("download-image")}'
    for image in data['dnos_images']:
        try:
            response = RestAPIUtil.postAPIrequest(url, image, authorizationToken)
            time.sleep(5)
            if apiurls.get("download-image"):
                dowloadjson['id'] = response["id"]
                RestAPIUtil.postAPIrequest(downloadurl, dowloadjson, authorizationToken)
        except:
            continue

@pytest.mark.addinputs
def test35_add_sites_to_DNOR():
    global groupsiteID
    global authorizationToken
    sites = open(f'inputs/sites/{dnorVersion}/sites.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_sites_url")}'
    for site in data['sites']:
        site['groupId'] = groupsiteID
        print(f'request = {site}')
        response = RestAPIUtil.postAPIrequest(url, site, authorizationToken)
        time.sleep(5)

@pytest.mark.addinputs
def test36_add_Tacacs_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Tacacs'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    tacacsServiceID = response1[0][0]
    global authorizationToken
    tacacs = open(f'inputs/tacacs/{dnorVersion}/tacacs.json')
    data = json.load(tacacs)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_tacacs_url")}'
    for tacacs in data['tacacs']:
        print(f'request = {tacacs}')
        tacacs['serviceId'] = tacacsServiceID
        response = RestAPIUtil.postAPIrequest(url, tacacs, authorizationToken)
        time.sleep(5)

@pytest.mark.addinputs
def test37_add_Radius_servers_to_DNOR():
    TacacsQuery = "select id from aaa.aaa_types_db_models where type='Radius'"
    response1 = postgresUtil.execQueryPS(TacacsQuery,config.primaryDNOR)
    radiusServiceID = response1[0][0]
    global authorizationToken
    radius = open(f'inputs/radius/{dnorVersion}/radius.json')
    data = json.load(radius)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_radius_url")}'
    for radius in data['radius']:
        print(f'request = {radius}')
        radius['serviceId'] = radiusServiceID
        response = RestAPIUtil.postAPIrequest(url, radius, authorizationToken)
        time.sleep(5)

@pytest.mark.addinputs
def test38_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open(f'inputs/syslogs/{dnorVersion}/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_syslog_servers_url")}'
    for syslogs in data['syslogs']:
        print(f'request = {syslogs}')
        response = RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)
        time.sleep(5)