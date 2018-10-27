# Google Cloud API + dictionary version of profanity detecting

import io
import logging
import os
import json

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

logger = logging.getLogger(__name__)

with open('obscene.json') as f:
    obscene_json = json.load(f)
    obscene_words = [word for word in obscene_json if obscene_json[word] > 0]

client = speech.SpeechClient()

def get_timestamps_from_gc(input_path_wav):
    with io.open(input_path_wav, 'rb') as audio_file:
        content = audio_file.read()
        recaudio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        #sample_rate_hertz=16000,
        enable_word_time_offsets=True,
        language_code='en-US')

    # Detects speech in the audio file
    logger.warning('perfoming a Google API request...')
    response = client.recognize(config, recaudio)
    logger.warning('done!')
    
    timestamps = []

    for result in response.results:
        alternative = result.alternatives[0]

        for word_info in alternative.words:
            if word_info.word in obscene_words:
                start_time = word_info.start_time.seconds * 1000 + word_info.start_time.nanos // 1000000
                end_time = word_info.end_time.seconds * 1000 + word_info.end_time.nanos // 1000000
                timestamps.append((start_time, end_time))
    return timestamps

