import time
import re

import pytest


def test_filtermap(connect_paramiko_fix):
    '''Тестирование filtermap. Запуск теста: pytest pb_test.py::test_filtermap -v'''
    packets = (r'(\S\s+p1-2\s+)(\S+\s+\S)(1                     )')
    connect_paramiko_fix.send('op show port statistic | match OK|port | view table\n')
    time.sleep(30)
    output = connect_paramiko_fix.recv(9000).decode("utf-8")
    find = re.search(packets, output)
    assert find, 'Должен быть 1 переданный пакет'


def test_firmware(connect_paramiko_fix, cmdopt):
    '''Тестирование правильности версии rdp-firmware . Запуск теста: pytest pb_test.py::test_firmware -q --ver=SDNSwitch-packet-broker-3.2.5.0.4844-develop-6a20422.image -v'''
    valid_version = cmdopt.split('-')[-3] #из переданной строки с названием прошивки (--ver==) вытаскиваем элемент с номером
    regex = "current "
    connect_paramiko_fix.send('op show rdp-firmware\n')
    time.sleep(30)
    output = connect_paramiko_fix.recv(9000).decode("utf-8").splitlines()
    for element in output:
        find = re.search(regex, element)
        if find:
            index = output.index(element)
            if 'A' in element:
                index2 = index + 10
            elif 'B' in element:
                index2 = index + 23
    assert valid_version in output[index2].strip(), f'Версия rdp-firmware должна быть {valid_version}'


def test_aaa_create(connect_aaa_fix):
    '''Тестирование создания новых пользователей. Запуск теста: pytest pb_test.py::test_aaa_create -v'''
    time.sleep(30)
    output = connect_aaa_fix.recv(9000).decode("utf-8")
    assert output

@pytest.mark.parametrize(
    ('conditions', 'result'), [('show aaa users | match myuser\n', 'No data'),
                               ('show aaa user-roles | match myrole\n', 'No data'),
                               ('show aaa users | view table\n', 'userread      |****       |operator'),
                               ('call aaa delete-user user admin\n', 'msg builtin user cannot be deleted'),]
)
def test_aaa_delete_change(connect_paramiko_fix, conditions, result):
    '''Тестирование ааа. Запуск теста: pytest pb_test.py::test_aaa_delete_change -v'''
    connect_paramiko_fix.send(conditions)
    time.sleep(30)
    output = connect_paramiko_fix.recv(9000).decode("utf-8")
    assert result in output, 'Пользователь и роль должны быть удалены'


def test_aaa_change_password(test_connection_fix):
    '''Проверка изменения пароля у пользователя userread. Запуск теста: pytest pb_test.py::test_change_password -v'''
    time.sleep(30)
    output = test_connection_fix.recv(9000).decode("utf-8")
    assert output

@pytest.mark.parametrize(
    ('conditions', 'result'), [('configure\n', 'No modules available to configure'),
                               ('show ?\n', 'snmp   - Module describes snmp configuration data'),
                               ('show hardware-info\n', 'syntax error: hardware-info'),
                               ]
)
def test_tacacs(connect_tacacs_fix, conditions, result):
    '''Тестирование возможности зайти под учеткой от такакса и наделение пользователя правами. Пользователю доступны команды show snmp, меню configure недоступно
     Запуск теста: pytest pb_test.py::test_tacacs -v'''
    time.sleep(30)
    output = connect_tacacs_fix.recv(9000).decode("utf-8")
    assert output

