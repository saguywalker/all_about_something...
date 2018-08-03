import requests
import os
from six.moves import urllib

download_root = 'https://www.physionet.org/pn4/eegmmidb/'
file_end = '.edf'

def create_folder(num):
    if not os.path.isdir("subjects"):
        os.makedirs("subjects")
    folder_name = "S"+str(num).zfill(3)
    current_path = os.path.join("subjects",folder_name)
    if not os.path.isdir(current_path):
        os.makedirs(current_path)
        print(current_path,"is created")
    return current_path,folder_name

def download_edf_data():
    for j in range(1,110):
        current_path,folder_name = create_folder(num=j)
        for i in range(1,15):
            file_name = folder_name+"R"+str(i).zfill(2)+file_end
            res = requests.get(download_root+"/"+folder_name+"/"+file_name)
            with open(current_path+"/"+file_name,'wb') as w:
                w.write(res.content)
        print("Subject:",j,"data is downloaded")

def download_edf_event():
    for j in range(1,110):
        current_path,folder_name = create_folder(num=j)
        for i in range(1,15):
            file_name = folder_name+"R"+str(i).zfill(2)+".edf.event"
            res = requests.get(download_root+"/"+folder_name+"/"+file_name)
            with open(current_path+"/"+file_name,'wb') as w:
                w.write(res.content)
        print("Subject:",j,",event is downloaded")

if __name__ == "__main__":
    download_edf_data()
