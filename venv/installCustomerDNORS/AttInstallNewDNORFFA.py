import configparser
import pytest
import time
from Models import Functions, DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config
from Models.RestAPIUtil import *
from datetime import datetime, timedelta
from Models.postgresUtil import postgresUtil


versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-11.5.9/dnor_11.5.9.2-e757f02173.tar'
#versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-11.5.5/dnor_11.5.5.45-53e3bbb68e.tar'
config = Config(dnor='dn49')

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
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ATTFFA/dnor.cfg')
    cfgfile.set('CFGFILE','name',primaryDNORIP)
    cfgfile.set('CFGFILE', 'addr', primaryDNORIP)
    cfgfile.set('CFGFILE', 'role', 'primary')
    content=''
    for key in cfgfile['CFGFILE']:
        content+=f"{key} = {cfgfile['CFGFILE'].get(key)}\n"
    Functions.postFileonDNOR(config.primaryDNOR,config,content)

def test18_Installing_The_Primary_DNOR():
    cmd1= "cd deploy;sudo ./uninstall"
    cmd2= "cd deploy;sudo ./install"
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password,config.primaryDNOR,config)
    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password,config.primaryDNOR,config)
    assert ('error' not in response1)
    assert ('exception' not in response1)
    assert ('failed' not in response1)
    assert ('error' not in response2)
    assert ('exception' not in response2)
    assert ('failed' not in response2)
    assert ('Deployment has been completed successfully' in response2)

def test19_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test20_Generating_DNORcfg_File_for_Secondary_DNOR():
    global secondaryDNORIP
    secondaryDNORIP = Functions.getDNORIP(config.secondaryDNOR, config)
    cfgfile = configparser.RawConfigParser()
    cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ATTFFA/dnor.cfg')
    cfgfile.set('CFGFILE', 'name', secondaryDNORIP)
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
        cfgfile.read('venv/installCustomerDNORS/CustomerFiles/ATTFFA/dnor.cfg')

        cfgfile.set('CFGFILE', 'name', tertiaryDNORIP)
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
    cmd1= "cd deploy;sudo ./uninstall"
    cmd2= "cd deploy;sudo ./install"
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password,config.secondaryDNOR,config)
    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password,config.secondaryDNOR,config)
    assert ('error' not in response1)
    assert ('exception' not in response1)
    assert ('failed' not in response1)
    assert ('error' not in response2)
    assert ('exception' not in response2)
    assert ('failed' not in response2)
    assert ('Deployment has been completed successfully' in response2)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test23_Validate_all_services_are_UP_SecondaryDNOR():
    assert Functions.waitingforservices(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test24_Installing_The_Tertiary_DNOR():
    cmd1= "cd deploy;sudo ./uninstall"
    cmd2= "cd deploy;sudo ./install"
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password,config.tertiaryDNOR,config)
    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password,config.tertiaryDNOR,config)
    assert ('error' not in response1)
    assert ('exception' not in response1)
    assert ('failed' not in response1)
    assert ('error' not in response2)
    assert ('exception' not in response2)
    assert ('failed' not in response2)
    assert ('Deployment has been completed successfully' in response2)

def test25_Enable_browser_certification_for_Primary_DNOR():
    cmd0= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/fullchain.pem -O dev.drivenets.net.crt"
    cmd1= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/privkey.pem -O dev.drivenets.net.key"

    response0 = RemoteUtil.execSSHCommands(cmd0, config.user, config.password, config.primaryDNOR, config)
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, config.primaryDNOR, config)

    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response0)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response1)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test26_Enable_browser_certification_for_Secondary_DNOR():
    cmd0= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/fullchain.pem -O dev.drivenets.net.crt"
    cmd1= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/privkey.pem -O dev.drivenets.net.key"
    response0 = RemoteUtil.execSSHCommands(cmd0, config.user, config.password, config.secondaryDNOR, config)
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, config.secondaryDNOR, config)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response0)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response1)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test27_Enable_browser_certification_for_Tertiary_DNOR():
    cmd0= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/fullchain.pem -O dev.drivenets.net.crt"
    cmd1= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/privkey.pem -O dev.drivenets.net.key"
    response0 = RemoteUtil.execSSHCommands(cmd0, config.user, config.password, config.tertiaryDNOR, config)
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, config.tertiaryDNOR, config)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response0)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response1)

