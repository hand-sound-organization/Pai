import threading
import RPi.GPIO as GPIO
import serial
from Lock_Server.MFCC import MFCC
from Lock_Server.play import Play
from multiprocessing import Manager
import numpy as npy
import time
from sklearn.externals import joblib
import os
from Lock_Server.dbconfig import Base, engine, User,Threshold
from sqlalchemy.orm import sessionmaker



class Vibration(threading.Thread):
    def __init__(self,event):
        super().__init__()
        self.event = event
        self.vibration = ''
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN)
        GPIO.add_event_detect(11, GPIO.RISING)

    def run(self):
        while True:
            self.event.wait()
            if GPIO.event_detected(11):
                manager = Manager()
                queue = manager.Queue()
                vectors = npy.ones((1, 2000))
                queue.put(vectors)
                mfcc = MFCC('Lock_Server/vibration.wav', queue)
                play = Play()
                play.start()
                time.sleep(0.16)
                mfcc.start()
                play.join()
                mfcc.join()
                time.sleep(1)
                vectors = queue.get()
                vector = vectors[1,:]
                path = "C:\\Users\\asus\\Desktop\\信息安全\\Pai"
                files = os.listdir(path)
                for file_bl in files:
                    position_bl = path + '\\' + file_bl
                    if "bl.model" in position_bl:
                        head_bl = position_bl[:position_bl.find("bl.model")]
                        for file_pos in files:
                            position_pos = path + '\\' + file_pos
                            if "pos.model" in position_pos:
                                head_pos = position_pos[:position_pos.find("pos.model")]
                                if head_bl == head_pos:
                                    ctl_bl = joblib.load(position_bl)
                                    ctl_pos = joblib.load(position_pos)
                                    dist_bl, ind_bl = ctl_bl.kneighbors(vector, n_neighbors=3)
                                    E_bl = npy.mean(dist_bl, axis=1)
                                    dist_pos, ind_pos = ctl_pos.kneighbors(vector, n_neighbors=3)
                                    E_pos = npy.mean(dist_pos, axis=1)
                                    a = 0.19
                                    newthreshold = (1-a)*E_pos + a*E_bl
                                    Session = sessionmaker(bind=engine)
                                    session = Session()
                                    thresholds = session.query(Threshold).all()
                                    for threshold in thresholds:
                                        if newthreshold < threshold:
                                            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
                                            ser.write('1'.encode())








