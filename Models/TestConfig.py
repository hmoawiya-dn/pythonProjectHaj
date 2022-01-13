import configparser
import os
from Models import DNOREnv

class TestConfig(DNOREnv.DNOREnvironment):

    def __init__(self,**kwargs):
        self.user = DNOREnv.DNOREnvironment.Shelluser
        self.password = DNOREnv.DNOREnvironment.Shellpassword
        self.NCC = kwargs.get('ncc')
        self.ncc0 = ''
        self.ncc1 = ''
        self.nccType = ''
        self.saltText = ''
        self.loaoadproperties(**kwargs)

    def loaoadproperties(self,**kwargs):
        print(f'self.ncc={self.NCC}')
        for arg in kwargs:
            print(f'hello = {arg} value = {kwargs.get(arg)}')
        # props = configparser.ConfigParser()
        # props.optionxform = str
        # fullpath = os.path.abspath(f"venv/NCCS/{self.NCC}/ncc.properties")
        # print(fullpath)
        # props.read(fullpath)
        # print(props.items('NCC'))
        # for name, value in props.items('NCC'):
        #     print(name, value)
        #     setattr(self, name, value)
        # print(dnorsIP)
