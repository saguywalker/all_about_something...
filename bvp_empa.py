import pandas as pd
import numpy as np
import os
from biosppy.signals import bvp
import mne
import sys
import re
from datetime import datetime

EMPATICA_PATH = "Empatica"
info = mne.create_info(ch_names=["ECG"], sfreq=64., ch_types=["ecg"])

if __name__ == "__main__":
    folders = [os.path.join(f, EMPATICA_PATH) for f in os.listdir() if "Subject0" in f or "Subject10" in f]
    folders.sort()
    bvp_files = [(folder, [file for file in os.listdir(folder) if "Bvp" in file]) for folder in folders]
    hr_files = [(folder, [file for file in os.listdir(folder) if "Hr" in file]) for folder in folders]
    bvp_files.sort()
    hr_files.sort()
    for i in range(len(bvp_files)):
        bvp_files[i][1].sort()
        hr_files[i][1].sort()

    all_data = []
    for i, bvp_file in enumerate(bvp_files):
        for j, f in enumerate(bvp_file[1]):
            df = pd.read_csv(os.path.join(bvp_file[0], f))
            data = df.values[:, 2]
            timestamps = df.values[:,0]
            data = pd.read_csv(os.path.join(bvp_file[0], f)).values[:, 2]
            if data.shape[0] > 384:
                raw = mne.io.RawArray(data.reshape(1, -1), info)
                times = np.arange(0, data.shape[0] / 64, 1 / 64)    
                events , _, avg_pulse = mne.preprocessing.find_ecg_events(raw, h_freq=8, l_freq=1)
                events = events[:,0]
                
                hr = []
                for k in range(events.shape[0] - 1):
                    ts = datetime.fromtimestamp(timestamps[events[k]]).strftime("%Y-%m-%d %H:%M:%S.%f")
                    time = ((times[events[k]] + times[events[k+1]]) / 2)
                    duration = times[events[k+1]] - times[events[k]]
                    ans = "{:.2f}".format(60 / duration)
                    if float(ans) >= 40 and float(ans) <= 200:
                        hr.append([ts, ans])
                hr = np.array(hr)
                df_result = pd.DataFrame(hr, columns=["Timestamp", "HR_BVP_empatica"])
                df_result.to_csv(os.path.join("bvp_empatica", f[:-4]+"_mne.csv"), index=False, na_rep=None)


                sampling_rate = "{:.2f}".format(hr.shape[0] / times[-1])
                #ts, filtered, onsets, hr_ts, hr = bvp.bvp(data, sampling_rate=64., show=False)
                raw_hr = pd.read_csv(os.path.join(bvp_file[0], hr_files[i][1][j])).values[:, 2]
                all_data.append((f, hr.shape[0], raw_hr.shape[0], sampling_rate))


    for data in all_data:
        print("{0}: number of hr = {1} ({2}), sampling rate of hr: {3}".format(data[0], data[1],data[2], data[3]))
        #print(data[0])
        #print("number of hr: {}, sampling rate of hr: {}".format(data[1], data[2]))
        print()

    df = pd.DataFrame(all_data, columns=["File", "No.HR_from_mne", "No.HR_from_file", "Sampling rate"])
    df.to_csv("mne-bvp.csv", index=False)
