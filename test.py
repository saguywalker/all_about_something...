'''import pyedflib
import numpy as np
import pandas as pd

def fetch_df(file_name):
    f = pyedflib.EdfReader(file_name)
    n = f.signals_in_file
    signal_labels = f.getSignalLabels()
    sigbufs = np.zeros((n,f.getNSamples()[0]))
    for i in np.arange(n):
        sigbufs[i,:] = f.readSignal(i)
    idx = ['Row'+str(i) for i in range(1,len(sigbufs)+1)]
    return pd.DataFrame(sigbufs,index=idx)

if __name__ == "__main__":
    arr = np.empty([14],dtype=object)
    for i in range(0,14):
        arr[i] = fetch_df("subjects/S025/S025R"+str(i+1).zfill(2)+".edf")
        print(arr[i].info())
        print('*'*99)
'''
import urllib.request
import numpy as np
import pyedflib
import pandas as pd

timeArray = np.array([round(x,5) for x in np.arange(0,124.5,.00625)])
timeArray = timeArray.reshape(19920,1)
reader = pyedflib.EdfReader('subjects/S001/S001R05.edf')
annotations = reader.readAnnotations()
intervals = np.append(annotations[0],[124.5])
codes = annotations[2]
codeArray = []
counter = 1
for timeVal in timeArray:
    if timeVal == 124.5:
        break
    elif timeVal / intervals[counter] == 1.0:
        counter += 1

    codeArray.append(codes[counter - 1])

invertCodeArray = np.array(codeArray).reshape(19920,1)
numSignals = reader.signals_in_file
signal_labels = reader.getSignalLabels()
dataset = np.zeros((numSignals, reader.getNSamples()[0]))
for signal in np.arange(numSignals):
    dataset[signal, :] = reader.readSignal(signal)

dataset = dataset[:,:-80].transpose()
masterSet = np.concatenate((timeArray,invertCodeArray,dataset),axis=1)

print(annotations[0])
