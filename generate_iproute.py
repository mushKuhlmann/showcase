prefix = 1001
octet_2 = 0
octet_3 = 0
octet_4 = 1
with open('result-ip_route.txt', 'w') as f:
        f.write("routing static\nvrf default\naf-ipv4 unicast\n")
        for ip in range(1, prefix):
                ip = f"11.{str(octet_2)}.{str(octet_3)}.{str(octet_4)}/32"
                octet_4 += 1
                if octet_4 == 255:
                        octet_3 += 1
                        octet_4 = 1
                        if octet_3 == 254:
                                octet_2 += 1
                                octet_3 = 1
                                octet_4 = 1
                f.write(f"route {ip} gateway 172.16.0.1\n")
        f.write(f"commit\nexit")
