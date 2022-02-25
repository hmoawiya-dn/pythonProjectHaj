import pytest
from Models import Functions, DNORFunctions
from Models.RemoteUtil import *
from Models.Config import Config

versionLink = 'http://minioio.dev.drivenets.net:9000/dnor/comet-dnor-rel-14.2.1/dnor_release.14.2.1.1-cef5b4b386.tar'
config = Config(dnor='dn56-dev1')

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason=f"need to have scondary dnor configured on dnor.proprerties file")
def test01_Validate_Secondary_DNOR_is_in_Cold():
    DNORFunctions.validate_dnor_is_Cold_statu(config.secondaryDNOR,config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test02_Validate_Tertiary_DNOR_is_in_Cold():
    DNORFunctions.validate_dnor_is_Cold_statu(config.tertiaryDNOR,config)

@pytest.mark.dependency()
def test03_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config, config.primaryDNOR, versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae, config.primaryDNOR, config)

@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test04_Downloading_TAR_file_and_Extract_it_to_The_Secondary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config, config.secondaryDNOR, versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae, config.secondaryDNOR, config)

@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test05_Downloading_TAR_file_and_Extract_it_to_The_Tertiary_DNOR():
    versionFilenmae = Functions.checkIfVersionExist(config, config.tertiaryDNOR, versionLink)
    DNORFunctions.extract_tar_file_on_DNOR(versionFilenmae, config.tertiaryDNOR, config)

@pytest.mark.dependency(depends=['test03_Downloading_TAR_file_and_Extract_it_to_The_Primary_DNOR'])
def test06_Installing_and_upgrading_The_Primary_DNOR():
    DNORFunctions.install_dnor(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test06_Installing_and_upgrading_The_Primary_DNOR'])
def test07_Validate_all_services_are_UP_PrimaryDNOR():
    assert Functions.waitingforservices(config.primaryDNOR,config)

@pytest.mark.dependency(depends=['test06_Installing_and_upgrading_The_Primary_DNOR'])
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test08_Installing_and_upgrading_The_Secondary_DNOR():
    DNORFunctions.install_dnor(config.secondaryDNOR, config)

@pytest.mark.dependency(depends=['test08_Installing_and_upgrading_The_Secondary_DNOR'])
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test09_Validate_all_services_are_UP_SecondaryDNOR():
    DNORFunctions.validate_dnor_is_Cold_statu(config.secondaryDNOR,config)

@pytest.mark.dependency(depends=['test08_Installing_and_upgrading_The_Secondary_DNOR'])
@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test10_Installing_and_upgrading_The_Tertiary_DNOR():
    DNORFunctions.install_dnor(config.tertiaryDNOR, config)

@pytest.mark.dependency(depends=['test10_Installing_and_upgrading_The_Tertiary_DNOR'])
@pytest.mark.skipif((config.tertiaryDNOR=='na') or (not config.tertiaryDNOR), reason="need to have tertiary dnor configured on dnor.proprerties file")
def test11_Validate_all_services_are_UP_TertiaryDNOR():
    DNORFunctions.validate_dnor_is_Cold_statu(config.tertiaryDNOR,config)

@pytest.mark.dependency(depends=['test06_Installing_and_upgrading_The_Primary_DNOR'])
def test12_Enable_NGINX_for_Primary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.primaryDNOR, config)

@pytest.mark.dependency(depends=['test08_Installing_and_upgrading_The_Secondary_DNOR'])
@pytest.mark.skipif((config.secondaryDNOR=='na') or (not config.secondaryDNOR), reason="need to have scondary dnor configured on dnor.proprerties file")
def test13_Enable_NGINX_for_Secondary_DNOR():
    DNORFunctions.enable_NGINX_for_DNOR(config.secondaryDNOR, config)