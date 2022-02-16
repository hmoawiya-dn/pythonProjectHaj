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


versionLink = 'https://jenkins2.dev.drivenets.net/job/comet/job/dnor_eng_16.0.0/4/'
dnorVersion = "V16"
gdnor = False
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

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test05_Delete_Old_DNOR_on_Secondary_VM_current_version():
    DNORFunctions.deleteDNOR(config.secondaryDNOR,config)

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test06_Delete_Old_DNOR_on_Tertiary_VM_current_version():
    DNORFunctions.deleteDNOR(config.tertiaryDNOR, config)

def test07_Delete_data_folder_primaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test08_Delete_data_folder_secondaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test09_Delete_data_folder_tertiaryDNOR():
    DNORFunctions.delete_folders_from_DNOR(config.tertiaryDNOR, config)

def test10_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.primaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test11_Downloading_TAR_file_and_Extract_it_to_The_Secondary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.secondaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test12_Downloading_TAR_file_and_Extract_it_to_The_Tertiary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config,config.tertiaryDNOR,versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae,config.tertiaryDNOR,config)

@pytest.mark.timeout(300)
def test13_Delete_Old_DNOR_on_Primary_VM():
    DNORFunctions.deleteDNOR(config.primaryDNOR,config)

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test14_Delete_Old_DNOR_on_Secondary_VM():
    DNORFunctions.deleteDNOR(config.secondaryDNOR,config)

@pytest.mark.timeout(300)
@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test15_Delete_Old_DNOR_on_Tertiary_VM():
    DNORFunctions.deleteDNOR(config.tertiaryDNOR, config)

