from .utils import *
from keras.models import load_model
import numpy as np
import os


def get_model():
    def f1(y_true, y_pred):
        def recall(y_true, y_pred):
            """Recall metric.

            Only computes a batch-wise average of recall.

            Computes the recall, a metric for multi-label classification of
            how many relevant items are selected.
            """
            true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
            possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
            recall = true_positives / (possible_positives + K.epsilon())
            return recall

        def precision(y_true, y_pred):
            """Precision metric.

            Only computes a batch-wise average of precision.

            Computes the precision, a metric for multi-label classification of
            how many selected items are relevant.
            """
            true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
            predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
            precision = true_positives / (predicted_positives + K.epsilon())
            return precision
        precision = precision(y_true, y_pred)
        recall = recall(y_true, y_pred)
        return 2*((precision*recall)/(precision+recall+K.epsilon()))

    return load_model('./ml/model.h5', custom_objects={'f1': f1})

def get_wav_info(wav_file):
    rate, data = wavfile.read(wav_file)
    return rate, data

def graph_spectrogram(wav_file):
    rate, data = get_wav_info(wav_file)
    print(data.shape)
    nfft = 200
    fs = 8000 
    noverlap = 120
    nchannels = data.ndim
    if nchannels == 1:
        pxx, freqs, bins, im = plt.specgram(data, nfft, fs, noverlap = noverlap)
    elif nchannels == 2:
        pxx, freqs, bins, im = plt.specgram(data[:,0], nfft, fs, noverlap = noverlap)
    return pxx, data, rate, bins

THRESHOLD = 0.5

def get_trigger_timestamps(model, filename):
    x, data, rate, bins = graph_spectrogram(filename)
    data_len_in_seconds = data.shape[0] / rate
    # the spectogram outputs (freqs, Tx) and we want (Tx, freqs) to input into the model
    x  = x.swapaxes(0,1)
    x = np.expand_dims(x, axis=0)
    predictions = model.predict(x)
    
    def binarize_preds(preds, th=THRESHOLD):
        for index in range(preds.shape[1]):
            if preds[0, index, 0] > th:
                preds[0, index, 0] = 1
            else:
                preds[0, index, 0] = 0
    
    binarize_preds(predictions)
    
    def index_to_timestamp(index):
        data_len = data.shape[0]
        in_len = x.shape[1]
        out_len = predictions.shape[1]
        return index / out_len * data_len_in_seconds * 1000
    
    def get_borders(preds):
        borders = []
        cur_start = -1
        cur_finish = -1
        state = -1
        for index in range(preds.shape[1] - 1):
            if preds[0, index, 0] == 0 and preds[0, index + 1, 0] == 1:
                state = 1
                cur_start = index + 1
            if preds[0, index, 0] == 1 and preds[0, index + 1, 0] == 0:
                state = -1
                cur_finish = index
                borders.append(list(map(index_to_timestamp, [cur_start, cur_finish])))
                cur_start, cur_finish = -1, -1
        return borders
    
    borders = get_borders(predictions)
    return data, rate, borders

if __name__ == '__main__':
    model = get_model()
    data, rate, borders = get_trigger_timestamps(model, './raw_data/speech.wav')
    for i, brd in enumerate(borders):
        left, right = map(lambda x: int(x / 1000 * rate), brd)
        data_slice = data[left: right]
        wavfile.write('curse_{0}.wav'.format(i), rate, data_slice)
