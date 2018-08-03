import requests
url_start = 'https://www.physionet.org/pn4/eegmmidb/S025/S025R'
url_end = '.edf'
file_start = 'S025R'
for i in range(1,15):
    res = requests.get(url_start+str(i).zfill(2)+url_end)
    with open(file_start+str(i).zfill(2)+url_end,'wb') as code:
        code.write(res.content)
