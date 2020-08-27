"""
Module Name: main.py
Author: Arlo Hollingshad & Gui Barati
Version Number: 0.1
Language Version: 3.6+
Description of Module:
This module creates an inventory of devices to be probed through manual imput or CSV file.
For every device in the inventory it colects the hardware model, software version, and hostname.
The information is saved on a CSV file in the local directory
Application flow is:
load_inventory() -> determines if user wants to load a file or manual information about devices.
                 -> calls appropriate function to load information manually or via CSV
                 -> Outputs a list of dictionaries. Each dictionary is a device with IP and credentials

create_report() -> Iterates through the list of dictionaries.
                -> for each item it calls the get_device_info() function to collect the devices information
                -> Information is added to new CSV file saved to local directory

get_device_info() -> Uses the appropriate device_control module to collect iformation from the device for
                     hardware model, softare version, hostname

"""


from getpass import getpass
import csv, sys, asa_control, ios_control
from exceptions import AuthFail


def load_inventory_manually():
    """
    This function prompts the user to manually enter device information
    and outputs a list of dictionaries with the device information
    """
    output = []
    n = 'y'
    while n.lower() == 'y': 
        device_type = input('Enter the device type: ')
        host_address = input('Enter the host address: ')
        username = input('Enter the username: ')
        password = getpass('Enter the device password: ')
        output.append({'dev_type': device_type,'host':host_address,'user':username,'pass':password})
        n = input('Add another device manually? (y/n): ')
    return output


def load_inventory_file(file=''):
   output = [] 
   if file == '':
       print('\n\nSupported file type is CSV. Expected headers below must be in the same order and are case sensitive:')
       print(' dev_type, host, user, pass ')
       inv_file = input('\nEnter the CSV file containing the discovery hosts: ')
   else:
       inv_file = file 
   with open(inv_file,'r') as f:
       reader = csv.DictReader(f)
       for row in reader:
           output.append(row)
   return output


def load_inventory():
    method = ''
    while method.lower() not in ['manual','file']:
        method = input('\nEnter the inventory loading method: manual or file?: ')
    if method.lower() == 'manual':
        inventory = load_inventory_manually()
    elif method.lower() == 'file':
        inventory = load_inventory_file()
    return inventory


def get_device_info(dev_type,host,user,password):
    try:
        if dev_type.lower() == 'asa':
            device = asa_control.connect(host,user,password)
            asa_control.get_info(device)
        if dev_type.lower() == 'ios':
            device = ios_control.connect(host,user,password)
            ios_control.get_info(device)

        output = {'hardware':device.hardware_model, 'software':device.software_version,'hostname':device.hostname,\
                  'serial':device.serial_num,'device_IP':host}
        
    except ConnectionError:
        output = {'hardware':'ConnectionError', 'software':'ConnectionError','hostname':'ConnectionError','device_IP':host}
    except AuthFail:
        output = {'hardware':'AuthFail', 'software':'AuthFail','hostname':'AuthFail','device_IP':host}
    return output


def create_report(inventory):
    i = 1
    with open('report.csv', 'w') as file:
        fieldnames = ['hardware','software','hostname','serial','device_IP']
        writer = csv.DictWriter(file,fieldnames)
        writer.writeheader()
        for device in inventory:
            print('Probing device ', i, ' of ',len(inventory))
            i = i + 1
            device_info = get_device_info(device['dev_type'],device['host'],device['user'],device['pass'])
            print(device_info)
            writer.writerow(device_info)


def main():
    if len(sys.argv) > 1:
        inv = load_inventory_file(sys.argv[1])
        print('using CSV file ', sys.argv[1])
    else:    
        inv = load_inventory()
    create_report(inv)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("User cancelled script execution.")