def test28_Enable_NGINX_for_Primary_DNOR():
        contaonerName = Functions.getNGINXcontainerName(config,config.primaryDNOR)
        lineDelete1 = "10.0.0.0"
        lineDelete2 = "deny"
        reload = "nginx -s reload"
        sedCMD1 = f"sed -ire '/{lineDelete1}/d' /etc/nginx/nginx.conf"
        sedCMD2 = f"sed -ire '/{lineDelete2}/d' /etc/nginx/nginx.conf"
        cmd1 = f"docker exec -it {contaonerName} {sedCMD1}"
        cmd2 = f"docker exec -it {contaonerName} {sedCMD2}"
        cmd3 = f"docker exec -it {contaonerName} {reload}"
        RemoteUtil.execSSHCommands(cmd1,config.user,config.password,config.primaryDNOR,config)
        RemoteUtil.execSSHCommands(cmd2,config.user,config.password,config.primaryDNOR,config)
        response3= RemoteUtil.execSSHCommands(cmd3,config.user,config.password,config.primaryDNOR,config)
        assert ('signal process started'in response3)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test29_Enable_NGINX_for_Secondary_DNOR():
    contaonerName = Functions.getNGINXcontainerName(config, config.secondaryDNOR)
    lineDelete1 = "10.0.0.0"
    lineDelete2 = "deny"
    reload = "nginx -s reload"
    sedCMD1 = f"sed -ire '/{lineDelete1}/d' /etc/nginx/nginx.conf"
    sedCMD2 = f"sed -ire '/{lineDelete2}/d' /etc/nginx/nginx.conf"
    cmd1 = f"docker exec -it {contaonerName} {sedCMD1}"
    cmd2 = f"docker exec -it {contaonerName} {sedCMD2}"
    cmd3 = f"docker exec -it {contaonerName} {reload}"
    RemoteUtil.execSSHCommands(cmd1, config.user, config.password, config.secondaryDNOR, config)
    RemoteUtil.execSSHCommands(cmd2, config.user, config.password, config.secondaryDNOR, config)
    response3 = RemoteUtil.execSSHCommands(cmd3, config.user, config.password, config.secondaryDNOR, config)
    assert ('signal process started' in response3)
@pytest.mark.addinputs1
def test30_getting_authorizationToken():
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
def test31_add_users_to_DNOR():
    global authorizationToken
    print(f'authorizationToken={authorizationToken}')
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/users/dnorUser'
    users = open('inputs/users/NCEusers.json')
    data = json.load(users)
    for user in data['dnorusers']:
        print(f'request = {user}')
        response = RestAPIUtil.postAPIrequest(url, user,authorizationToken)
        assert (response['success'] == True)
@pytest.mark.addinputs
def test32_add_images_to_DNOR():
    global authorizationToken
    images = open('venv/installCustomerDNORS/CustomerFiles/ATTFFA/images/images.json')
    data = json.load(images)

    dowloadimages = open('venv/installCustomerDNORS/CustomerFiles/ATTFFA/dowloadimage.json')
        #cache = dowloadimages.read()
    downloadimagedata = json.load(dowloadimages)
        #downloadimagedata = json.load(dowloadimages)
        #downloadimagedatareq = downloadimagedata['downloadimage']

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
def test33_add_Tacacs_servers_to_DNOR():
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
def test34_add_Syslog_servers_to_DNOR():
    global authorizationToken
    syslogs = open('inputs/syslogs/syslogs.json')
    data = json.load(syslogs)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/syslog/settings'
    for syslogs in data['syslogs']:
        print(f'request = {syslogs}')
        RestAPIUtil.postAPIrequest(url, syslogs, authorizationToken)

@pytest.mark.addinputs
def test35_add_sites_to_DNOR():
    global authorizationToken
    sites = open('inputs/sites/SiteGroups.json')
    data = json.load(sites)
    url = f'https://{config.primaryDNOR}.dev.drivenets.net/api/sites'
    for site in data['sites']:
        print(f'request = {site}')
        RestAPIUtil.postAPIrequest(url, site, authorizationToken)

def test36_Change_Yang_Version_Control_Date():
    query = 'select "createdAt" from yangs_version_control.yangs_version_control_db_models LIMIT 1'
    response = postgresUtil.execQueryPS(query, config.primaryDNOR)
    dateMinus = response[0][0] + timedelta(days=-14)
    queryupdateCreatedAt = f'UPDATE yangs_version_control.yangs_version_control_db_models '\
             f'SET "createdAt" = '+f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateCreatedAt,config.primaryDNOR)
    queryupdateUpdateddAt = f'UPDATE yangs_version_control.yangs_version_control_db_models ' \
                  f'SET "updatedAt" = ' + f"'{dateMinus}';"
    postgresUtil.updateTable(queryupdateUpdateddAt, config.primaryDNOR)