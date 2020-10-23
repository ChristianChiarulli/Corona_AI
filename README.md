# Corona_AI

## Setup Environment

```
conda env create -f environment.yml
```

## Pull down models

```
curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.6.1/deepspeech-0.6.1-models.tar.gz

tar xvf deepspeech-0.6.1-models.tar.gz

mv deepspeech-0.6.1-models models
```

## Start the Server

```
uvicorn nlp_server:app --reload
```

## Begin speech recognition

```
python speech_recognition_vad.py
```

## Original Deepspeech VAD 

```
python speech_recognition_vad.py -v 3 -d 11 -r 48000 -m models/deepspeech-0.8.2-models.pbmm
```