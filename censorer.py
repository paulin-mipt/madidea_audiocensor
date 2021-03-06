import io
import os
import numpy as np
from ml import analyzer
from pydub import AudioSegment
from google_cloud_cens import get_timestamps_from_gc

class Censorer:

    def __init__(self, use_google_cloud=True):
        self.use_google_cloud = use_google_cloud
        self.censor_beep = AudioSegment.from_wav('./censor-beep.wav')
        self.censor_beep = self.censor_beep * 10 # 10 beeps in a row for long words

        self.model = analyzer.get_model()
        self.model._make_predict_function()

    def get_censored_timestamps(self, input_path_wav):
        '''Returns: [(start_ms, end_ms)]'''
        if self.use_google_cloud:
            return get_timestamps_from_gc(input_path_wav)
        else:
            data, rate, borders = analyzer.get_trigger_timestamps(self.model, './ml/raw_data/speech.wav')
            return borders

    def censore(self, input_path_ogg):
        '''Returns: path for the output file'''
        
        audio = AudioSegment.from_ogg(input_path_ogg)
        input_path_wav = input_path_ogg[:-4] + '.wav'
        audio.set_channels(1).export(input_path_wav, format='wav')
        
        censored_timestamps = self.get_censored_timestamps(input_path_wav)
        if len(censored_timestamps) == 0:
            return None # nothing to censore
        
        censor_beep_norm = self.censor_beep.apply_gain(np.average(audio.dBFS) - self.censor_beep.max_dBFS)
        for start_ms, end_ms in censored_timestamps:
            audio = audio[:start_ms] + censor_beep_norm[:(end_ms-start_ms)] + audio[end_ms:]
        
        output_path_ogg = input_path_ogg[:-4] + '_c.ogg'
        audio.export(output_path_ogg, format='ogg')
        return output_path_ogg
