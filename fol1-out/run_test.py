from datetime import datetime
import time
import subprocess
import yaml
import sys
import os
from pb_connect import connect_paramiko, connect_paramiko_configure


condition = sys.argv[1]
start_time = datetime.now()
new_conf_list = [] #список команд с указанием названия прошивки
ping = 0 #для контроля состояния устройства
i = 0 #счетчик для красоты

with open('devices.yaml') as f:
    devices = yaml.safe_load(f)

for device in devices:
    print(f'Connect to {device.get("hostname")}... please, wait\n')
    print('*' * 100)

    if 'aaa' in condition:
        with open(condition) as conf_file:
            config_list = yaml.safe_load(conf_file)
        print(f'\n1 Configure...')
        try:
            for key in config_list.keys():
                if 'create' in key:  # на устройстве создаем пользователей
                    i += 1
                    print(f'\n1.{i} Configure {key}:')
                    connect_paramiko(device, config_list[key])


        except ValueError:
            print('\nsomething shit')
        else:
            time.sleep(5)
            print(f'\n3. Run test create user, please wait... \n')
            # С помощью теста убедиться что можно залогиниться на устройстве по созданными учетными данными
            os.system('pytest pb_test.py::test_aaa_create')
        i = 0
        print(f'\n4 Configure...')
        try:
            for key in config_list.keys():
                if 'delete' in key or 'change' in key:  # на устройстве удалить или изменить пользователей/роли/пароли
                    i += 1
                    print(f'\n4.{i} Configure {key}:')
                    connect_paramiko(device, config_list[key])
        except ValueError:
            print('\nsomething shit')

        else:
            time.sleep(5)
            print(f'\n5. Run test delete/change  users and roles, please wait \n')
            # с помощью теста убедиться что изменения на предыдущем шаге применились
            os.system('pytest pb_test.py::test_aaa_delete_change')
            time.sleep(5)
            print(f'\n6. Run test change password for custom user, please wait \n')
            # с помощью теста убедиться что пароль был изменен
            os.system('pytest pb_test.py::test_aaa_change_password')

    elif 'image' in condition:
        with open('updatefirmware.yaml') as conf_file:
            config_list = yaml.safe_load(conf_file)
        print('\n1. Download and install the image\n')
        for element in config_list:
            new_conf_list.append(element.format(condition, condition))
        try:
            result = connect_paramiko(device, new_conf_list)
        except ValueError:
            print('\nsomething shit')
        else:
            print('\n2. The image was installed, please wait for reboot\n')
            time.sleep(80)
            # с помощью пинг проверяем доступность устройства, как только пинг есть запускаем pytest
            while ping != 1:
                run_ping = subprocess.run(['ping', '-c', '3', '-n', f'{device.get("hostname")}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                if run_ping.returncode == 0:
                    print('\nThe device was successfully rebooted\n')
                    print(f'\n3. Run test \n')
                    ping += 1
                    os.system(f'pytest pb_test.py::test_firmware -q --ver={condition}')

    if 'tacacs' in condition:
        with open(condition) as conf_file:
            config_list = yaml.safe_load(conf_file)
        print(f'1. Run docker tacacs server\n')
        os.system(f'docker run -d  ubuntu18/tacacs/v0923 bash -c "while true; do sleep 2; wait; done" > container.txt') #докер ubuntu18/tacacs/v0923 уже установлен
        with open('container.txt') as container_file:
            for line in container_file:
                container_id = line.strip()
        os.system(f'docker exec -it {container_id} bash -c "/etc/init.d/tacacs_plus start"')
        os.system(f'docker exec -it {container_id} bash -c "/etc/init.d/tacacs_plus start"') #иногда запускается только со второго раза
        print(f'\n2. Configure tacacs server on the dut')
        try:
            connect_paramiko_configure(device, config_list)
        except ValueError:
            print('\nsomething shit')
            os.system(f'docker rm -f {container_id}')
            os.system('rm containers.txt')
        else:
            time.sleep(5)
            print(f'\n2. Run test tacacs \n')
            # С помощью теста убедиться что можно залогиниться на устройстве по созданными учетными данными, настроенными на tacacs
            os.system('pytest pb_test.py::test_tacacs')
            os.system(f'docker rm -f {container_id}')
            os.system('rm container.txt')

print('*' * 100)
print('total execution time:', datetime.now() - start_time)

