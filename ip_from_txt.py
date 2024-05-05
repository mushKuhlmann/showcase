import re
from toip import base2ip




# with open('tricolor.txt') as f:
#     find = re.findall(regex2, f.read())
#     for element in find:
#         list1.append(f'{element[0]} {element[1]}')



def txt2ip(file):
    "only ipv4, only file.txt"
    list1 = []

    regex2 = (r'"ip": "(\S+)",\n'
              r'\s+"lpm": (\d+)')
    with open(file) as f:
        find = re.findall(regex2, f.read())
        for element in find:
            list1.append(f'{element[0]} {element[1]}')

    return list1




if __name__ == "__main__":
    for ip in txt2ip('tricolor.txt'):
        print(base2ip(ip), ip)
