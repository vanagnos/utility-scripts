"""
sript for getting jboss logs using jbosslog command.
"""
import config
from utilities import get_ssh_utility
from threading import Thread
from datetime import datetime


def create_log_name(business_key):
    """ log name for jboss logging """
    current_date_time = datetime.today()
    current_timestamp = current_date_time.strftime("%c")

    log_name = business_key + '_' + current_timestamp
    log_name = '_'.join(log_name.split(' ')) + '.log'

    return log_name


def get_jbosslog_pid():
    sshutility = get_ssh_utility()
    pid, _, _ = sshutility.run_command("sudo pidof tail | cut -d ' ' -f 1")
    return pid


def stop_vnflcm_logging(pid):
    """ terminate jbosslog process with specified pid """
    sshutility = get_ssh_utility()
    print('pid: ', pid)
    sshutility.run_command('sudo kill ' + pid)


def start_vnflcm_logging(business_key):
    """ start jbosslog process for a workflow """
    sshutility = get_ssh_utility()
    log_name = create_log_name(business_key)
    command = config.START_LOGGING_COMMAND.format(log_name)
    thread = Thread(target=sshutility.run_command, args=(command, ))
    thread.daemon = True
    try:
        thread.start()
    except Exception as exception:
        raise Exception(str(exception))

    return log_name


def get_vnflcm_log(log_name):
    """ get VNF-LCM log file for a workflow """
    sshutility = get_ssh_utility()
    sshutility.get_file('/tmp/{}'.format(log_name), 'logs/{}'.format(log_name))
    sshutility.run_command('rm -f /tmp/{}'.format(log_name))
    print('o')


def cleanup(pid, logname):
    stop_vnflcm_logging(pid)
    get_vnflcm_log(logname)
