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
    print(data.shape, times.shape, times[-1])
    events , _, avg_pulse = mne.preprocessing.find_ecg_events(raw)
    events = events[:,0]
    hr = []
    for i in range(events.shape[0] - 1):
        duration = times[events[i+1]] - times[events[i]]
        hr.append( ((times[events[i]],times[events[i+1]]), 60 / duration))
    return (hr, times[-1], avg_pulse)

if __name__ == "__main__":
    file_path = os.path.join(sys.argv[1], "Biosignalsplux")
    files = [(file_path, f) for f in os.listdir(file_path) if ".csv" in f]
    print("List of files: {}".format(files))

    data = [get_data(file) for file in files]
    hr = [get_hr(d) for d in data]
    for i, x in enumerate(hr):
        print("Reading {}, avg_hr: {:.2f}, times: {:.2f} ...".format(files[i][1], x[1], x[2]))
        for xx in x[0]:
            print("heart rate of ({:.2f}, {:.2f}): {:.2f}".format(xx[0][0], xx[0][1], xx[1]))
        

