import numpy
import scipy.io.wavfile
from scipy.fftpack import dct
from multiprocessing import Process
import pyaudio
import wave



class MFCC(Process):
    def __init__(self, file,queue):
        super().__init__()
        self.file = file
        self.queue = queue

    def run(self):
        self.vibration_product()
        self.mfcc_fearture_extraction(self.file)

    def vibration_product(self):
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second
        seconds = 1
        filename = "Lock_Server/vibration.wav"

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)
        # print(frames)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

    def mfcc_fearture_extraction(self,source):
        sample_rate, signal = scipy.io.wavfile.read(source)
        # sample_rate 采样率，表示一秒采样个数
        # print(sample_rate, signal.shape[0])
        # 读取前3.5s 的数据
        signal = signal[0:int(1 * sample_rate)]
        print("+++++++++++++++++++++")
        # print(signal.shape)
        # plt.plot(signal)

        # # 预先处理
        # pre_emphasis = 0.97
        # emphasized_signal = numpy.append(signal[0], signal[1:] - pre_emphasis * signal[:-1])
        mu = numpy.average(signal)
        sigma = numpy.std(signal)
        emphasized_signal = (signal - mu) / sigma

        frame_size = 0.0025  # 0.025  0.0025
        frame_stride = 0.01  # 0.1    0.01
        frame_length, frame_step = frame_size * sample_rate, frame_stride * sample_rate
        signal_length = len(emphasized_signal)
        frame_length = int(round(frame_length))
        frame_step = int(round(frame_step))
        num_frames = int(numpy.ceil(float(numpy.abs(signal_length - frame_length)) / frame_step))

        pad_signal_length = num_frames * frame_step + frame_length
        z = numpy.zeros((pad_signal_length - signal_length))
        pad_signal = numpy.append(emphasized_signal, z)

        indices = numpy.tile(numpy.arange(0, frame_length), (num_frames, 1)) + numpy.tile(
            numpy.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T

        frames = pad_signal[numpy.mat(indices).astype(numpy.int32, copy=False)]

        # 加上汉明窗
        frames *= numpy.hamming(frame_length)
        # frames *= 0.54 - 0.46 * numpy.cos((2 * numpy.pi * n) / (frame_length - 1))  # Explicit Implementation **

        # 傅立叶变换和功率谱
        NFFT = 512
        mag_frames = numpy.absolute(numpy.fft.rfft(frames, NFFT))  # Magnitude of the FFT
        # print(mag_frames.shape)
        pow_frames = ((1.0 / NFFT) * ((mag_frames) ** 2))  # Power Spectrum 功率谱

        low_freq_mel = 0
        # 将频率转换为Mel
        nfilt = 40  # 在low_freq 和 high_freq之间等间隔划分的个数
        #########################################################原代码
        # high_freq_mel = (2595 * numpy.log10(1 + (sample_rate / 2) / 700))
        # mel_points = numpy.linspace(low_freq_mel, high_freq_mel, nfilt + 2)  # Equally spaced in Mel scale 等间距成梅尔刻度
        # hz_points = (700 * (10 ** (mel_points / 2595) - 1))  # Convert Mel to Hz 将梅尔转换为Hz ？？？？？？
        #
        # bin = numpy.floor((NFFT + 1) * hz_points / sample_rate) # 对梅尔转换为Hz的数组每一个数字向下取整
        # fbank = numpy.zeros((nfilt, int(numpy.floor(NFFT / 2 + 1))))  # 生成一个2维数组，横长nfilt，纵长NFFT / 2 + 1向下取整
        ###########################################################
        ###########################################################新代码
        hz_points = numpy.linspace(low_freq_mel, sample_rate, nfilt + 2)
        bin = numpy.floor((NFFT / 2 + 1) * hz_points / sample_rate)
        fbank = numpy.zeros((nfilt, int(numpy.floor(NFFT / 2 + 1))))
        ###########################################################

        for m in range(1, nfilt + 1):  # 对每个刻度进行操作
            f_m_minus = int(bin[m - 1])  # left 左Hz刻度
            f_m = int(bin[m])  # center 中间Hz刻度
            f_m_plus = int(bin[m + 1])  # right 右Hz刻度
            for k in range(f_m_minus, f_m):  # 对从左Hz刻度 开始，到中间Hz刻度操作
                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
            for k in range(f_m, f_m_plus):
                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])  # 对从中间Hz刻度 开始，到右Hz刻度操作

        filter_banks = numpy.dot(pow_frames, fbank.T)  # dot代表两个矩阵乘积（不是简单标号相乘），fbank.T表示fbank的转置，
        filter_banks = numpy.where(filter_banks == 0, numpy.finfo(float).eps, filter_banks)  # Numerical Stability 数值稳定性
        filter_banks = 20 * numpy.log10(filter_banks)  # dB

        # 倒谱特征提取
        num_ceps = 20
        mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, 1: (num_ceps + 1)]
        (nframes, ncoeff) = mfcc.shape

        n = numpy.arange(ncoeff)
        cep_lifter = 22
        lift = 1 + (cep_lifter / 2) * numpy.sin(numpy.pi * n / cep_lifter)
        mfcc *= lift  # *

        # filter_banks -= (numpy.mean(filter_banks, axis=0) + 1e-8)
        mfcc -= (numpy.mean(mfcc, axis=0) + 1e-8)
        # plt.imshow(numpy.flipud(mfcc.T), cmap=plt.cm.jet, aspect=0.2, extent=[0,mfcc.shape[0],0,mfcc.shape[1]])#热力图

        # print(mfcc.shape)
        # print(mfcc)
        # plt.plot(filter_banks)
        # plt.axis([0, 100, -20, 135])
        # plt.show()
        mfcc = numpy.array(mfcc)
        mfcc = mfcc.flatten()
        mfcc = mfcc.reshape((1, 2000))
        print(mfcc)
        mfcc_vectors = self.queue.get(block=False)
        mfcc_vectors = numpy.append(mfcc_vectors, mfcc, axis=0)
        print(mfcc_vectors)
        # print(self.queue.qsize(),self.queue.empty())
        self.queue.put(mfcc_vectors,block=False,timeout=500)


