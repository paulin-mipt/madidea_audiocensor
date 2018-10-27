import io
import os
import json
from pydub import AudioSegment

from google_cloud_cens import get_timestamps_from_gc

censor_beep = AudioSegment.from_wav('./censor-beep.wav')
censor_beep = censor_beep + censor_beep + censor_beep + censor_beep + censor_beep # for long words

def get_censrored_timestamps(input_path_wav):
    '''Returns: [(start_ms, end_ms)]'''
    # TODO
    return get_timestamps_from_gc(input_path_wav)

def censore(input_path_ogg):
    '''Returns: path for the output file'''
    
    audio = AudioSegment.from_ogg(input_path_ogg)
    input_path_wav = input_path_ogg[:-4] + '.wav'
    audio.set_channels(1).export(input_path_wav, format='wav')
    
    censored_timestamps = get_censrored_timestamps(input_path_wav)
    if len(censored_timestamps) == 0:
        return None # nothing to censore
    
    for start_ms, end_ms in censored_timestamps:
        audio = audio[:start_ms] + censor_beep[:(end_ms-start_ms)] + audio[end_ms:]
    
    output_path_ogg = input_path_ogg[:-4] + '_c.ogg'
    audio.export(output_path_ogg, format='ogg')
    return output_path_ogg
