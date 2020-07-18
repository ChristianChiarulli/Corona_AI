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
