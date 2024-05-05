import time
import yaml
import pytest
import paramiko
def pytest_addoption(parser):
    parser.addoption("--ver", action="store",  help="version must be")
@pytest.fixture
def cmdopt(request):
    return request.config.getoption("--ver")


def read_device(file):
    with open(file) as f:
        devices = yaml.safe_load(f)
    return devices

def get_host(devices):
    return devices.get("hostname")

def get_user(devices):
    return devices.get("username")



@pytest.fixture(params=read_device("devices.yaml"), ids=get_host)
def connect_paramiko_fix(request):
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(**request.param)
    with cl.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(10)
        yield ssh
        ssh.settimeout(5)
        ssh.close()



@pytest.fixture(params=read_device("aaatest.yaml"), ids=get_user)
def connect_aaa_fix(request):
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(**request.param)
    with cl.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(10)
        yield ssh
        ssh.settimeout(5)
        ssh.close()


@pytest.fixture(params=read_device("aaatest.yaml"), ids=get_user)
def connect_aaa_new_pass_fix(request):
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(**request.param)
    with cl.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(10)
        yield ssh
        ssh.settimeout(5)
        ssh.close()


@pytest.fixture(scope="session")
def test_connection_fix():
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(
        hostname="10.212.131.185",
        username="userread",
        password="1234userread",
    )
    with cl.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(10)
        yield ssh
        ssh.settimeout(5)
        ssh.close()


@pytest.fixture(params=read_device("tacacstest.yaml"), ids=get_user)
def connect_tacacs_fix(request):
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(**request.param)
    with cl.invoke_shell() as ssh:
        ssh.settimeout(5)
        time.sleep(10)
        yield ssh
        ssh.settimeout(5)
        ssh.close()