from datetime import datetime
from prettytable import PrettyTable
import re
import yaml
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
current_datetime = datetime.now()



def send_config(device, commands):
	with ConnectHandler(**device) as ssh:
		ssh.enable()
		result_expect = ssh.send_config_set(commands)
	return result_expect


if __name__ == "__main__":
	with open("devices.yaml") as f:
		devices = yaml.safe_load(f)
	print('Подключение к оборудованию...')
	commands = ['access-list 1 permit 6.6.6.0 0.0.0.255', 'access-list 2 permit 7.7.7.0 0.0.0.255']
	for device in devices:
		try:
			result = send_config(device, commands)
			print(result)
		except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
			with open('unreachable_devices.txt', 'a') as f:
				f.write(f'*Hеудачная попытка подключения в {current_datetime:{current_datetime}}, причина:\n {error} \n {"-"*30}\n ')
			print(f'Оборудование {device["ip"]} не отвечает, посмотреть причину в файле unreachable_devices.txt')
	print('Выполнено успешно')
