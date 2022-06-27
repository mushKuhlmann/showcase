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
# функция send_show_command подключается к железке с помощью netmiko
# и записывает результат в виде списка строк list_output
def send_show_command(device, command):
	with ConnectHandler(**device) as ssh:
		ssh.enable()
		output = ssh.send_command(command)
		list_output = output.splitlines()
	return list_output

#функция to_file принимает список строк и преобразует их в таблицу(PrettyTable), записывает в файл
def to_file(title, command_result, device, hostname):
	regex = r'(\S+) +(\S+) +\w+ \w+ +(administratively down|up|down) +(up|down)'
	with open(title, 'a') as f:
		f.write(f'hostname: {hostname}, ip manage: {device}\n')
		f.write(f'current_datetime:{current_datetime} \n')
		mytable = PrettyTable()
		mytable.field_names = ['Interface', 'IP-Address', 'Status', 'Protocol']
		for element in command_result:
			find = re.search(regex, element)
			if find:
				mytable.add_row([find.group(1),find.group(2),find.group(3),find.group(4)])
			table = mytable.get_string()
		f.write(table)
		f.write('\n\n')
	return



if __name__ == "__main__":
	with open("devices.yaml") as f:
		devices = yaml.safe_load(f)
	print('Подключение к оборудованию...')
	for device in devices:
		try:
			result = send_show_command(device, 'show ip int br')
			to_file('ip_interfaces.txt', result, device['ip'], device['host'])
		except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
			with open('unreachable_devices.txt', 'a') as f:
				f.write(f'*Hеудачная попытка подключения в {current_datetime:{current_datetime}}, причина:\n {error} \n {"-"*30}\n ')
			print(f'Оборудование {device["ip"]} не отвечает, посмотреть возможную причину в файле unreachable_devices.txt')
	print('Завершено успешно. Результат выполнения команды в файле ip_interfaces.txt')
