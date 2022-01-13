import time

from Models.RemoteUtil import RemoteUtil

def checkIfVersionExist(config, dn, fullVersion):
    version = str(fullVersion).split("/")[-1]
    cmd =f"sudo ls | grep {version} | wc -l"
    response = RemoteUtil.execSSHCommands(cmd, config.user,config.password, dn, config)
    if (response.strip()=="0"):
        print("Looks like that the Version isn't exist on the server ... Going to dowenload it...")
        cmd2 = f"sudo wget {fullVersion}"
        RemoteUtil.execSSHCommands(cmd2, config.user,config.password, dn,config)
    response = RemoteUtil.execSSHCommands(cmd, config.user,config.password, dn, config)
    assert (str(response).strip() >= "1")
    return version

def rebootVM(vm, host, config):
        cmd = f"sudo virsh reboot {vm}"
        response = RemoteUtil.execSSHCommands(cmd, config.HostUser,config.HostPassword, host,config)
        assert (f'Domain {vm} is being rebooted' in response)
        return True

def getDNORIP(dnor, config):
    cmd = 'hostname -I'
    response = RemoteUtil.execSSHCommands(cmd,config.user,config.password,dnor,config)
    return response.split()[0]

def waitingforservices(dnor, config):
    cmd = 'sudo docker service ls'
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    out = 0
    while (not validateServices(response)):
        if out>60:
            return False
        print("Waiting 10 seconds more for all services to be up")
        time.sleep(10)
        response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
        out+=1
    return True

def validateServices(services):
    servicesLinesSize = len(str(services).splitlines())
    print(f"lines count = {servicesLinesSize}")
    for i in range(1, servicesLinesSize):
        line = str(services).splitlines()[i]
        serviceName = line.split()[1]
        replicas = line.split()[3]
        rep1 = replicas.split("/")[0]
        rep2 = replicas.split("/")[1]
        print(f'service name = {serviceName} replicas = {replicas}')
        if int(rep1) != int(rep2):
            print(f'The service - {serviceName} still not up fully')
            return False
    return True

def isSSHpass(dnor, config):
    cmd = "sshpass"
    response = RemoteUtil.execSSHCommands(cmd,config.user,config.password,dnor,config)
    if 'not found' in response:
        cmd = 'sudo apt install sshpass'
        response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    else:
        return True
    cmd = "sshpass"
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    if 'not found' in response:
        return False
    else:
        return True

def getNGINXcontainerName(config, dnor):
    cmd = "sudo docker ps --filter 'name==*nginx*'"
    response = RemoteUtil.execSSHCommands(cmd,config.user,config.password,dnor,config)
    line = response.splitlines()[1]
    containerName = line.split()[-1]
    print(f"The NGINX contaner name: {containerName}")
    assert (containerName)
    return containerName

def postFileonDNOR(dnor,config,filecontent):
    cmd = f'cd deploy; echo "{filecontent}" > dnor.cfg'
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)

def converCFGtoStrign(cfgfile,section):
    content=''
    for name, value in cfgfile.items('CFGFILE'):
        content += f'{name}={value}\n'
        #print(f"key={name} value = {value}")
        #content+=line
    return content
    #print(content)

