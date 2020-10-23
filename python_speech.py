# pip install gTTS speechrecognition pyaudio playsound PyObjC
# conda install -c conda-forge pygobject
import speech_recognition as sr
import webbrowser
import time
# import playsound
# import os
# import random
# from gtts import gTTS
from time import ctime

r = sr.Recognizer()


def record_audio(ask=False):
    with sr.Microphone(device_index=10) as source:
        if ask:
            print(ask)
        audio = r.listen(source)
        voice_data = ""
        try:
            voice_data = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Sorry, I did not get that")
        except sr.RequestError:
            print("Sorry, my speech service is down")
        return voice_data


# def speak(audio_string):
#     tts = gTTS(text=audio_string, lang="en")
#     r = random.randint(1, 1000000)
#     audio_file = "/home/chris/Repos/python_speech_assistant/audio-" + str(r) + ".mp3"
#     print(audio_file)
#     tts.save(audio_file)
#     playsound.playsound(audio_file)
#     print(audio_string)
#     os.remove(audio_file)


def respond(voice_data):
    if "what is your name" in voice_data:
        print("My name is Nick")
    if "what time is it" in voice_data:
        print(ctime())
    if "search" in voice_data:
        search = record_audio("What do want to search for?")
        url = "http://google.com/search?q=" + search
        webbrowser.get().open(url)
        print("Here is what I found for " + search)
    if "find location" in voice_data:
        location = record_audio("What is the location?")
        url = "http://google.nl/maps/place/" + location + "/&amp;"
        webbrowser.get().open(url)
        print("Here is the location of " + location)
    if "exit" in voice_data:
        exit()


time.sleep(1)

print("How can I help you?")
while 1:
    voice_data = record_audio()
    respond(voice_data)
