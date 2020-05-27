# 树莓派服务器实例定义
#
#
import time
from Lock_Server.Util import gen_logger, get_local_IP
import socket
from datetime import datetime
import threading
import  json
from Lock_Server.dbconfig import Base, engine, User,Threshold
from sqlalchemy.orm import sessionmaker
import requests


import numpy as npy
from Lock_Server.MFCC import MFCC
from Lock_Server.play import Play
from multiprocessing import Queue,Manager
from sklearn import neighbors,svm
import joblib

logger = gen_logger('LockSSDP')


class Server(threading.Thread):
    BCAST_IP = '239.255.255.250'
    UPNP_PORT = 1901
    IP = '0.0.0.0'
    M_SEARCH_REQ_MATCH = "LOCK-SEARCH"
    message = ''

    def __init__(self, port, protocal, networkid,event):
        '''
        port: a blockchain network port to broadcast to others
        '''
        threading.Thread.__init__(self)
        self.interrupted = False
        self.port = port
        self.protocol = protocal
        self.networkid = networkid
        self.event = event
        self.flag = True
        return

    def run(self):

        self.listen()

    def stop(self):
        self.interrupted = True
        logger.info("upnp server stop")

    def listen(self):
        '''
        UDP监听广播地址上的1900端口,如果收到标准的LockSSDP协议消息(查找消息)，则认为搜索到APP服务（通过检查关键字段：M_SEARCH）
        '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                            1)  # linux 使用：socket.SO_REUSEPORT 而不是 socket.SO_REUSEADDR
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(self.BCAST_IP) + socket.inet_aton(self.IP))
            sock.bind((self.IP, self.UPNP_PORT))
            sock.settimeout(1)
            logger.info("upnp server is listening...")
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                except socket.error:
                    if self.interrupted:
                        sock.close()
                        return
                else:
                    if self.M_SEARCH_REQ_MATCH in data.decode('ASCII'):
                        logger.debug("received M-SEARCH from %s \n %s", addr, data)
                        self.event.clear()
                        self.respond(addr)
                        self.newTCPsock()
                        self.event.set()
        except Exception as e:
            logger.error('Error in npnp server listening: %s', e)

    def respond(self, addr):
        try:
            local_ip = get_local_IP()
            UPNP_RESPOND = """
            -------Touch Voice SSDP Standard Response-------
            Status: 200 OK
            Version: Touch Voice SSDP 1.0
            Exception: None
            Location: {}_{}://{}::{}|
            Time:{}
            ------------------------------------------------
            """.format(self.protocol, self.networkid, local_ip, self.port, datetime.now())  # .replace("\n", "\r\n")
            outSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            outSock.sendto(UPNP_RESPOND.encode('ASCII'), addr)
            logger.debug('response data: %s', UPNP_RESPOND)
            outSock.close()
        except Exception as e:
            logger.error('Error in upnp response message to client %s', e)

    # 树莓派建立新的TCP监听，用来与APP进行交互
    def newTCPsock(self):

        Server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        Server_sock.bind((get_local_IP(), self.port))
        Server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        Server_sock.listen(5)
        try:
            print("Waiting for connection...")
            Client_sockect, Client_addr = Server_sock.accept()
            print("Client address is ", Client_addr)
            while True:
                self.message = Client_sockect.recv(1024).decode()
                print(self.message)
                self.message = json.loads(self.message)
                # 获取token并验证
                if self.message['PAGEID'] == 'bind':
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    user1 = User(username=self.message['USERNAME'], lockid=self.message['LOCKID'],
                                 token=self.message['TOKEN'])
                    session.add(user1)
                    session.commit()
                    session.close()
                elif self.message['PAGEID'] == 'vibration':
                    t = time.time()
                    strt = time.strftime("%b_%d_%Y_%H_%M_%S", time.gmtime(t))
                    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
                    manager = Manager()
                    queue = manager.Queue()
                    vectors = npy.ones((1, 2000))
                    queue.put(vectors)
                    for x in range(0, 40):  # 30 -> pos,10 -> baseline
                        mfcc = MFCC('Lock_Server/vibration.wav', queue)
                        play = Play()
                        play.start()
                        time.sleep(0.16)
                        mfcc.start()

                        play.join()
                        mfcc.join()
                        time.sleep(1)
                        if x == 29:
                            print("请抬起手")
                    vectors = queue.get()
                    print(vectors)
                    print(vectors.shape)
                    newvectors = npy.ones((40, 2000))
                    n_neighbors = 3
                    target1 = npy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                         1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                         2, 2, 2, 2, 2, 2, 2, 2, 2, 2]).T
                    target2 = npy.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3]).T
                    for x in range(1, 41):
                        for y in range(0, 2000):
                            newvectors[x - 1, y] = (vectors[x, y] - npy.min(vectors[1:41, y])) / (
                                        npy.max(vectors[1:41, y]) - npy.min(vectors[1:41, y]))
                    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    weight = []
                    for i in range(0, 2000):
                        weight.append(
                            (npy.max(npy.std(vectors, axis=0)) - npy.std(vectors[:, i])) / (
                                npy.sum(npy.max(npy.std(vectors, axis=0)) - npy.std(vectors, axis=0)))
                        )
                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    pos = neighbors.KNeighborsClassifier(n_neighbors,
                                                         weights="uniform",
                                                         metric="wminkowski",
                                                         metric_params={
                                                             'w': npy.array(weight)
                                                         }, p=1)
                    print(newvectors[:30, :].shape, target1.shape)
                    posmodel = pos.fit(newvectors[:30, :], target1)
                    joblib.dump(posmodel, '{}_pos.model'.format(strt),compress=3)
                    dist_pos, ind_pos = pos.kneighbors(newvectors[:30, :], n_neighbors=3)
                    E_distance_pos = npy.mean(npy.mean(dist_pos, axis=1))

                    baseline = neighbors.KNeighborsClassifier(n_neighbors,
                                                              weights="uniform",
                                                              metric="wminkowski",
                                                              metric_params={
                                                                  'w': npy.array(weight)
                                                              }, p=1)
                    blmodel = baseline.fit(newvectors[30:, :], target2)
                    joblib.dump(blmodel, '{}_bl.model'.format(strt),compress=3)
                    dist_bl, ind_bl = baseline.kneighbors(newvectors[:30, :], n_neighbors=3)
                    E_distance_bl = npy.mean(npy.mean(dist_bl, axis=1))
                    a = 0.19
                    threshold = (1 - a) * E_distance_pos + a * E_distance_bl
                    print("Threshold is ：{}".format(threshold))
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    th = Threshold(threshold=threshold)
                    session.add(th)
                    session.commit()
                    session.close()
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
                elif self.message['PAGEID'] == 'createclock':
                    self.flag = False
                elif self.message['PAGEID'] == 'deleteclock':
                    self.flag = True
                    GPIO.event_detected(11)
                elif self.message['PAGEID'] == "attack":
                    self.flag = False
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    data = {
                        "name": 'Stranger',
                        "event": 'attack',
                        "occur_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "app_username": session.query(User).filter(
                            User.username == self.message['USERNAME']).one().username,
                        "lock_id": session.query(User).filter(User.username == self.message['USERNAME']).one().lockid,
                        "isSafe": 'True'
                    }

                    response = requests.post("http://192.168.101.10:5000/app/WarningInfo", data)
                    print(response)
                    print(response.content.decode())
                    print(response.headers)

                if self.message['IsOver'] == "True":  # 会话结束标识 ‘LockSSDP End’
                    time.sleep(0.5)
                    break
            Client_sockect.close()
        except Exception as e:
            print("Server error!",e)
        Server_sock.close()



# vibration 发出振动注册用户
# createclock 创建门链
# deleteclock 删除门链
# bind 绑定