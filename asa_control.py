"""
Script/Utility Name: 
Author: 
Version Number: 0.2
Language Version: 3.6+
Description of Function:
"""


from sys import exit as sys_exit
from netmiko import ConnectHandler, cisco, ssh_exception


def connect(host,username,password) -> cisco.CiscoAsaSSH:
    """
    This function uses netmiko to connect to a remote device over SSH.
    :SSH keys are not supported at this time
    :return: netmiko CiscoAsaSSH object with SSH connection to remote device
    """
    asa = {'device_type': 'cisco_asa', 'host': host, 'username': username, 'password': password}
    device = ConnectHandler(**asa)
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


def show_ver(device: cisco.CiscoAsaSSH):
    shver = send_command('show ver',device)
    for i in shver:
        if 'Hardware' in i:
            device.hardware_model = i.split()[1].split(',')[0]
        if 'Software Version' in i:
            device.software_version = i.split()[-1]
        if 'mins' in i:
            device.hostname = i.split()[0]
    

