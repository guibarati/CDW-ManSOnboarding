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

def get_hostname(device):
    prompt = device.find_prompt()
    hostname = prompt.split('#')[0]
    return hostname

def show_ver(device: cisco.CiscoAsaSSH):
    """
    Calls the 'send_command' function and parses the result to extract
    hardware model, software version, and hostname
    The function must receive an object of the type CiscoAsaSSH as parameter
    and will add the hardware model, software version, and hostname as parameters
    to the objected passed to the function.
    """
    shver = send_command('show ver',device)
    for i in shver:
        if 'Hardware' in i:
            device.hardware_model = i.split()[1].split(',')[0]
        if 'Software Version' in i:
            device.software_version = i.split()[-1]
    device.hostname = get_hostname(device)
    

