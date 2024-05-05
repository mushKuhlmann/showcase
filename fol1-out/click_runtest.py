from datetime import datetime
import time
import subprocess
import yaml
import sys
import os
import click
from pb_connect import connect_paramiko, connect_paramiko_configure
from sdkpython import docker_run_tacacs


@click.command()
# @click.option("-i", "--image",  required=True)
#для каждой опции отдельная строка. здесь: аргумент можно вводить после -i или --image
# list options = [aaa, update, tacacs, filtermap]
@click.option("-f", "--feature",  required=True, type=click.Choice(["aaa", "update", "tacacs", "filtermap"]), help="Specify a feature for test")
@click.option("-i", "--image", required=False, help="Specify a image for upload")


def cli(feature, image):
    start_time = datetime.now()

    i = 0  # счетчик
    new_conf_list = []  # список команд с указанием названия прошивки
    ping = 0  # для контроля состояния устройства
    with open('devices.yaml') as f:
        devices = yaml.safe_load(f)
    with open(f'{feature}.yaml') as conf_file:
        config_list = yaml.safe_load(conf_file)
    for device in devices:

        if feature == 'update':
            print('\n-----Test image: download new firmware and check for correct install-----')
            if os.path.exists(image):
                for element in config_list:
                    new_conf_list.append(element.format(image, image))
                try:
                    # pass
                    print('\n1. Run http.server... Done')
                    time.sleep(3)
                    # запускаем http сервер в фоновом режиме
                    subprocess.Popen('python3 -m http.server 8000 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                    # os.system('python3 -m http.server 8000 &')
                    print(f'Connect to {device.get("hostname")}... please, wait\n')
                    print('*' * 100)
                    print(f'\n2. Install the new firmware...')
                    connect_paramiko(device, new_conf_list)
                    time.sleep(3)

                except ValueError:
                    print('\nsomething shit')
                else:
                    # после завершения загрузки убиваем процесс по pid
                    show_proc = subprocess.Popen('sudo netstat -anp tcp | grep  8000', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                    while show_proc.communicate()[0] != '':
                        procnumber = show_proc.communicate()[0].split()[-1].split('/')[0]
                        subprocess.Popen(f'kill -9 {procnumber}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                        show_proc = subprocess.Popen('sudo netstat -anp tcp | grep 8000', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                    else:
                        print('Kill http.server... Done')

                    time.sleep(3)
                    print('\n2. The image was installed, please wait for reboot\n')
                    time.sleep(80)
                    # с помощью пинг проверяем доступность устройства, как только пинг есть запускаем pytest
                    while ping != 1:
                        run_ping = subprocess.run(['ping', '-c', '3', '-n', f'{device.get("hostname")}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                        if run_ping.returncode == 0:
                            print('\nThe device was successfully rebooted\n')
                            print(f'\n3. Run test \n')
                            ping += 1
                            os.system(f'pytest pb_test.py::test_firmware -q --ver={image}')
            else:
                print(f'File {image} is not exist, test can\'t be run')



        # Тестирование ААА
        elif feature == 'aaa':
            try:
                print('\n-----Test AAA: create, delete, modify for user, role, password-----\n')
                print(f'Connect to {device.get("hostname")}... please, wait\n')
                print('*' * 100)
                for key in config_list.keys():
                    if 'create' in key:  # на устройстве создаем пользователей
                        i += 1
                        print(f'\n1.{i} Configure {key}:')
                        connect_paramiko(device, config_list[key])
            except ValueError:
                print('\nsomething shit')
            else:
                time.sleep(5)
                print(f'\n2. Run test create user, please wait... \n')
                # С помощью теста убедиться что можно залогиниться на устройстве по созданными учетными данными
                os.system('pytest pb_test.py::test_aaa_create')
            i = 0
            try:
                for key in config_list.keys():
                    if 'delete' in key or 'change' in key:  # на устройстве удалить или изменить пользователей/роли/пароли
                        i += 1
                        print(f'\n3.{i} Configure {key}:')
                        connect_paramiko(device, config_list[key])
            except ValueError:
                print('\nsomething shit')

            else:
                time.sleep(5)
                print(f'\n4. Run test delete/change  users and roles, please wait \n')
                # с помощью теста убедиться что изменения на предыдущем шаге применились
                os.system('pytest pb_test.py::test_aaa_delete_change')
                time.sleep(5)
                print(f'\n5. Run test change password for custom user, please wait \n')
                # с помощью теста убедиться что пароль был изменен
                os.system('pytest pb_test.py::test_aaa_change_password')

        elif feature == 'tacacs':
            print('\n-----Test TACACS+-server: create TACACS+ connection and access to dut via TACACS+ authentication-----\n')
            print(f'1. Run docker TACACS+ server\n')
            container = docker_run_tacacs("10.212.131.48")
            if container:
                print("Container ID:", container.id)
            print(f'\n2. Configure TACACS+ server on the dut')
            try:
                print(f'Connect to {device.get("hostname")}... please, wait\n')
                print('*' * 100)
                connect_paramiko_configure(device, config_list)
            except ValueError:
                print('\nsomething shit')
                container.stop()
                container.remove()

            else:
                time.sleep(5)
                print(f'\n2. Run test: access to the dut via TACACS+ authentication (username, password and services)  \n')
                # С помощью теста убедиться что можно залогиниться на устройстве по созданными учетными данными, настроенными на tacacs
                os.system('pytest pb_test.py::test_tacacs')
                container.stop()
                container.remove()

        if feature == 'filtermap':
            print('\n-----Test filter-map: create filter conditions and check packets in output-----\n')
            print(f'\n1. Configure flow')
            try:
                print(f'Connect to {device.get("hostname")}... please, wait\n')
                print('*' * 100)
                connect_paramiko_configure(device, config_list['all_conf'])
            except ValueError:
                print('\nsomething shit')
            for match_condition in config_list.keys():
                if match_condition != 'all_conf':
                    print('*' * 100)
                    try:
                        print(f'\n2. Configure filter-map, match is: {match_condition}\n')
                        connect_paramiko_configure(device, config_list[match_condition])
                    except ValueError:
                        print('\nsomething shit')
                    else:
                        print(f'Configure with {match_condition} is done\n')
                        print(f'\n3. Send packets\n')
                        os.system(f'sudo python3 send_pcap.py {match_condition}')
                        print(f'\n4. Run test {match_condition}\n')
                        os.system(f'pytest pb_test.py::test_filtermap')
                elif match_condition == 'all_conf':
                    pass

    print('*' * 100)
    print('total execution time:', datetime.now() - start_time)

if __name__ == "__main__":
    cli()