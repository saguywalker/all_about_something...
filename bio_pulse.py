import os
import pandas as pd
import numpy as np
import mne
import sys

SFREQ = 3000
info = mne.create_info(ch_names=["ECG"], sfreq=SFREQ, ch_types=["ecg"])
TIME_RANGE = 6*3000

def get_data(file):
    path = os.path.join(file[0], file[1])
    data = pd.read_csv(path).values
    if data.shape[0] != 6:
        data = data[1:, 4]
    else:
        data = data[:, 4]
    if data.shape[0] < 9000:
        return None

    return data.astype(np.float32)

def get_hr(data):
    raw = mne.io.RawArray(data.reshape(1, -1), info)
    times = np.arange(0, data.shape[0] / SFREQ, 1 / SFREQ)
    events , _, _ = mne.preprocessing.find_ecg_events(raw)
    events = events[:,0]
    #avg_pulse = events.shape[0] * 60.0 / (times[-1] - times[0])
    hr = []
    for i in range(events.shape[0] - 1):
        #print("2 peaks are {} and {}".format(events[i], events[i+1]))
        duration = times[events[i+1]] - times[events[i]]
        #print("duration = {}, heart rate = {}".format(duration, 60/duration))
        hr.append(((events[i],events[i+1]), 60 / duration))
        
    return hr

if __name__ == "__main__":
    file_path = os.path.join(sys.argv[1], "Biosignalsplux")
    files = [(file_path, f) for f in os.listdir(file_path) if ".csv" in f]
    print("List of files: {}".format(files))
    data = [[file[1], get_data(file)] for file in files]
    hr = [[d[0], get_hr(d[1])] for d in data]
    for x in hr:
        print("Reading {} ...".format(x[0]))
        for xx in x[1]:
            print("Index: {}, heart rate = {}".format(xx[0], xx[1]))
        print("*"*30)


