from Lock_Server.lock_server import Server

if __name__ == '__main__':
    upnpServer = Server(8048, 'LockSSDP', 'TouchVoiceNet')
    upnpServer.start()