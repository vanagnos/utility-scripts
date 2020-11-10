"""
script for running commands over ssh on a host using an intermediate jump server
"""
import functools
import paramiko


def with_ssh(fun):
    """ decorator for running a command over ssh. """
    @functools.wraps(fun)
    def func(self, *args, **kwargs):
        if self.target is None:
            self.connect_to_target()
        try:
            return fun(self, *args, **kwargs)
        finally:
            if self.keep_alive is False:
                self.close()
                self.jumpserver = None
                self.target = None
    return func


class SSHUtility(object):
    """
    class for running commands over ssh on a host using an intermediate jump server
    """

    def __init__(self,
                 jumpserver_ip,
                 jumpserver_private_ip,
                 jumpserver_username,
                 jumpserver_password,
                 target_ip,
                 target_username,
                 target_password,
                 port=22,
                 keep_alive=False):

        self.jumpserver_ip = jumpserver_ip
        self.jumpserver_private_ip = jumpserver_private_ip
        self.jumpserver_username = jumpserver_username
        self.jumpserver_password = jumpserver_password
        self.target_ip = target_ip
        self.target_username = target_username
        self.target_password = target_password
        self.port = port
        self.keep_alive = keep_alive
        self.jumpserver = None
        self.target = None

    def connect_to_jumpserver(self):
        """ connect to intermediate jumpserver """
        try:
            self.jumpserver = paramiko.SSHClient()
            self.jumpserver.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.jumpserver.connect(self.jumpserver_ip, username=self.jumpserver_username,
                                    password=self.jumpserver_password, port=self.port)
        except Exception as exception:
            raise Exception(
                "Couldn't ssh into jumpserver: " + str(exception))

        return self.jumpserver

    def connect_to_target(self):
        """ connect to target host via the jumpserver """
        jumpserver_transport = self.connect_to_jumpserver().get_transport()
        transport_addr = (self.jumpserver_private_ip, 22)
        target_addr = (self.target_ip, 22)

        jumpbox_channel = jumpserver_transport.open_channel(
            "direct-tcpip", target_addr, transport_addr)
        self.target = paramiko.SSHClient()
        self.target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.target.connect(self.target_ip, username=self.target_username,
                            password=self.target_password, sock=jumpbox_channel)

    def close(self):
        """ close the ssh conection """
        self.jumpserver.close()
        self.jumpserver = None
        self.target.close()
        self.target = None

    @with_ssh
    def run_command(self, command):
        """ run a remote command on target host """
        stdin, stdout, stderr = self.target.exec_command(command)
        out = stdout.read()
        err = stderr.read()
        ret = stdout.channel.recv_exit_status()

        if ret != 0:
            raise RuntimeError(
                "Command failed. " + "exit code: " + str(ret) + " stderr: " + str(err))

        return out, err, ret

    @with_ssh
    def get_file(self, remote_filepath, local_filepath):
        """ SFTP get"""
        sftp = self.target.open_sftp()
        try:
            sftp.get(remote_filepath, local_filepath)
        finally:
            sftp.close()

    @with_ssh
    def send_file(self, local_filepath, remote_filepath):
        sftp = self.ssh.open_sftp()
        try:
            sftp.put(local_filepath, remote_filepath)
        finally:
            sftp.close()
