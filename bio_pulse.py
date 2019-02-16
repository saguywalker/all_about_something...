import os
import pandas as pd
import numpy as np
import mne
import sys
import datetime
import re

pattern_time = re.compile('\d+:\d+:\d+.\d+')
pattern_date = re.compile('\d+-\d+-\d+')

def get_data(file):
    path = os.path.join(file[0], file[1])
    data = pd.read_csv(path)
    if data.shape[0] != 6:
        for col in data:
            if "sampling rate" in col:
                srate = float(col[-3:])
            elif "time" in col:
                time = pattern_time.search(col).group()
            elif "date" in col:
                date = pattern_date.search(col).group()
        data = data.values[1:, 4]
        timestamp = datetime.datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S.%f")
    else:
        srate = 300
        timestamp = datetime.datetime.now()
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
        timestamp = data[0] + datetime.timedelta(seconds=time)
        ans = "{:.2f}".format(60/duration)
        hr.append((timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-1], ans))
    return (np.array(hr), times[-1], avg_pulse)

def write_output(result):
    print("writing...")
    

if __name__ == "__main__":
    file_path = os.path.join(sys.argv[1], "Biosignalsplux")
    files = [(file_path, f) for f in os.listdir(file_path) if ".csv" in f]
    print("List of files...")
    for file in files:
        print(file)
    data = [get_data(file) for file in files]
    hr = [get_hr(d) for d in data]

    for i, x in enumerate(hr):
        print("Reading {}, avg_hr: {:.2f}, times: {:.2f}, srate: {} ...".format(files[i][1], x[2], x[1], data[i][1]))
        print(x[0])
        
