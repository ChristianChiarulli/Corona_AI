import collections, queue
import numpy as np
import pyaudio
import webrtcvad
from scipy import signal
import websockets
import deepspeech
import asyncio


class Audio(object):

    FORMAT = pyaudio.paInt16
    RATE_PROCESS = 16000  # VAD only supports 16kHz
    CHANNELS = 1  # VAD only supprts 1 channel
    BLOCKS_PER_SECOND = 50

    def __init__(self, device, input_rate=RATE_PROCESS):
        def proxy_callback(in_data, frame_count, time_info, status):
            # pylint: disable=unused-argument
            callback(in_data)
            return (None, pyaudio.paContinue)

        callback = lambda in_data: self.buffer_queue.put(in_data)

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
        # print(self.)
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
        data16 = np.fromstring(string=data, dtype=np.int16)
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


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness, device, input_rate):
        super().__init__(device=device, input_rate=input_rate)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        # No frames
        if frames is None:
            frames = self.frame_generator()

        # We have frames
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            if len(frame) < 640:
                return

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()


async def main():

    BEAM_WIDTH = 500
    LM_ALPHA = 0.75
    LM_BETA = 1.85
    MODEL = "./models/output_graph.pbmm"
    LANG_MODEL = "./models/lm.binary"
    TRIE = "./models/trie"

    model = deepspeech.Model(MODEL, BEAM_WIDTH)
    model.enableDecoderWithLM(LANG_MODEL, TRIE, LM_ALPHA, LM_BETA)
    vad_audio = VADAudio(aggressiveness=3, device=9, input_rate=44100)

    uri = "ws://localhost:8000/ws"
    ws = await websockets.connect(uri, ping_interval=None)

    stream_context = model.createStream()
    for frame in vad_audio.vad_collector():
        if frame is not None:
            model.feedAudioContent(stream_context, np.frombuffer(frame, np.int16))
        else:
            text = model.finishStream(stream_context)
            try:
                await ws.send(text)
                stream_context = model.createStream()
                returned = await ws.recv()
                print(returned)
            except:  # there is clearly a better ay to do this but I have a smol brain
                print("Reconnecting")
                ws = await websockets.connect(uri, ping_interval=None)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
