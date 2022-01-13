from datetime import time
import time

from Models import Functions
from Models.RemoteUtil import RemoteUtil

def change_NCCC_config(ncc,config):
    cmd0 = f'echo "{config.saltText}" > /tmp/debconf.dn'
    cmd1 = "sudo /usr/bin/debconf-set-selections /tmp/debconf.dn"
    cmd2 = "sudo DEBIAN_FRONTEND=noninteractive /usr/sbin/dpkg-reconfigure dn-management-agent"
    response0 = RemoteUtil.execSSHCommands(cmd0, config.user, config.password, ncc, config)
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, ncc, config)
    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password, ncc, config)
    assert response0 == 'There was no output for this command'
    assert response1 == 'There was no output for this command'
    assert response2 == 'There was no output for this command'