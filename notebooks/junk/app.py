import deepspeech
import numpy as np
import speech_recognition as sr
import time
from time import ctime
# import scipy.signal as sps
from scipy import signal

BEAM_WIDTH = 500
LM_ALPHA = 0.75
LM_BETA = 1.85
# MODEL = "./models/output_graph.pbmm"
MODEL = "./models/deepspeech-0.7.4-models.pbmm"
LANG_MODEL = "./models/lm.binary"
TRIE = "./models/trie"
RATE_PROCESS = 16000  # VAD only supports 16kHz

r = sr.Recognizer()

def resample(data, input_rate):
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
    resample_size = int(len(data16) / input_rate * RATE_PROCESS)
    resample = signal.resample(data16, resample_size)
    resample16 = np.array(resample, dtype=np.int16)
    return resample16.tostring()

# def record_audio():
with sr.Microphone(device_index=10) as source:
    audio = r.listen(source)
    # print(audio.frame_data)
    try:
        # number_of_samples = round(len(audio.frame_data) * float(16000) / 44100)
        # print("NUMBER OF SAMPLES: ", number_of_samples)
        # print("AUDIO TYPE:", type(a))
        resampled_data = resample(audio.frame_data, 441000)
        print("MADE IT HERE")
        print("DATA:", resampled_data)
        # data = sps.resample(audio.frame_data[:,np.newaxis], number_of_samples)
        # print("DATA: ", data)
        model = deepspeech.Model('models/deepspeech-0.8.2-models.pbmm')
        stream_context = model.createStream()
        stream_context.feedAudioContent(np.frombuffer(resampled_data, np.int16))
        text = stream_context.finishStream()
        print("TEXT:", text)
        # voice_data = r.recognize_google(audio)
        print("YOU SAID:", text)
    except sr.UnknownValueError:
        print("Sorry, I did not get that")
    except sr.RequestError:
        print("Sorry, my speech service is down")
    



# time.sleep(1)

# print("How can I help you?")
# while 1:
# voice_data = record_audio()
# print(voice_data)

# model = deepspeech.Model(MODEL, BEAM_WIDTH)
# model.enableDecoderWithLM(LANG_MODEL, TRIE, LM_ALPHA, LM_BETA)

# stream_context = model.createStream()

# model.feedAudioContent()

# model.feedAudioContent(stream_context, np.frombuffer(frame, np.int16))