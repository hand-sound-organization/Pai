# 测试代码 没用
#
#
#
#
from socket import *
from random import random
HOST = "255.255.255.255"
PORT = 9191
BUFFER = 1024

Client_sockect = socket(family=AF_INET,type=SOCK_STREAM)
Client_sockect.connect((HOST,PORT))

token = "Token is "+str(random())
print(token)
Client_sockect.send(token.encode())
Client_sockect.close()
