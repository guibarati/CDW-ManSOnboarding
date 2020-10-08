"""
Module Name: asa_control.py
Author: Arlo Hollingshad & Gui Barati
Version Number: 0.1
Language Version: 3.6+
Description of Module:
This function establishes an SSH connection with the IOS(router/switch) object,
issues the "show ver" command and parses the result

"""

import re
from sys import exit as sys_exit
from netmiko import ConnectHandler, cisco, ssh_exception
from exceptions import AuthFail


def connect(host,username,password) -> cisco.CiscoAsaSSH:
    """
    This function uses netmiko to connect to a remote device over SSH.
    If SSH fails, then try telnet
    :SSH keys are not supported at this time
    :return: netmiko CiscoAsaSSH object with SSH connection to remote device
    """
    ios_ssh = {'device_type': 'cisco_ios_ssh', 'host': host, 'username': username, 'password': password}
    ios_telnet = {'device_type': 'cisco_ios_telnet', 'host': host, 'username': username, 'password': password}
    try: 
        # Try to SSH to the device
        device = ConnectHandler(**ios_ssh)
    except ssh_exception.NetMikoTimeoutException as t_err:
        # IF SSH fails, try telnet
        try:
            device = ConnectHandler(**ios_telnet)
        except:
            # If neither SSH nor Telnet work, raise an exception and move on
            #raise ConnectionError(t_err.args[0])
            raise ConnectionError('Could not connect with SSH or Telnet')
    except ssh_exception.NetMikoAuthenticationException as au_err:
        raise AuthFail(au_err.args[0])
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
    if 'Nexus' in shver[0]:
        for i in shver:
            if 'System version' in i:
                software_version = i.split(':')[1].strip()
    if 'Version' in shver[0]:
        software_version = shver[0].split('Version')[1].split(',')[0].strip()
    return software_version

def get_ip_interfaces(device):
    # this regex is to match for gigabit, ethernet, fastethernet and loopback.
    intf_pattern = "^[lLgGeEfF]\S+[0-9]/?[0-9]*"
    # create a regex object with the pattern in place
    regex = re.compile(intf_pattern)
    # create an empty list
    interfaces = []

    output = send_command('show ip interface brief', device)
    type(output)
    for row in output:
        # check for interface names only
        if regex.search(row):
        # start collecting the dictionary
            interfaces.append(
                {'interface': row.split()[0],
                 'ip_address': row.split()[1],
                 'ok': row.split()[2],
                 'method': row.split()[3],
                 'status': row.split()[4],
                 'protocol': row.split()[5]}
            )

    return interfaces


def get_show_inventory(device):
    j = 0
    output = {}
    hardware = (send_command('show inventory',device))
    for i in hardware:
        if 'PID' in i and j == 0:
            hardware_model = i.split()[1]
            serial_num = i.split('SN:')[1]
            j = 1
            output['hardware'] = hardware_model.strip()
            output['serial'] = serial_num.strip()
    return output


def get_info(device: cisco.CiscoAsaSSH):
    device.software_version = get_software_version(device)
    device.hostname = get_hostname(device)
    shinv = get_show_inventory(device)
    device.hardware_model = shinv['hardware']
    device.serial_num = shinv['serial']

    
    

