import yaml
import paramiko
from scapy.all import *
import sys

#здесь выполняются предварительные работы для выполнения тестирования:


def connect_paramiko(device, conf_commands):
    '''подключение к устройству, настройка'''
    dut = paramiko.SSHClient()
    dut.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    dut.connect(**device)
    with dut.invoke_shell() as ssh:
        ssh.settimeout(10)
        time.sleep(15)
        for command in conf_commands:
            print(command)
            ssh.send(f"{command}\n")
            ssh.settimeout(10)
            time.sleep(15)
            part = ssh.recv(10000).decode("utf-8")
            if 'return-code 0' in part:
                print('RESULT OK')
            elif 'result OK' in part:
                print('RESULT OK')
            else:
                print(part)
                raise ValueError('При выполнении команды возникла ошибка')

        return part


def connect_paramiko_configure(device, conf_commands):
    '''подключение к устройству, настройка'''
    dut = paramiko.SSHClient()
    dut.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    dut.connect(**device)
    with dut.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(5)
        ssh.send('configure\n')
        ssh.settimeout(5)
        for command in conf_commands:
            ssh.send(f"{command}\n")
            ssh.settimeout(5)
            time.sleep(5)
        ssh.send('apply\n')
        ssh.settimeout(10)
        time.sleep(10)
        part = ssh.recv(10000).decode("utf-8")
        print(part)
    return part

if __name__ == "__main__":
    condition = sys.argv[1]
    with open('devices.yaml') as f:
        devices = yaml.safe_load(f)
    with open(condition) as conf_file:
        config_list = yaml.safe_load(conf_file)
        print(config_list.keys())

    for device in devices:
        list1 = config_list.keys()
        for key in config_list.keys():
            if 'create' not in key:
            # это запуск функции через (парамико)
                connect_paramiko(device, config_list[key])


