import numpy as np
import matplotlib.pyplot as plt
import pydicom
import os
import time

initial = time.time()
os.system('clear')
path_in = '/Users/philippelaporte/Desktop/École/Université/Ph D/Thèse/Fantôme/FantDyn5/'
path_out = '/Users/philippelaporte/Desktop/Programmation/Python/'
all_files_Header = []
folder = []
folders = os.listdir(path_in)

for i,root in enumerate(folders):
    if root[0:3]=='PET':
        first_file = os.listdir(path_in+root+'/')[0]
        ds = pydicom.dcmread(path_in+root+'/'+first_file)
        all_files_Header.append(ds)
        folder.append(root)
#all_files_Header.append(pydicom.dcmread())
order_idx = np.argsort(folder)
all_files_Header = np.array(all_files_Header)[order_idx]
folder = np.array(folder)[order_idx]
order_idx = np.argsort(folder)

Study_Time = np.zeros((len(all_files_Header)))
Series_Time = np.zeros(len(all_files_Header))
Acquisition_Time = np.zeros(len(all_files_Header))
Content_Time = np.zeros(len(all_files_Header))
Reference_Time = np.zeros((len(all_files_Header)))
instance = np.zeros((len(all_files_Header)))

for i in range(len(all_files_Header)):
    Study_Time[i] = all_files_Header[i].StudyTime
    Series_Time[i] = all_files_Header[i].SeriesTime
    Acquisition_Time[i] = all_files_Header[i].AcquisitionTime
    Content_Time[i] = all_files_Header[i].ContentTime
    Reference_Time[i] = all_files_Header[i].FrameReferenceTime
    instance[i] = all_files_Header[i].InstanceNumber

#textfile = open(path_out+"all_headers_fantome1.txt", "w")
#for element in all_files_Header:
#    textfile.write(str(element))
#textfile.close()

textfile = open(path_out+"first_header_fantome1.txt", "w")
textfile.write(str(all_files_Header[0]))
textfile.close()

#textfile = open(path_out+"all_headers_times_fantome1.txt", "w")
#for i in range(len(all_files_Header)):
#    textfile.write(str(i)+'\n')
#    textfile.write(str(folder[i])+'\n')
#    textfile.write(str(Study_Time[i])+'\n')
#    textfile.write(str(Series_Time[i])+'\n')
#    textfile.write(str(Acquisition_Time[i])+'\n')
#    textfile.write(str(Content_Time[i])+'\n')
#    textfile.write(str(instance[i])+'\n')
#    textfile.write(str(Reference_Time[i])+'\n\n')
#    times = (Reference_Time[i]-np.min(Reference_Time))/(Reference_Time[1]-np.min(Reference_Time))
#    textfile.write(str(times)+'\n\n')
#textfile.close()

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')

