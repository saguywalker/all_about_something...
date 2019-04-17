#!/usr/bin/ python3

import os
import pandas as pd
import numpy as np
import mne
import sys
import datetime
import re

#regex for matching time and date in the first row
P_TIME = re.compile('\d+:\d+:\d+.\d+')
P_DATE = re.compile('\d+-\d+-\d+')
SUBJECTS = re.compile('Subject\d\d')


'''
    fetch_data
    parameter: - path
               - file name
    return: - timestamp object
            - sampling rate
            - ecg data
'''
def fetch_data(path_name, file_name):
    #read a file into DataFrame
    path = os.path.join(path_name, file_name)
    data = pd.read_csv(path)

    #find the detail of sampling rate, time and date from the first row.
    for col in data:
        if "sampling rate" in col:
            srate = float(col[-3:])
        if "time" in col:
            time = P_TIME.search(col).group()
        if "date" in col:
            date = P_DATE.search(col).group()
    
    #get only ecg column
    data = data.values[1:, 4]

    #create timestamp object
    timestamp = datetime.datetime.strptime(date+" "+time, "%Y-%m-%d %H:%M:%S.%f")

    return (timestamp, srate, data.astype(np.float32))


'''
    calculate_hr
    parameter: - timestamp object
               - sampling rate
               - ecg data
    return: tuple that contains timestamp and heart rate at that time
'''
def calculate_hr(start_time, sampling_rate, ecg_data):
    #info data according to sampling rate and channel
    info = mne.create_info(ch_names=["ECG"], sfreq=sampling_rate, ch_types=["ecg"])
    #raw mne data from ecg_data
    raw = mne.io.RawArray(ecg_data.reshape(1, -1), info)
    #time(sec) array from ecg_data
    times = np.arange(0, ecg_data.shape[0] / sampling_rate, 1 / sampling_rate)
    #get index of peaks
    events , _, _ = mne.preprocessing.find_ecg_events(raw, h_freq=8, l_freq=1)
    #pick only peak indexes
    events = events[:,0]
    
    #calculate heart rate of each consecutive pair of peak events
    #hr variable contains tuple of timestamp and heart rate result in that time.
    hr = []
    for i in range(events.shape[0] - 1):
        time = (times[events[i]] + times[events[i+1]]) / 2          #mid-point of each pair
        duration = times[events[i+1]] - times[events[i]]            #find duration between peaks
        timestamp = start_time + datetime.timedelta(seconds=time)   #timestamp in that time
        ans = "{:.2f}".format(60/duration)                          #calculate heart rate (60/duration)
        hr.append((timestamp, ans))             
    print("{} hr(s) was found from {} events, ({},{},{})\n".format(len(hr), events.shape, start_time, sampling_rate, ecg_data.shape))
    
    return hr


'''
    write_output
    parameter: - file name
               - list of tuple of timestamp and heart rate
'''
def write_output(fname, hr_results):
    #concate all data from the specific subject
    all_data = np.array(hr_results[0])
    if len(hr_results) > 1:
        for r in hr_results[1:]:
            if len(r) > 0:
                all_data = np.concatenate((all_data, r), axis=0)
    print("shape from all data: {}".format(all_data.shape))

    #sort by timestamp
    all_data[all_data[:, 0].argsort()]
    #create DataFrame 
    df = pd.DataFrame(all_data, columns=["Timestamp", "HR_biosignalsplux"])
    #create output folder
    if not os.path.exists("heartrate_results"):
        os.makedirs("heartrate_results")
    #write file
    df.to_csv(os.path.join("heartrate_result",fname+"_biosignalsplux_mne.csv"), index=True, na_rep=None)


'''
    read_each_folder
    parameter: - subject folder name
               - sub folder name
'''
def read_each_folder(folder, sub_folder):
    file_path = os.path.join(folder, sub_folder)
    #list of tuple of file_path and file name
    files = [(file_path, f) for f in os.listdir(file_path) if ".csv" in f]
    print("List of files...")
    for file in files:
        print(file)


    data = [fetch_data(*file) for file in files]
    hr = [calculate_hr(*d) for d in data]

    write_output(folder, hr)
    print("{} is writed".format(folder))
    print("*"*50)


#"python3 hr-mne.py Subject11"
if __name__ == "__main__":
    #subject = sys.argv[1]
    #folders = [f for f in os.listdir() if subject in f]

    #select only Subject files
    folders = [f for f in os.listdir() if SUBJECTS.search(f)] 
    folders.sort()
    for folder in folders:
        read_each_folder(folder, "Biosignalsplux")
