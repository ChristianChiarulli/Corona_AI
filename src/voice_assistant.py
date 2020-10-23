import os
import deepspeech
import numpy as np
from halo import Halo
from vad import VADAudio


def main():
    # Load DeepSpeech model
    print('Initializing model...')
    model = deepspeech.Model('../models/deepspeech-0.8.2-models.pbmm')

    # Start audio with VAD
    vad_audio = VADAudio(aggressiveness=3,
                         device=11,
                         input_rate=48000)

    print("Listening (ctrl-C to exit)...")
    frames = vad_audio.vad_collector()

    # Stream from microphone to DeepSpeech using VAD
    # spinner = None
    spinner = Halo(spinner='line')
    stream_context = model.createStream()
    for frame in frames:
        if frame is not None:
            if spinner: spinner.start()
            # print("streaming frame")
            stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
        else:
            if spinner: spinner.stop()
            print("end utterence")
            text = stream_context.finishStream()
            print(f"Recognized: {text}")
            # function call for commands
            if "browser" in text:
                print("EXECUTING COMMAND")
                os.system("/usr/bin/brave")
            if "code" in text:
                print("EXECUTING COMMAND")
                os.system("/usr/bin/code-insiders")
                
            stream_context = model.createStream()

if __name__ == '__main__':
    main()