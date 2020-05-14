# import threading
# import RPi.GPIO as GPIO
# import serial
# import pyaudio
# import wave
#
# class Vibration(threading.Thread):
#     def __init__(self,event):
#         super().__init__()
#         self.event = event
#         self.vibration = ''
#         GPIO.setmode(GPIO.BOARD)
#         GPIO.setup(11, GPIO.IN)
#         GPIO.add_event_detect(11, GPIO.RISING)
#
#     def run(self):
#         while True:
#             self.event.wait()
#             if GPIO.event_detected(11):
#                 CHUNK = 1024
#
#                 wf = wave.open("challenge.wav", 'rb')
#
#                 p = pyaudio.PyAudio()
#                 stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                                 channels=2,  # wf.getnchannels(),
#                                 rate=wf.getframerate(),
#                                 output=True)
#
#                 data = wf.readframes(CHUNK)
#
#                 while data != b'':
#                     stream.write(data)
#                     data = wf.readframes(CHUNK)
#                     print("not stop!,data=%s" % data)
#
#                 stream.stop_stream()
#                 stream.close()
#                 p.terminate()
#                 wf.close()
#
#                 ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
#                 ser.write('1'.encode())
#
#
