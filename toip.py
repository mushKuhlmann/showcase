import base64
import socket
import struct


def base2ip(input_ip):
    "only ipv4"
    try:
        input_ip = input_ip.split(' ')
        ip, mask = input_ip[0], input_ip[1]
        hex_ip = base64.b64decode(ip).hex()
        dec_ip = int(hex_ip, 16)

        ip_list = socket.inet_ntoa(struct.pack("<L", dec_ip)).split('.')
        ip_ok = '.'.join(i for i in ip_list[::-1])
    except:
        return 'can not convertation', input_ip
    return f"{ip_ok}/{mask}"





if __name__ == "__main__":
    a = 'wdqIAA==/22'

    print(base2ip("KhFiQAAAAAAAAAAAAAAAAA=="))
    print(base2ip(a))