"""
Module Name: asa_control.py
Author: Arlo Hollingshad & Gui Barati
Version Number: 0.1
Language Version: 3.6+
Description of Module:
This function establishes an SSH connection with the IOS(router/switch) object,
issues the "show ver" command and parses the result

"""


from sys import exit as sys_exit
from netmiko import ConnectHandler, cisco, ssh_exception

class AuthFail(Exception):
    pass

def connect(host,username,password) -> cisco.CiscoAsaSSH:
    """
    This function uses netmiko to connect to a remote device over SSH.
    :SSH keys are not supported at this time
    :return: netmiko CiscoAsaSSH object with SSH connection to remote device
    """
    ios = {'device_type': 'cisco_ios', 'host': host, 'username': username, 'password': password}
    try:
        device = ConnectHandler(**ios)
    except ssh_exception.NetmikoTimeoutException:
        raise ConnectionError('Unable to connect')
    except ssh_exception.NetmikoAuthenticationException:
        raise AuthFail('Invalid Credentials')
    
    return device


def send_command(command: str, device: cisco.CiscoAsaSSH) -> list:
    """
    Passes a show command to a remote device, and splits the result by the newline character
    :param command: String with show command to be passed to remote device
    :param device: Netmiko SSH connection to remote device
    :return: Output from show command as a list
    """
    if not isinstance(command, str):
        print("Invalid value for parameter command.")
        sys_exit()
    output = device.send_command(command)
    return output.split('\n')


def get_hostname(device):
    prompt = device.find_prompt()
    hostname = prompt.split('#')[0].split('>')[0]
    return hostname


def get_software_version(device):
    shver = send_command('show ver',device)
    if 'NX-OS' not in shver[0]:
        software_version = shver[0].split('Version')[1].split(',')[0]
    else:
        for i in shver:
            if 'System version' in i:
                software_version = i.split(':')[1]
    return software_version


def get_hardware_model(device):
    j = 0
    hardware = (send_command('show inventory',device))
    for i in hardware:
        if 'PID' in i and j == 0:
            hardware_model = i.split()[1]
            j = 1
    return hardware_model


def get_info(device: cisco.CiscoAsaSSH):
    device.software_version = get_software_version(device)
    device.hostname = get_hostname(device)
    device.hardware_model = get_hardware_model(device)

        

    
    

