import logging
import subprocess

import paramiko


class RemoteUtil:

    def execSSHCommands(commandLine, user, password, server, config, port="2222"):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #commandLineNew = f'sshpass -p {password} {commandLine}'
        print(f"Executing on {user}@${server} command: " + commandLine)

        try:
            ssh.connect(server, port, user, password)
        except Exception as e:
            print(f"Failed to connect to {server} Error = {e}")
            if 'unable to connect' or 'error' or 'failed' or 'connection refused' in str(e).lower():
                try:
                    print(f"Failed to connect trying with port {config.ConnectionPort}")
                    ssh.connect(server, config.ConnectionPort, user, password)
                except Exception as e:
                    print(f"Failed to connect to {server} Error = {e}")
                    return "Connection to the server failed"


        stdin, stdout, stderr = ssh.exec_command(commandLine, get_pty=True)
        output=""
        for line in stdout.readlines():
            output += line
        if output:
            print(output)
            return output
        else:
            print("There was no output for this command")
            return "There was no output for this command"

    def openFileParamiko(user, password, server, config, filepath,port="22"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Reading file on {user}@${server}")
        print(f"file path = {filepath}")

        try:
            ssh.connect(server, port, user, password)
        except Exception as e:
            print(f"Failed to connect to {server} Error = {e}")
            if 'Unable to connect' in str(e):
                try:
                    print(f"Failed to connect trying with port {config.ConnectionPort}")
                    ssh.connect(server, config.ConnectionPort, user, password)
                except Exception as e:
                    print(f"Failed to connect to {server} Error = {e}")
                    return "Connection to the server failed"
        sftp = ssh.open_sftp()
        try:
            fileObject = sftp.open(filepath)
        except Exception as e:
            print(f"Failed to open file {filepath}")
            print(f"error = {str(e)}")
            return "failed"


        fileContent = ''
        try:
            for line in fileObject:
                fileContent+=line
        finally:
            fileObject.close()
        return fileContent

    def writeToFileParamiko(user, password, server, config, content, filepath, port="22"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Reading file on {user}@${server}")
        print(f"file path = {filepath}")

        try:
            ssh.connect(server, port, user, password)
        except Exception as e:
            print(f"Failed to connect to {server} Error = {e}")
            if 'Unable to connect' in str(e):
                try:
                    print(f"Failed to connect trying with port {config.ConnectionPort}")
                    ssh.connect(server, config.ConnectionPort, user, password)
                except Exception as e:
                    print(f"Failed to connect to {server} Error = {e}")
                    return "Connection to the server failed"
        sftp = ssh.open_sftp()
        fileObject = sftp.file(filepath,'a',-1)

        fileObject.write(content)
        fileObject.flush()
        sftp.close()
        ssh.close()

    def execSSHCommandsNew(commandLine, user, password, server, config, port="2222"):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Executing on {user}@${server} command: " + commandLine)

        try:
            ssh.connect(server, port, user, password)
        except Exception as e:
            print(f"Failed to connect to {server} Error = {e}")
            if 'unable to connect' or 'error' or 'failed' in str(e).lower():
                try:
                    print(f"Failed to connect trying with port {config.ConnectionPort}")
                    ssh.connect(server, config.ConnectionPort, user, password)
                except Exception as e:
                    print(f"Failed to connect to {server} Error = {e}")
                    return "Connection to the server failed"

        stdin, stdout, stderr = ssh.exec_command(commandLine, get_pty=True)

        def line_buffered(f):
            line_buf = ""
            while not f.channel.exit_status_ready():
                line_buf += f.read(1024).decode('utf-8', 'ignore')
                if line_buf.endswith('\n'):
                    yield line_buf
                    line_buf = ''

        for l in line_buffered(stdout):
            print(l)
