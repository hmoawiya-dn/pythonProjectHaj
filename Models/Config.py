import configparser
import os
from Models import DNOREnv

class Config(DNOREnv.DNOREnvironment):

    def __init__(self,**kwargs):
        self.user = DNOREnv.DNOREnvironment.Shelluser
        self.password = DNOREnv.DNOREnvironment.Shellpassword
        self.DNOR = ''
        self.NCC = ''
        if (kwargs.get('dnor')):
            self.DNOR = kwargs.get('dnor')
        self.primaryDNOR = ''
        self.secondaryDNOR = ''
        self.tertiaryDNOR = ''
        self.primaryHost = ''
        self.secondaryHost = ''
        self.tertiaryHost = ''
        self.dnorsIP = ''
        if (kwargs.get('ncc')):
            self.NCC = kwargs.get('ncc')
            self.dnorsIP = kwargs.get('dnorsIP')
        self.ncc0 = ''
        self.ncc1 = ''
        self.nccType = ''
        self.saltText = ''
        self.loaoadproperties()

    def loaoadproperties(self):
        props = configparser.ConfigParser()
        props.optionxform = str
        if (self.DNOR):
            fullpath = os.path.abspath(f"venv/DNORs/{self.DNOR}/dnor.properties")
            print(fullpath)
            props.read(fullpath)
            for name, value in props.items('DNOR'):
                print(name, value)
                setattr(self, name, value)
        if (self.NCC):
            fullpath = os.path.abspath(f"venv/NCCS/{self.NCC}/ncc.properties")
            print(fullpath)
            props.read(fullpath)
            for name, value in props.items('NCC'):
                print(name, value)
                setattr(self, name, value)
            self.saltText = f'dn-management-agent drivenets/clustername string\ndn-management-agent drivenets/saltmaster string {self.dnorsIP}\ndn-management-agent drivenets/vpetype select {self.nccType}\ndn-management-agent drivenets/model string X86'


