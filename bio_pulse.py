import os
import pandas as pd
import numpy as np
import mne
import sys
import ownTime
import re

def get_data(file):
    path = os.path.join(file[0], file[1])
    data = pd.read_csv(path)
    if data.shape[0] != 6:
        for col in data:
            if "sampling rate" in col:
                srate = float(col[-3:])
            elif "time" in col:
                time = col[10:-1]
                nums = re.split(r'[:.]', time)
                timestamp = ownTime.Time(int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]))
        data = data.values[1:, 4]
    else:
        srate = 300
        timestamp = ownTime.Time(0,0,0,0)
        data = data.values[:, 4]

    return (timestamp, srate, data.astype(np.float32))

def get_hr(data):
    info = mne.create_info(ch_names=["ECG"], sfreq=data[1], ch_types=["ecg"])
    raw = mne.io.RawArray(data[2].reshape(1, -1), info)
    times = np.arange(0, data[2].shape[0] / data[1], 1 / data[1])

    events , _, avg_pulse = mne.preprocessing.find_ecg_events(raw)
    events = events[:,0]
    hr = []
    for i in range(events.shape[0] - 1):
        time = (times[events[i]] + times[events[i+1]]) / 2
        duration = times[events[i+1]] - times[events[i]]
        timestamp = data[0].add(time)
        print("{:.2f}, {}".format(time, timestamp))
        hr.append((timestamp, 60 / duration))
    return (hr, times[-1], avg_pulse)

if __name__ == "__main__":
    file_path = os.path.join(sys.argv[1], "Biosignalsplux")
    files = [(file_path, f) for f in os.listdir(file_path) if ".csv" in f]
    print("List of files: {}".format(files))

    data = [get_data(file) for file in files]
    hr = [get_hr(d) for d in data]

    """for i, x in enumerate(hr):
        print("Reading {}, avg_hr: {:.2f}, times: {:.2f} ...".format(files[i][1], x[2], x[1]))
        for xx in x[0]:
            print("time: {}, hr = {:.2f}".format(xx[0], xx[1]))"""
        
