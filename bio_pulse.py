#!/usr/bin/ python3

import os
import pandas as pd
import numpy as np
import mne
import sys
import datetime
import re

P_TIME = re.compile('\d+:\d+:\d+.\d+')
P_DATE = re.compile('\d+-\d+-\d+')

def get_data(file):
    path = os.path.join(file[0], file[1])
    data = pd.read_csv(path)

    for col in data:
        if "sampling rate" in col:
            srate = float(col[-3:])
        if "time" in col:
            time = P_TIME.search(col).group()
        if "date" in col:
            date = P_DATE.search(col).group()
    data = data.values[1:, 4]
    timestamp = datetime.datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S.%f")

    return (timestamp, srate, data.astype(np.float32))


#for Empatica


def get_hr(data):
    info = mne.create_info(ch_names=["ECG"], sfreq=data[1], ch_types=["ecg"])
    raw = mne.io.RawArray(data[2].reshape(1, -1), info)
    times = np.arange(0, data[2].shape[0] / data[1], 1 / data[1])

    events , _, avg_pulse = mne.preprocessing.find_ecg_events(raw, h_freq=8, l_freq=1)
    events = events[:,0]
    hr = []
    for i in range(events.shape[0] - 1):
        time = (times[events[i]] + times[events[i+1]]) / 2
        duration = times[events[i+1]] - times[events[i]]
        timestamp = data[0] + datetime.timedelta(seconds=time)
        ans = "{:.2f}".format(60/duration)
        hr.append([timestamp, ans])
        #hr.append((timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-1], ans))
    print("{} hr(s) was found from {} events, ({},{},{})\n".format(len(hr), events.shape, data[0], data[1], data[2].shape))
    return (hr, times[-1], avg_pulse)

def write_output(fname, results):
    all_data = results[0][0]
    print("first data's file:",len(all_data), len(all_data[0]))
    print("len: {}".format(len(results)))
    if len(results) > 1:
        for r in results[1:]:
            print("data shape: {}".format(len(r[0])))
            if len(r[0]) > 0:
                all_data = np.concatenate((all_data, r[0]), axis=0)
    print("all data:", all_data.shape)
    all_data[all_data[:, 0].argsort()]
    df = pd.DataFrame(all_data, columns=["Timestamp", "HR_BVP_empatica"])
    #df.to_csv(os.path.join("heartrate",fname+"_biosignalsplux_mne.csv"), index_label="index", na_rep=None)
    df.to_csv(os.path.join("bvp_empatica",fname+"_mne.csv"), index_label="Index", na_rep=None)

def read_each_folder(folder, sub_folder):
    file_path = os.path.join(folder, sub_folder)
    files = [(file_path, f) for f in os.listdir(file_path) if "Bvp" in f]
    print("List of files...")
    for file in files:
        print(file)
    data = [get_data(file) for file in files]
    hr = [get_hr(d) for d in data]

    write_output(folder, hr)
    print("{} is writed".format(folder))
    print("*"*30)

if __name__ == "__main__":
    folders = [f for f in os.listdir() if "Subject0" in f or "Subject10" in f]
    folders.sort()
    #folders = [sys.argv[1]]
    for folder in folders:
        read_each_folder(folder, "Empatica")
