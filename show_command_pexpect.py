from datetime import datetime
from prettytable import PrettyTable
import re
import pexpect
import yaml

def send_command(ip, username, password, enable, command, prompt="#"):
	with pexpect.spawn(f'ssh {username}@{ip}', timeout=10, encoding='utf-8') as ssh:
		status = ssh.expect(['[Pp]assword', pexpect.TIMEOUT, pexpect.EOF])
		if status == 1:
			with open('unreachable_devices.txt', 'a') as err:
				err.write(f'неудачная попытка подключения в {current_datetime:{current_datetime}} к device: {ip}. Причина: TIMEOUT \n')
			print(f'железка {ip} не отвечает, посмотреть причину в файле unreachable_devices.txt')
		if status == 2:
			with open('unreachable_devices.txt', 'a') as err:
				err.write(f'неудачная попытка подключения в {current_datetime:{current_datetime}} к device: {ip}. Причина: EOF \n')
			print(f'железка {ip} не отвечает, посмотреть причину в файле unreachable_devices.txt')
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

find_list = []
regex = r'(\S+) +(\S+) +\w+ \w+ +(administratively down|up|down) +(up|down)'
current_datetime = datetime.now()

with open("devices.yaml") as opfile:
	devices = yaml.safe_load(opfile)
print('подключаемся к железкам...')
for equip in devices:
	try:
		result = send_command(equip['ip'], equip['username'], equip['password'], equip['secret'], 'sh ip int br')
		with open('result.txt', 'a') as f:
			f.write(f'current_datetime:{current_datetime} \n')
			f.write(f'hostname: {result[-1]}, ip manage: {equip["ip"]}\n')
			mytable = PrettyTable()
			mytable.field_names = ['Interface', 'IP-Address', 'Status', 'Protocol']
			for element in  result:
				find = re.search(regex, element)
				if find:
					mytable.add_row([find.group(1),find.group(2),find.group(3),find.group(4)])
				table = mytable.get_string()
			f.write(table)
			f.write('\n\n')
	except:
		print('продолжаем с другой железкой')
print('результат выполнения команды в файле result.txt')


