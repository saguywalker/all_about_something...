import requests
import os
from six.moves import urllib

download_root = 'https://www.physionet.org/pn4/eegmmidb/'
file_end = '.edf'

def download_data():
    if not os.path.isdir("subjects"):
        os.makedirs("subjects")
    for j in range(1,110):
        folder_name = "S"+str(j).zfill(3)
        current_path = os.path.join("subjects",folder_name)
        if not os.path.isdir(current_path):
            os.makedirs(current_path)
            print(current_path,"is created")
        for i in range(1,15):
            file_name = folder_name+"R"+str(i).zfill(2)+file_end
            res = requests.get(download_root+"/"+folder_name+file_name)
            with open("./subjects/"+folder_name+"/"+file_name,'wb') as w:
                w.write(res.content)
        print("Subject:",j,"data is downloaded")
