from datetime import time
import time

from Models import Functions
from Models.RemoteUtil import RemoteUtil
from Models.postgresUtil import postgresUtil


def deleteDNOR(dnor,config):
    for i in ['First', 'Second', 'Third']:
        print(f'Deleting the Old dnor for the {i} Time')
        cmd = 'cd deploy;sudo ./uninstall'
        response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
        if 'please use the -s ' in response:
            cmd = 'cd deploy;sudo ./uninstall -s'
            response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)

    cmd5 = "sudo docker ps -aq | xargs -r docker rm -f"
    cmd6 = "sudo docker system prune --all --volumes -f"
    #cmd7 = "sudo docker ps -aq | xargs docker rm -f"
    response5 = RemoteUtil.execSSHCommands(cmd5, config.user, config.password, dnor, config)
    response6 = RemoteUtil.execSSHCommands(cmd6, config.user, config.password, dnor, config)
    #response7 = RemoteUtil.execSSHCommands(cmd7, config.user, config.password, dnor, config)

    assert ('error' not in response.lower())
    assert ('exception' not in response.lower())
    assert ('failed' not in response.lower())
    assert ('not found' not in response.lower())
    assert (('Node left the swarm' in response) or ('The node is not a part of swarm cluster' in response) or ('The node is not a part of cluster' in response))
    assert ('Total reclaimed space' in response)
    assert ('permission denied' not in response5)
    assert ('permission denied' not in response6)
    #assert ('permission denied' not in response7)

def check_containers_stability(dnor,config):
    cmd1 = 'timeout 5 docker events --filter event=restart --since=5m'
    cmd2 = 'timeout 5 docker events --filter event=destroy --since=5m'
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, dnor, config)
    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password, dnor, config)
    assert (response1 == 'There was no output for this command')
    assert (response2 == 'There was no output for this command')

def delete_folders_from_DNOR(dnor,config):
    cmd1 = "sudo rm -r /data/*"
    cmd2 = "sudo rm -rf /opt/drivenets"
    cmd3 = "sudo rm -rf /opt/db-backup"
    cmd4 = "sudo rm -rf deploy/"

    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, dnor, config)
    if ('Directory not empty' in response1):
        response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, dnor, config)

    response2 = RemoteUtil.execSSHCommands(cmd2, config.user, config.password, dnor, config)
    response3 = RemoteUtil.execSSHCommands(cmd3, config.user, config.password, dnor, config)
    response4 = RemoteUtil.execSSHCommands(cmd4, config.user, config.password, dnor, config)
    assert (response1 == 'There was no output for this command' or "cannot remove '/data/*': No such file or directory" in response1)
    assert response2 == 'There was no output for this command'
    assert response3 == 'There was no output for this command'
    assert response4 == 'There was no output for this command'

def extract_tar_file_on_DNOR(versionFilenmae,dnor,config):
    cmd = f"tar xvf {versionFilenmae}"
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)

    if ( ('Cannot open: File' in response) or ('Operation not permitted' in response)):
        cmd = f"sudo tar xvf {versionFilenmae}"
        response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)

    assert ('error' not in response.lower())
    assert ('exception' not in response.lower())
    assert ('failed' not in response.lower())

def install_dnor(dnor,config):
    cmd = "cd deploy;sudo ./install"
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    assert ('error' not in response.lower())
    assert ('exception' not in response.lower())
    assert ('failed' not in response.lower())
    assert ('Deployment has been completed successfully' in response)

def enable_browser_certification(dnor,config):
    cmd0= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/fullchain.pem -O dev.drivenets.net.crt"
    cmd1= "wget http://minioio.dev.drivenets.net:9000/devops/letsencrypt/*.dev.drivenets.net/privkey.pem -O dev.drivenets.net.key"
    response0 = RemoteUtil.execSSHCommands(cmd0, config.user, config.password, dnor, config)
    response1 = RemoteUtil.execSSHCommands(cmd1, config.user, config.password, dnor, config)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response0)
    assert (('100%' and 'dev.drivenets.net.crt' and 'saved') in response1)

def enable_NGINX_for_DNOR(dnor,config):
    contaonerName = Functions.getNGINXcontainerName(config, dnor)
    lineDelete1 = "10.0.0.0"
    lineDelete2 = "deny"
    reload = "nginx -s reload"
    sedCMD1 = f"sed -ire '/{lineDelete1}/d' /etc/nginx/nginx.conf"
    sedCMD2 = f"sed -ire '/{lineDelete2}/d' /etc/nginx/nginx.conf"
    cmd1 = f"sudo docker exec -it {contaonerName} {sedCMD1}"
    cmd2 = f"sudo docker exec -it {contaonerName} {sedCMD2}"
    cmd3 = f"sudo docker exec -it {contaonerName} {reload}"
    RemoteUtil.execSSHCommands(cmd1, config.user, config.password, dnor, config)
    RemoteUtil.execSSHCommands(cmd2, config.user, config.password, dnor, config)
    response3 = RemoteUtil.execSSHCommands(cmd3, config.user, config.password, dnor, config)
    assert ('signal process started' in response3)

def validate_prerequisites_VMs_are_up_and_reachable(dnor,config):
    cmd = f'sudo virsh list --all | grep -w {dnor}'
    dnorHost = str(dnor).split('-')[0]
    response = RemoteUtil.execSSHCommands(cmd, config.HostUser, config.HostPassword, dnorHost, config)
    response = response.split()[-1]
    if (response.lower() != 'running'):
        print(f"The vm status on the Host = {response}")
        print(f"Starting it ...")
        cmd = f"sudo virsh start {dnor}"
        RemoteUtil.execSSHCommands(cmd, config.HostUser, config.HostPassword, dnorHost, config)
        print("Waiting 2 Mins after statrting the VM")
        time.sleep(120)
    cmd = f'sudo virsh list --all | grep {dnor}'
    response = RemoteUtil.execSSHCommands(cmd, config.HostUser, config.HostPassword, dnorHost, config)
    response = response.split()[-1]
    assert (response.lower()=='running')
    cmd = 'pwd'
    response = RemoteUtil.execSSHCommands(cmd, config.user,config.password,dnor,config)
    print(f"response={str(response).strip()}")
    assert str(response).strip()=='/home/dn'

    # cmd = 'sudo sshpass -V'
    # response = RemoteUtil.execSSHCommands(cmd, config.user,config.password,dnor,config)
    # if ('not found' in (str(response).strip().lower())):
    #     cmd2='sudo apt install sshpass'
    #     RemoteUtil.execSSHCommands(cmd2, config.user, config.password, dnor, config)

    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    assert ('not found' not in (str(response).strip().lower()))



def validate_dnor_is_Cold_statu(dnor,config):
    cmd = f'sudo docker service ls | grep 1/1 | wc -l'
    response = RemoteUtil.execSSHCommands(cmd, config.user, config.password, dnor, config)
    assert int(response) <= 10

def get_groupid_from_DNOR(dnor):
    query = 'select id from nce_management.nce_group_models'
    response = postgresUtil.execQueryPS(query, dnor)
    print(f"Group id = {response[0][0]}")
    return response[0][0]

def get_siteid_from_DNOR(dnor,siteName):
    query = f"select id from nce_management.sites where name='{str(siteName).upper()}'"
    response = postgresUtil.execQueryPS(query, dnor)
    print(f"Site id for site {str(siteName).upper()} = {response[0][0]}")
    return response[0][0]