def test16_reboot_Primary_DNOR_VM():
    assert Functions.rebootVM(config.primaryDNOR,config.primaryHost,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test17_reboot_Secondary_DNOR_VM():
    assert Functions.rebootVM(config.secondaryDNOR,config.secondaryHost,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test18_reboot_Tertiary_DNOR_VM():
    assert Functions.rebootVM(config.tertiaryDNOR,config.tertiaryHost,config)

def test19_waiting_2_minutes_after_rebooting_VMS():
    time.sleep(120)

@pytest.mark.dependency()
def test20_Generating_DNORcfg_File_for_Primary_DNOR():
    global primaryDNORIP
    primaryDNORIP = Functions.getDNORIP(config.primaryDNOR,config)
    cfgfile = configparser.RawConfigParser()
    cfgFilecontent = '[CFGFILE]\n'
    cmd = 'cd deploy;sudo cp dnor.cfg.template dnor.cfg'
    responsecopy = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.primaryDNOR, config)
    filecontent = RemoteUtil.openFileParamiko(config.user, config.password, config.primaryDNOR,config,filepath='/home/dn/deploy/dnor.cfg')
    cmd ='cd deploy;sudo rm dnor.cfg'
    responseDelete = RemoteUtil.execSSHCommands(cmd,config.user,config.password,config.primaryDNOR,config)
    cfgFilecontent += filecontent
    cfgfile.read_string(cfgFilecontent)
    cfgfile.set('CFGFILE', 'name', config.primaryDNOR)
    cfgfile.set('CFGFILE', 'addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'primary')

    cfgFilestring = Functions.converCFGtoStrign(cfgfile, 'CFGFILE')
    RemoteUtil.writeToFileParamiko(config.user,config.password,config.primaryDNOR,config,cfgFilestring,filepath='/home/dn/deploy/dnor.cfg')
    assert (responseDelete == 'There was no output for this command')
    assert (responsecopy == 'There was no output for this command')
    assert ('failed' not in filecontent)


def test21_Installing_The_Primary_DNOR():
    DNORFunctions.install_dnor(config.primaryDNOR,config)

def test22_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test23_get_keep_alive_token_from_primaryDNOR():
    global keeepAliveToken
    cfgfile = configparser.RawConfigParser()
    cfgFilecontent = '[CFGFILE]\n'
    filecontent = RemoteUtil.openFileParamiko(config.user, config.password, config.primaryDNOR, config,filepath='/home/dn/deploy/dnor.cfg')
    cfgFilecontent += filecontent
    cfgfile.read_string(cfgFilecontent)
    keeepAliveToken = cfgfile.get('CFGFILE', 'keepalive_token')
    assert keeepAliveToken

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test24_Generating_DNORcfg_File_for_Secondary_DNOR():
    global secondaryDNORIP
    secondaryDNORIP = Functions.getDNORIP(config.secondaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgFilecontent = '[CFGFILE]\n'
    cmd = 'cd deploy;cp dnor.cfg.template dnor.cfg'
    responsecopy = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.secondaryDNOR, config)
    filecontent = RemoteUtil.openFileParamiko(config.user, config.password, config.secondaryDNOR, config,filepath='/home/dn/deploy/dnor.cfg')
    cmd = 'cd deploy;sudo rm dnor.cfg'
    responseDelete = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.secondaryDNOR, config)
    cfgFilecontent += filecontent
    cfgfile.read_string(cfgFilecontent)
    cfgfile.set('CFGFILE', 'name', config.secondaryDNOR)
    cfgfile.set('CFGFILE', 'addr', secondaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'secondary')
    cfgfile.set('CFGFILE', 'keepalive_token', keeepAliveToken)
    cfgfile.set('CFGFILE', 'primary_addr', primaryDNORIP)
    cfgFilestring = Functions.converCFGtoStrign(cfgfile, 'CFGFILE')
    RemoteUtil.writeToFileParamiko(config.user, config.password, config.secondaryDNOR, config, cfgFilestring,filepath='/home/dn/deploy/dnor.cfg')
    assert (responseDelete == 'There was no output for this command')
    assert (responsecopy == 'There was no output for this command')
    assert ('failed' not in filecontent)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test25_Generating_dnorcfg_file_for_tertiary_DNOR():
    tertiaryDNORIP = Functions.getDNORIP(config.tertiaryDNOR,config)
    cfgfile = configparser.RawConfigParser()
    cfgFilecontent = '[CFGFILE]\n'
    cmd = 'cd deploy;cp dnor.cfg.template dnor.cfg'
    responsecopy = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.tertiaryDNOR, config)
    filecontent = RemoteUtil.openFileParamiko(config.user, config.password, config.tertiaryDNOR, config,filepath='/home/dn/deploy/dnor.cfg')
    cmd = 'cd deploy;sudo rm dnor.cfg'
    responseDelete = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.tertiaryDNOR, config)
    cfgFilecontent += filecontent
    cfgfile.read_string(cfgFilecontent)
    cfgfile.set('CFGFILE', 'name', config.tertiaryDNOR)
    cfgfile.set('CFGFILE', 'addr', tertiaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'tertiary')
    cfgfile.set('CFGFILE', 'keepalive_token', keeepAliveToken)
    cfgfile.set('CFGFILE', 'primary_addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'secondary_addr', secondaryDNORIP)
    cfgFilestring = Functions.converCFGtoStrign(cfgfile, 'CFGFILE')
    RemoteUtil.writeToFileParamiko(config.user, config.password, config.tertiaryDNOR, config, cfgFilestring,filepath='/home/dn/deploy/dnor.cfg')
    assert (responseDelete == 'There was no output for this command')
    assert (responsecopy == 'There was no output for this command')
    assert ('failed' not in filecontent)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test26_Installing_The_Secondary_DNOR():
    DNORFunctions.install_dnor(config.secondaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test27_Validate_all_services_are_UP_SecondaryDNOR():
    assert Functions.waitingforservices(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test28_Installing_The_Tertiary_DNOR():
    DNORFunctions.install_dnor(config.tertiaryDNOR, config)

def test29_Enable_browser_certification_for_Primary_DNOR():
    DNORFunctions.enable_browser_certification(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test30_Enable_browser_certification_for_Secondary_DNOR():
    DNORFunctions.enable_browser_certification(config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test31_Enable_browser_certification_for_Tertiary_DNOR():
    DNORFunctions.enable_browser_certification(config.tertiaryDNOR, config)

def test31_Enable_NGINX_for_Primary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test32_Enable_NGINX_for_Secondary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.secondaryDNOR, config)

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test33_load_yamls_files():
    global apiurls
    with open(f'API_URLS/{dnorVersion}/API_urls.yaml') as file:
        apiurls = yaml.load(file,Loader=yaml.FullLoader)
    assert (apiurls)

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test34_getting_authorizationToken():
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
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test35_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}{apiurls.get("add_users_url")}'
    users = open(f'inputs/users/{dnorVersion}/users.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)
        time.sleep(5)

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test36_add_images_to_DNOR():
    global authorizationToken
    images = open(f'inputs/images/{dnorVersion}/images.json')
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

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test37_add_sites_to_DNOR():
    global authorizationToken
    sites = open(f'inputs/sites/{dnorVersion}/sites.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_sites_url")}'
    for site in data['sites']:
        print(f'request = {site}')
        response = RestAPIUtil.postAPIrequest(url, site, authorizationToken)
        time.sleep(5)

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test38_add_Tacacs_servers_to_DNOR():
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
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test39_add_Radius_servers_to_DNOR():
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
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test40_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open(f'inputs/syslogs/{dnorVersion}/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_syslog_servers_url")}'
    for syslogs in data['syslogs']:
        print(f'request = {syslogs}')
        response = RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)
        time.sleep(5)

@pytest.mark.addinputs
@pytest.mark.skipif((bool(gdnor)), reason="Installing GDNOR")
def test41_add_NCE_users_group_to_DNOR():
    global authorizationToken
    ncegroup = open(f'inputs/NCEusers/{dnorVersion}/NCEusers.json')
    data = json.load(ncegroup)
    url = f'https://{config.primaryDNOR}{apiurls.get("add_nce_user_group")}'
    for group in data['ncegroups']:
        print(f'request = {group}')
        response = RestAPIUtil.postAPIrequest(url, group, authorizationToken)
        time.sleep(5)