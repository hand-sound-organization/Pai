import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('主机IP','端口'))
data, addr = sock.recvfrom(1024)
print(data.decode())