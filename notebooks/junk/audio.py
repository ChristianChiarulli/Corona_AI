import queue
import numpy as np
import pyaudio
from scipy import signal


class Audio(object):

    FORMAT = pyaudio.paInt16
    RATE_PROCESS = 16000  # VAD only supports 16kHz
    CHANNELS = 1  # VAD only supprts 1 channel
    BLOCKS_PER_SECOND = 50

    def __init__(self, device, input_rate=RATE_PROCESS):
        def proxy_callback(in_data, frame_count, time_info, status):
            callback(in_data)
            return (None, pyaudio.paContinue)

        def callback(in_data):
            return self.buffer_queue.put(in_data)

        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = pyaudio.PyAudio()

        kwargs = {
            "format": self.FORMAT,
            "channels": self.CHANNELS,
            "rate": self.input_rate,
            "input": True,
            "frames_per_buffer": self.block_size_input,
            "stream_callback": proxy_callback,
            "input_device_index": self.device,
        }

        print("CHANNELS: ", self.CHANNELS)

        self.chunk = None
        self.stream = self.pa.open(**kwargs)
        print("Stream Channels", self.stream._channels)
        print("Stream type", self.stream)
        self.stream.start_stream()

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech

        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        # read data in as a string and create a 1D numpy array
        data16 = np.fromstring(string=data, dtype=np.int16)
        # RATE_PROCESS= 16000 get the len of the data
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(), input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(
        lambda self: 1000 * self.block_size // self.sample_rate
    )
