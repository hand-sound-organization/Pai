# import pygame
# # import time
# #
# # musicPath = r"D:\CloudMusic\狐言-三无.mp3"
# # pygame.mixer.init()#初始化
# #
# # track = pygame.mixer.music.load(musicPath)#加载音乐
# # pygame.mixer.music.play()#播放

import pyaudio
import wave
import sys
from multiprocessing import Process
import os

class Play(Process):
    def __init__(self):
        super().__init__()

    def run(self):
        # os.system("challenge.wav")
        self.playaudio()
        sys.exit(0)

    def playaudio(self):
        CHUNK = 1024

        wf = wave.open("Lock_Server/challenge.wav", 'rb')

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=2,# wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)
            # print("not stop!,data=%s"%data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()