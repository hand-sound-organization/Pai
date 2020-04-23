from socket import *
from random import random
HOST = "127.0.0.1"
PORT = 9191
BUFFER = 1024

Client_sockect = socket(family=AF_INET,type=SOCK_STREAM)
Client_sockect.connect((HOST,PORT))

data = "Token is "+str(random())
print(data)
Client_sockect.send(data.encode())
Client_sockect.close()
