from datetime import datetime
from prettytable import PrettyTable
import re
import pexpect
import yaml

current_datetime = datetime.now()

def send_command(ip, username, password, enable, command, prompt="#"):
	with pexpect.spawn(f'ssh {username}@{ip}', timeout=10, encoding='utf-8') as ssh:
		status = ssh.expect(['[Pp]assword', pexpect.TIMEOUT, pexpect.EOF])
		if status == 1:
			with open('unreachable_devices.txt', 'a') as err:
				err.write(f'неудачная попытка подключения в {current_datetime:{current_datetime}} к device: {ip}. Причина: TIMEOUT \n')
			print(f'Оборудование {ip} не отвечает, посмотреть возможную причину в файле unreachable_devices.txt')
		if status == 2:
			with open('unreachable_devices.txt', 'a') as err:
				err.write(f'неудачная попытка подключения в {current_datetime:{current_datetime}} к device: {ip}. Причина: EOF \n')
			print(f'Оборудование {ip} не отвечает, посмотреть возможную причину в файле unreachable_devices.txt')
		else:
			ssh.sendline(password)
			ssh.expect(prompt)
			ssh.sendline(command)
			status = ssh.expect(prompt)
			ssh.before
			output = ssh.before
			ssh.close()
			list_output = output.splitlines()

	return list_output


def to_file(title, command_result, device_ip, hostname):
	regex = r'\S+ +(\S+) +(\d+|-) +(\S+) +\w+ +(\S+)'
	with open(title, 'a') as f:
		f.write(f'hostname: {hostname}, ip manage: {device_ip}\n')
		f.write(f'current_datetime:{current_datetime} \n')
		mytable = PrettyTable()
		mytable.field_names = ['IP-Address', 'MAC-Address', 'Interface']
		for element in command_result:
			find = re.search(regex, element)
			if find:
				mytable.add_row([find.group(1),find.group(3),find.group(4)])
			table = mytable.get_string()
		f.write(table)
		f.write('\n\n')
	return



if __name__ == "__main__":
	with open("devices.yaml") as opfile:
		devices = yaml.safe_load(opfile)
	print('Подключение к оборудованию...')
	for equip in devices:
		try:
			result = send_command(equip['ip'], equip['username'], equip['password'], equip['secret'], 'show arp')
			to_file('show_arp.txt', result, equip['ip'], equip['host'])
		except:
			print('продолжаем с другой железкой')
	print('Завершено успешно. Результат выполнения команды в файле show_arp.txt')

