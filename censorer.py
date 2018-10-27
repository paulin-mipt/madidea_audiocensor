import io
import os
import numpy as np
from ml import analyzer
from pydub import AudioSegment

censor_beep = AudioSegment.from_wav('./censor-beep.wav')
censor_beep = censor_beep + censor_beep + censor_beep + censor_beep + censor_beep # for long words

model = analyzer.get_model()

def get_censored_timestamps(input_path_wav):
    '''Returns: [(start_ms, end_ms)]'''
    data, rate, borders = analyzer.get_trigger_timestamps(model, './ml/raw_data/speech.wav')
    return borders

def censore(input_path_ogg):
    '''Returns: path for the output file'''
    
    audio = AudioSegment.from_ogg(input_path_ogg)
    input_path_wav = input_path_ogg[:-4] + '.wav'
    audio.set_channels(1).export(input_path_wav, format='wav')
    
    censored_timestamps = get_censored_timestamps(input_path_wav)
    if len(censored_timestamps) == 0:
        return None # nothing to censore
    
    censor_beep_norm = censor_beep.apply_gain(np.average(audio.dBFS) - censor_beep.max_dBFS)
    for start_ms, end_ms in censored_timestamps:
        audio = audio[:start_ms] + censor_beep_norm[:(end_ms-start_ms)] + audio[end_ms:]
    
    output_path_ogg = input_path_ogg[:-4] + '_c.ogg'
    audio.export(output_path_ogg, format='ogg')
    return output_path_ogg
