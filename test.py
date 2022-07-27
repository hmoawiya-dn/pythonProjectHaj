import time
import logging
import sys

from Models.Config import Config
from Models.RemoteUtil import RemoteUtil


def test_haj():
    print(f"hello {config.primaryDNOR}")
    cmd = 'sshpass -p drivenets sudo ls | grep {version} | wc -l'
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, config.primaryDNOR, config)
    print(f"response =  {response}")

