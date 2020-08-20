from getpass import getpass
import csv, asa_control

def load_inventory_manually():
    device_type = input('Enter the device type: ')
    host_address = input('Enter the host address: ')
    username = input('Enter the username: ')
    password = getpass('Enter the device password: ')
    output = [{'dev_type': device_type,'host':host_address,'user':username,'pass':password}]
    return output


def load_inventory_file():
   inv_file = input('\n\nEnter the CSV file containing the discovery hosts')
   output = []
   with open(inv_file,'r') as f:
       reader = csv.DictReader(f)
       for row in reader:
           output.append(row)
   return output
               

def load_inventory():
    method = ''
    while method.lower() not in ['manual','file']:
        method = input('Enter the inventory loading method: manual or file?: ')
    if method.lower() == 'manual':
        inventory = load_inventory_manually()
    elif method.lower() == 'file':
        inventory = load_inventory_file()
    return inventory


def get_device_info(dev_type,host,user,password):
    if dev_type.lower() == 'asa':
        fw = asa_control.connect(host,user,password)
        asa_control.show_ver(fw)   
    output = {'hardware':fw.hardware_model, 'software':fw.software_version, 'hostname':fw.hostname}
    return output
    

def create_report(inventory):
    i = 1
    with open('report.csv', 'w') as file:
        fieldnames = ['hardware','software','hostname']
        writer = csv.DictWriter(file,fieldnames)
        writer.writeheader()
        for device in inventory:
            print('Probing device ', i, ' of ',len(inventory))
            i = i + 1
            device_info = get_device_info(device['dev_type'],device['host'],device['user'],device['pass'])
            print(device_info)
            writer.writerow(device_info)
            
        
