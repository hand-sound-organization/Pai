# 树莓派服务器实例定义
#
#
from Pai.Lock_SSDP.Info_Component import gen_logger, get_local_IP
import socket
import re
import sys
import time
import threading
import miniupnpc

logger = gen_logger('LockSSDP')


class Server(threading.Thread):
    BCAST_IP = '239.255.255.250'
    UPNP_PORT = 1901
    IP = get_local_IP()
    M_SEARCH_REQ_MATCH = "LOCK-SEARCH"
    TOKEN = ''

    def __init__(self, port, protocal, networkid):
        '''
        port: a blockchain network port to broadcast to others
        '''
        threading.Thread.__init__(self)
        self.interrupted = False
        self.port = port
        self.protocol = protocal
        self.networkid = networkid
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
            # sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
            #                 socket.inet_aton(self.BCAST_IP) + socket.inet_aton(self.IP))
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
                        self.respond(addr)
                        self.newTCPsock()
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
            ------------------------------------------------
            """.format(self.protocol, self.networkid, local_ip, self.port)  # .replace("\n", "\r\n")
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
        Server_sock.listen(5)
        try:
            print("Waiting for connection...")
            Client_sockect, Client_addr = Server_sock.accept()
            print("Client address is ", Client_addr)
            while True:
                self.TOKEN = Client_sockect.recv(1024).decode()
                # 获取token并验证
                #
                #
                #
                #
                #
                #
                print(self.TOKEN)
                if "Lock Session End" in self.TOKEN:  # 会话结束标识 ‘LockSSDP End’
                    break
            Client_sockect.close()
        except:
            print("Server error!")




class Nat():
    def __init__(self):
        self.upnp = miniupnpc.UPnP()
        self.upnp.discoverdelay = 10

    def addPortForward(self, internal_port, external_port):
        try:
            discover = self.upnp.discover()
            igd = self.upnp.selectigd()
            # addportmapping(external-port, protocol, internal-host, internal-port, description, remote-host)
            port_result = self.upnp.addportmapping(external_port, 'TCP', self.upnp.lanaddr, internal_port,
                                                   'spectre upnp nap mapping', '')
            # logger.info('Port Forward Attempt: Mapping {0} --> {1} ... {2}'.format(internal_port, external_port, 'OK' if port_result else 'Fail'))
            # if succeed, return (external_ip, external_port)
            return (self.upnp.externalipaddress(), external_port)
        except Exception as e:
            logger.error('Error in upnp nat port forward: %s', e)
            # Bind find, return None
            return None

    def removePortForward(self, external_port):
        try:
            discover = self.upnp.discover()
            igd = self.upnp.selectigd()
            port_result = self.upnp.deleteportmapping(external_port, 'TCP')
            logger.info("Port Delete Attempt: ~{0} ... {1}".format(external_port, 'OK' if port_result else 'Fail'))
            return True
        except Exception as e:
            logger.error('Error in upnp nat port remove: %s', e)
            return False

