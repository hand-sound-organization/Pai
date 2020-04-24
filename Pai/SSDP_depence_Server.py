# import sys
# from SSDP.ssdp_upnp.ssdp import Server, Client, Nat
# from SSDP.ssdp_upnp.ssdp import gen_logger
# from queue import Queue
from Pai.Lock_SSDP.Lock_Server import Server
# logger = gen_logger('sample')

if __name__ == '__main__':
    upnpServer = Server(8048, 'LockSSDP', 'TouchVoiceNet')
    upnpServer.start()

