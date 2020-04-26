#  测试代码 没用
#
#
#
#
from socket import *

HOST = '169.254.215.65'
PORT = 9191
BUFFER = 1024
Server_sockect = socket(family=AF_INET, type=SOCK_STREAM)
Server_sockect.bind((HOST, PORT))
Server_sockect.listen(5)
while True:
    try:
        print("Waiting for connection...")
        Client_sockect, Client_addr = Server_sockect.accept()
        print("Client address is ", Client_addr)
        while True:
            data = Client_sockect.recv(BUFFER).decode()
            if not data:
                break
            else:
                print("Get data :%s" % data)
        Client_sockect.close()
    except:
        print("Server error!")



