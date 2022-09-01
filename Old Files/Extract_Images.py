import os
import numpy as np
import matplotlib.pyplot as plt
import pydicom #To read Dicom Files
import time #To monitor time to run program
import pickle #To save the instance created
import ipyvolume as ipv #To visualize the volume
from MyFunctions.DicomImage import DicomImage #Custom Class
from MyFunctions.pickle_functions import pickle_save
os.system('clear')
#print("Trying to read a single DICOM file...")
path = '/Volumes/Backup Stuff/These/Données CUSM/S028/PET_En_Ordre/'
single_file = 'PET_3069_179600_-145'
#os.system('cd '+path+';ls')

#ds = pydicom.dcmread(path+single_file)
#print(ds)
#print('\n',ds['ImageIndex'],'\n',ds[0x0054,0x1330],'\n',ds.ImageIndex,ds['ImageIndex'].VM)
#print(ds.pixel_array.shape)
#plt.imshow(ds.pixel_array)
print("Reading all DICOM files...")
print('Opening all files one by one and storing the data in an array')
number_of_files = len(os.listdir(path))
all_files_Im = np.zeros((number_of_files),dtype=object)
all_files_Im_ordered = np.zeros((number_of_files),dtype=object)
all_files_Header = []
all_files_Header_ordered = []
IntNum = np.zeros((number_of_files))
###
initial1 = time.time()
for i,dicom_file in enumerate(os.listdir(path),start=0):
    if(dicom_file[0:4]=='PET_'):
        ds = pydicom.dcmread(path+dicom_file)
        all_files_Im[i] = ds.pixel_array
        all_files_Header.append(ds)
        IntNum[i] = all_files_Header[i].InstanceNumber
    if(i%1000 == 0 or i == number_of_files):
        print("Time Elapsed: ", "{:.2f}".format(time.time()-initial1),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
###
print('Ordering Files')
initial2 = time.time()
all_files_Header_ordered = all_files_Header.copy()
for i in range(number_of_files):
    all_files_Im_ordered[int(IntNum[i]-1)] = all_files_Im[i]
    all_files_Header_ordered[int(IntNum[i]-1)] = all_files_Header[i]
    if(i%1000 == 0 or i == number_of_files - 1):
        print("Time Elapsed: ", "{:.2f}".format(time.time()-initial2),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
###
print("Extracting times and positions")
temps = np.zeros((number_of_files))
Instance = np.zeros((number_of_files))
position = np.zeros((number_of_files))
width = np.zeros((number_of_files))
length = np.zeros((number_of_files))
rescaleS = np.zeros((number_of_files))
rescaleI = np.zeros((number_of_files))
initial3 = time.time()
for i in range(number_of_files):
    temps[i] = all_files_Header_ordered[i].FrameReferenceTime
    Instance[i] = all_files_Header_ordered[i].InstanceNumber
    position[i] = all_files_Header_ordered[i].ImagePositionPatient[2]
    width[i] = all_files_Header_ordered[i].Rows
    length[i] = all_files_Header_ordered[i].Columns
    rescaleS[i] = all_files_Header_ordered[i].RescaleSlope
    rescaleI[i] = all_files_Header_ordered[i].RescaleIntercept
    if(i%1000 == 0 or i == number_of_files - 1):
        pass
        #print("Time Elapsed: ", "{:.2f}".format(time.time()-initial3),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
###
print("Extraction of temporal acquisition number")
nb_acq = 1
times = [temps[0]]
RescaleSlope = [rescaleS[0]]
RescaleIntercept = [rescaleI[0]]
for i in range(1,number_of_files):
    if temps[i] != temps[i-1]:
        nb_acq += 1
        times.append(temps[i])
    if rescaleS[i] != rescaleS[i-1]:
        RescaleSlope.append(rescaleS[i])
        RescaleIntercept.append(rescaleI[i])

nb_slice = 1
for i in range(1,number_of_files):
    if(temps[i] == temps[0]):
        nb_slice += 1

if (nb_slice != number_of_files/nb_acq):
    print('Error in the number of slice')

if (np.max(width) != np.min(width) and np.max(length) != np.min(length)):
    print('Error in the width and/or length of the images!')
    exit()
else:
    Width = int(np.max(width))
    Length = int(np.max(length))
###
print('Creating the 4d array')
Im = np.zeros((nb_acq,nb_slice,Width,Length))
print(Im.shape)
for i in range(nb_acq):
    for j in range(nb_slice):
        Im[i,j,:,:] = all_files_Im_ordered[int(i*nb_slice+j)]
###

###
print('Creating the class instance')
dicom = DicomImage(Im,name='S028')
###

###
print('Saving Data')
initial4 = time.time()
pickle_save(dicom, os.path.dirname(os.path.realpath(__file__))+'/S028.pkl')
print('Saving took ',"{:.2f}".format(time.time()-initial4),' s')
###-----------------Termination-Statement-------------###
print('Total Run Time: ',"{:.2f}".format(time.time()-initial1),' s')
print("Program ran until the end without a major problem")