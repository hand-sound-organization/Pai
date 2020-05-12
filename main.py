from Lock_Server.lock_server import Server
# import RPi.GPIO as GPIO
# import serial
if __name__ == '__main__':
    # UDP服务器端口1900，新TCP连接端口8048， 'LockSSDP', 'TouchVoiceNet'分别是协议名称和网络名称，用来返回给手机
    upnpServer = Server(8048, 'LockSSDP', 'TouchVoiceNet')
    # 子进程开启
    upnpServer.start()
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setup(11, GPIO.IN)
    # GPIO.add_event_detect(11, GPIO.RISING)
    # while True:
    #     if GPIO.event_detected(11):
    #         ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    #         ser.write('2'.encode())
