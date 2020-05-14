from Lock_Server.lock_server import Server
import threading
# from Lock_Server.Verify import Vibration
# import RPi.GPIO as GPIO
# import serial
if __name__ == '__main__':
    # UDP服务器端口1900，新TCP连接端口8048， 'LockSSDP', 'TouchVoiceNet'分别是协议名称和网络名称，用来返回给手机
    event = threading.Event()
    event.set()
    upnpServer = Server(8048, 'LockSSDP', 'TouchVoiceNet',event)
    # vibration = Vibration()
    # # 子进程开启
    upnpServer.start()
    # vibration.start()