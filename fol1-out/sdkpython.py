import docker
import time

def docker_run_tacacs(tacacs_server):
    docker_client = docker.DockerClient(base_url=f'tcp://{tacacs_server}:2375')

    try:
        docker_client.networks.get('tacacs_network')
    except docker.errors.NotFound:
        docker_client.networks.create('tacacs_network', driver='bridge')

    container_params = {
        'image': 'ubuntu18/tacacs/v0923',
        'name': 'my_tacacs_container',
        'detach': True,
        'ports': {'49': 49},
        'command': "/bin/bash -c '/etc/init.d/tacacs_plus start && tail -f /dev/null'",
        'network': 'tacacs_network'
    }

    container = docker_client.containers.run(**container_params)

    return container


if __name__ == "__main__":

    tacacs_server = "10.212.131.48"
    container = docker_run_tacacs(tacacs_server)
    if container:
        print("Container ID:", container.id)

    time.sleep(10)

    container.stop()
    container.remove()