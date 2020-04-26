import socket
from random import random
if __name__ == '__main__':
    ENDFLAG = "Lock Session End"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto("LOCK-SEARCH".encode(), ('<broadcast>', 1900))
    while 1:
        buf, address = s.recvfrom(2048)
        data = buf.decode()
        print("Received from %s: %s" % (address, data))
        if "Touch Voice SSDP Standard Response" in data:
            ip = data[data.find('//') + len('//'):data.find('::')]
            port = int(data[data.find('::') + len('::'):data.find('|')])
            print(ip, port)
            Client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Client_sock.connect((ip, port))
            token = "Token is " + str(random())
            print(token)
            Client_sock.send(token.encode())
            Client_sock.send((" "+ENDFLAG).encode()) # 结束会话
            Client_sock.close()
