import asa_control
import ios_control
import pan_control


def load_inventory():
    input('manual or file?')
    manual -> enter type, h,u,p
    file -> select file, call read_inventory(file)
    
    return a list_of_dict

def get_info(dev_type,h,u,p):
    if dev_type = 'asa':
        fw = asa_control.connect(h,u,p)
        asa_control.show_ver(fw)
    if dev_type = 'pan':
        fw == pan_control.connect(h,u,p)


def read_inventory(file):
    for i in file:
        get_info(i['dev_type'],i['host'],i['user'],i['pass'])
