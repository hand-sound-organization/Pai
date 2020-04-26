from Lock_Server.lock_server import Server

if __name__ == '__main__':
    # UDP服务器端口1900，新TCP连接端口8048， 'LockSSDP', 'TouchVoiceNet'分别是协议名称和网络名称，用来返回给手机
    upnpServer = Server(8048, 'LockSSDP', 'TouchVoiceNet')
    # 子进程开启
    upnpServer.start()
