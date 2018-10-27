# Credits to @Tony607: https://github.com/Tony607/Keras-Trigger-Word/

import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import os
from pydub import AudioSegment

# Calculate and plot spectrogram for a wav audio file
def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    nperseg = 200
    fs = 8000 
    noverlap = 120
    nchannels = data.ndim
    if nchannels == 1:
        freqs, times, pxx = spectrogram(data, fs=fs, nperseg=nperseg, noverlap = noverlap)
    elif nchannels == 2:
        freqs, times, pxx = spectrogram(data[:,0], fs=fs, nperseg=nperseg, noverlap = noverlap)
    return pxx, data, rate, times

# Load a wav file
def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

# Used to standardize volume of audio clip
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

# Load raw audio files for speech synthesis
def load_raw_audio():
    activates = []
    backgrounds = []
    vols = []
    negatives = []
    for filename in os.listdir("./ml/raw_data/activates"):
        if filename.endswith("wav"):
            activate = AudioSegment.from_wav("./ml/raw_data/activates/"+filename)
            vols.append(activate.max_dBFS)
            activates.append(activate)
    for filename in os.listdir("./ml/raw_data/backgrounds"):
        if filename.endswith("wav"):
            background = AudioSegment.from_wav("./ml/raw_data/backgrounds/"+filename)
            backgrounds.append(background)
    for filename in os.listdir("./ml/raw_data/negatives"):
        if filename.endswith("wav"):
            negative = AudioSegment.from_wav("./ml/raw_data/negatives/"+filename)
            vols.append(negative.max_dBFS)
            negatives.append(negative)
    max_vol = max(vols)
    for i in range(len(activates)):
        activates[i] -= (max_vol - activates[i].max_dBFS)
    for i in range(len(negatives)):
        negatives[i] -= (max_vol - negatives[i].max_dBFS)
    return activates, negatives, backgrounds
