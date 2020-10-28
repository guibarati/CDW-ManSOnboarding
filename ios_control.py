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
from netmiko.ssh_exception import NetMikoAuthenticationException
from paramiko.ssh_exception import AuthenticationException
from exceptions import AuthFail


def connect(dev_type,host,username,password) -> cisco.CiscoAsaSSH:
    """
    This function uses netmiko to connect to a remote device over SSH.
    If SSH fails, then try telnet
    :SSH keys are not supported at this time
    :return: netmiko CiscoAsaSSH object with SSH connection to remote device
    """
    ssh = {'device_type': dev_type + '_ssh', 'host': host, 'username': username, 'password': password}
    telnet = {'device_type': dev_type + '_telnet', 'host': host, 'username': username, 'password': password}
    try: 
        # Try to SSH to the device
        device = ConnectHandler(**ssh)
    except ssh_exception.NetMikoTimeoutException as t_err:
        # IF SSH fails, try telnet
        try:
            device = ConnectHandler(**telnet)
        except:
            # If neither SSH nor Telnet work, raise an exception and move on
            #raise ConnectionError(t_err.args[0])
            raise ConnectionError('Could not connect with SSH or Telnet')
    except (AuthenticationException, NetMikoAuthenticationException) as au_err:
        raise AuthFail(au_err.args[0])
    except Exception as e:
        print(e)
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
#        if 'Hardware' in i:
#            output['hardware'] = (i.split()[1].split(',')[0])
        # Check for ASA
        if 'Software Version' in i:
            output = (i.split()[-1])
        # Check for NX-OS
        if 'Nexus' in shver[0]:
            for i in shver:
                if 'System version' in i:
                    output = i.split(':')[1].strip()
        # For IOS/IOS-XE
        if 'Version' in shver[0]:
            output = shver[0].split('Version')[1].split(',')[0].strip()
    return output

def get_ip_interfaces(device, dev_type):
    # this regex is to match for gigabit, ethernet, fastethernet, management, port-channel, BVI, and loopback.
    intf_pattern = "^[lLgGeEfFpPmMbB]\S+[0-9]/?[0-9]*"
    # create a regex object with the pattern in place
    regex = re.compile(intf_pattern)
    # create an empty list
    interfaces = []

    # Why do we need to check for device type? Because Cisco that's why....
    if dev_type == 'cisco_asa':
        output = send_command('show int ip bri', device)
    else:
        output = send_command('show ip interface brief', device)

    if dev_type == 'cisco_nxos':
        for row in output:
            # check for interface names only
            if regex.search(row):
            # start collecting the dictionary
                interfaces.append(
                    {'interface': row.split()[0],
                     'ip_address': row.split()[1],
                     'status': row.split()[2]}
                )
    else:
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

