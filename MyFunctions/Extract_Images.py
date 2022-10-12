import os
import numpy as np
import matplotlib.pyplot as plt
import pydicom #To read Dicom Files
import time #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
from MyFunctions.Pickle_Functions import pickle_save

def Extract_Images(path_in,name='',path_out='',verbose = False,
                    verbose_precise = False,time_scale = 'min',Dose_inj=0,mass=1,
                    rescale=False,Description='',save = True):
    if verbose:
        print("Reading all DICOM files for "+name)
        print('Opening all files one by one and storing the data in an array')
    number_of_files = len(os.listdir(path_in))
    all_files_Im = np.zeros((number_of_files),dtype=object)
    all_files_Header = []
    all_files_Header_ordered = []
    IntNum = np.zeros((number_of_files))
    initial1 = time.time()
    counter = 0
    for i,dicom_file in enumerate(os.listdir(path_in),start=0):
        if(dicom_file[0:4]=='PET_' or dicom_file.endswith('.dcm')):
            ds = pydicom.dcmread(path_in+dicom_file)
            all_files_Im[i-counter] = ds.pixel_array
            all_files_Header.append(ds)
            IntNum[i-counter] = all_files_Header[i-counter].InstanceNumber
        else: #Decreases for each non-dicom file in the folder
            counter += 1
        if((i%1000 == 0 or i == number_of_files)and verbose):
            print("Time Elapsed: ", "{:.2f}".format(time.time()-initial1),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
    ###
    number_of_files -= counter
    if verbose_precise:
        print('Number of Files',number_of_files)
    all_files_Im_ordered = np.zeros((number_of_files),dtype=object)
    if verbose:
        print('Ordering Files')
    initial2 = time.time()
    all_files_Header_ordered = all_files_Header.copy()
    for i in range(number_of_files):
        all_files_Im_ordered[int(IntNum[i]-1)] = all_files_Im[i]
        all_files_Header_ordered[int(IntNum[i]-1)] = all_files_Header[i]
        if((i%1000 == 0 or i == number_of_files - 1)and verbose_precise):
            print("Time Elapsed: ", "{:.2f}".format(time.time()-initial2),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
    ###
    ###
    if verbose:
        print("Extracting times and positions")
    if verbose_precise:
        print('Size of Image: ',all_files_Im_ordered.shape)
    temps = np.zeros((number_of_files))
    Instance = np.zeros((number_of_files))
    position = np.zeros((number_of_files))
    width = np.zeros((number_of_files))
    length = np.zeros((number_of_files))
    rescaleS = np.zeros((number_of_files))
    rescaleI = np.zeros((number_of_files))
    voxel_thickness = np.zeros((number_of_files))
    voxel_width = np.zeros((number_of_files))
    voxel_length = np.zeros((number_of_files))
    initial3 = time.time()
    for i in range(number_of_files):
        temps[i] = all_files_Header_ordered[i].FrameReferenceTime
        Instance[i] = all_files_Header_ordered[i].InstanceNumber
        position[i] = all_files_Header_ordered[i].ImagePositionPatient[2]
        width[i] = all_files_Header_ordered[i].Rows
        length[i] = all_files_Header_ordered[i].Columns
        rescaleS[i] = all_files_Header_ordered[i].RescaleSlope
        rescaleI[i] = all_files_Header_ordered[i].RescaleIntercept
        voxel_thickness[i] = all_files_Header_ordered[i].SliceThickness
        voxel_width[i] = all_files_Header_ordered[i].PixelSpacing[0]
        voxel_length[i] = all_files_Header_ordered[i].PixelSpacing[1]
        if((i%1000 == 0 or i == number_of_files - 1)and verbose_precise):
            print("Time Elapsed: ", "{:.2f}".format(time.time()-initial3),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
    ###
    if verbose:
        print("Extraction of temporal acquisition number")
    nb_acq = 1
    times = [temps[0]]
    RescaleSlope = [rescaleS[0]]
    RescaleIntercept = [rescaleI[0]]
    for i in range(1,number_of_files):
        if temps[i] != temps[i-1]:
            nb_acq += 1
            times.append(temps[i])
            RescaleSlope.append(rescaleS[i])
            RescaleIntercept.append(rescaleI[i])  
    if verbose_precise:
        print('Number of Acquisitions: ',nb_acq)
    times=np.array(times)
    RescaleSlope=np.array(RescaleSlope)
    RescaleIntercept=np.array(RescaleIntercept)
    times = (times - times[0])/times[-1]*60.62 #In min.
    if time_scale == 'sec':
        times = times*60
    elif time_scale == 'hr':
        times = times/60
    elif time_scale == 'ms':
        times = times * 60000

    nb_slice = 1
    for i in range(1,number_of_files):
        if(temps[i] == temps[0]):
            nb_slice += 1
    if verbose_precise:
        print('Number of Slices: ',nb_slice)
    if (nb_slice != number_of_files/nb_acq):
        print('Error in the number of slice')

    if ((np.max(width) != np.min(width) and np.min(width)!=0) and (np.max(length) != np.min(length) and np.min(length!=0))):
        print('Error in the width and/or length of the images!: ', np.max(width),np.min(width),np.max(length),np.min(length))
        exit()
    else:
        Width = int(np.max(width))
        Length = int(np.max(length))
    ###
    if verbose:
        print('Creating the 4d array')
    Im = np.zeros((nb_acq,nb_slice,Width,Length))
    for i in range(nb_acq):
        for j in range(nb_slice):
            Im[i,j,:,:] = all_files_Im_ordered[int(i*nb_slice+j)]
            #*RescaleSlope[i]
            if rescale:
                Im[i,j,:,:] = Im[i,j,:,:] * RescaleSlope[i] + RescaleIntercept[i]
    ###
    if np.max(voxel_thickness) == np.min(voxel_thickness):
        vt = voxel_thickness[0]
    if np.max(voxel_width) == np.min(voxel_width):
        vw = voxel_width[0]
    if np.max(voxel_length) == np.min(voxel_length):
        vl = voxel_length[0]

    ###
    if verbose:
        print('Creating the class instance')
    dicom = DicomImage(Im,time=times,name=name,rescaleSlope=RescaleSlope,
                        rescaleIntercept = RescaleIntercept,time_scale=time_scale,
                        voxel_thickness=vt,voxel_width=vw,voxel_length=vl,
                        units=all_files_Header_ordered[0].Units,
                        mass=mass,Dose_inj=Dose_inj,flat_images = True,Description=Description)
    ###

    ###
    if verbose:
        print('Saving Data')
    initial4 = time.time()
    if save == True:
        if len(path_in) == 0: #Sets the output directory to the running directory if there is no specification
            pickle_save(dicom, os.path.dirname(os.path.realpath(__file__))+'/'+name+'.pkl')
        else:
            pickle_save(dicom, path_out+'/'+name+'.pkl')
    if verbose:
        print('Saving took ',"{:.2f}".format(time.time()-initial4),' s')
    ###-----------------Termination-Statement-------------###
    if verbose:
        print('Run Time for this extraction: ',"{:.2f}".format(time.time()-initial1),' s')
    return dicom