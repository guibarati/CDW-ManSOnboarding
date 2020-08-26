"""
Module Name: asa_control.py
Author: Arlo Hollingshad & Gui Barati
Version Number: 0.1
Language Version: 3.6+
Description of Module:
This function establishes an SSH connection with the ASA object,
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
    asa = {'device_type': 'cisco_asa', 'host': host, 'username': username, 'password': password}
    try:
        device = ConnectHandler(**asa)
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
    output = {}
    shver = send_command('show ver',device)
    for i in shver:
        if 'Hardware' in i:
            output['hardware'] = (i.split()[1].split(',')[0])
        if 'Software Version' in i:
            output['software'] = (i.split()[-1])
    return output


def get_show_inventory(device):
    j = 0
    output = {}
    hardware = (send_command('show inventory',device))
    for i in hardware:
        if 'PID' in i and j == 0:
            hardware_model = i.split()[1]
            serial_num = i.split('SN:')[1]
            j = 1
            output['hardware'] = hardware_model
            output['serial'] = serial_num
    return output


def get_info(device: cisco.CiscoAsaSSH):
    shver = get_software_version(device)
    device.software_version = shver['software']
    shinv = get_show_inventory(device)
    device.serial_num = shinv['serial']
    device.hardware_model = shinv['hardware']
    device.hostname = get_hostname(device)
    

