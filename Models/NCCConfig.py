import configparser
import os
from Models import DNOREnv

class NCCConfig(DNOREnv.DNOREnvironment):

    def __init__(self, NCC, dnorsIP):
        self.user = DNOREnv.DNOREnvironment.Shelluser
        self.password = DNOREnv.DNOREnvironment.Shellpassword
        self.NCC = NCC
        self.ncc0 = ''
        self.ncc1 = ''
        self.nccType = ''
        self.saltText = ''
        self.loaoadproperties(dnorsIP)

    def loaoadproperties(self,dnorsIP):
        props = configparser.ConfigParser()
        props.optionxform = str
        fullpath = os.path.abspath(f"venv/NCCS/{self.NCC}/ncc.properties")
        print(fullpath)
        props.read(fullpath)
        print(props.items('NCC'))
        for name, value in props.items('NCC'):
            print(name, value)
            setattr(self, name, value)
        self.saltText = f'dn-management-agent drivenets/clustername string\ndn-management-agent drivenets/saltmaster string {dnorsIP}\ndn-management-agent drivenets/vpetype select {self.nccType}\ndn-management-agent drivenets/model string X86'


