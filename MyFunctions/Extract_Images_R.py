try:
    import os
except: 
    pass
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.defchararray import count
import pydicom #To read Dicom Files
import time #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
from MyFunctions.Pickle_Functions import pickle_save

def Extract_Images(path_in,name='',path_out='',verbose = False,
                    verbose_precise = False,time_scale = 'min',Dose_inj=0,mass=1,
                    rescale=False,Description='',save=True):
    if verbose:
        print("Reading all DICOM files for "+name)
        print('Opening all files one by one and storing the data in an array')
    all_folders = os.listdir(path_in)
    number_folders = 0
    folders = []
    files_all = []
    number_files = []
    counter = 0
    for i in range(len(all_folders)):
        if all_folders[i][0:3]=='PET':
            number_folders+=1
            folders.append(all_folders[i])
            all_subfolders = os.listdir(path_in+all_folders[i]+'/')
            counter_sub = 0
            for j in range(len(all_subfolders)):
                if(all_subfolders[j].endswith('.dcm')):
                    files_all.append(path_in+all_folders[i]+'/'+all_subfolders[j])
                else:
                    counter_sub += 1
            number_files.append(len(os.listdir(path_in+all_folders[i]+'/'))-counter_sub)
            current_value = len(os.listdir(path_in+all_folders[i]+'/'))-counter_sub
            if number_files[0] != current_value:
                print('Problem in the number of files for folder: ',all_folders[i])
        else:
            counter += 1
            if verbose_precise:
                print('Invalid dir :',all_folders[i])
    if (number_folders * np.max(number_files) != len(files_all)) or (number_folders * np.min(number_files) != len(files_all)):
        print('Ending problem in the number of files: ',len(files_all),' vs ',number_folders * np.max(number_files) != len(files_all),' or ',number_folders * np.min(number_files) != len(files_all))
        exit()
    nb_slice_tmp = np.max(number_files)
    number_of_files = len(files_all)
    #print('Number of files: ',number_of_files)
    all_files_Im = np.zeros((number_of_files),dtype=object)
    all_files_Header = []
    all_files_Header_ordered = []
    IntNum = np.zeros((number_of_files))
    initial1 = time.time()
    for i in range(number_of_files):
        ds = pydicom.dcmread(files_all[i])
        all_files_Im[i] = ds.pixel_array
        all_files_Header.append(ds)
        IntNum[i] = all_files_Header[i].InstanceNumber
        if((i%1000 == 0 or i == number_of_files)and verbose):
            print("Time Elapsed: ", "{:.2f}".format(time.time()-initial1),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
    ###
    if verbose:
        print('Ordering Files')
    initial2 = time.time()

    #textfile = open(path_out+"/files_name.txt", "w")
    #for i in range(len(files_all)):
        #textfile.write(str(i)+str(files_all[i])+'\n')
    #textfile.close()

    order_idx = np.argsort(folders)

    #Ordering by times
    all_files_Header_ordered_tmp = all_files_Header.copy()
    all_files_Im_ordered_tmp = np.zeros((number_of_files),dtype=object)
    for i in range(number_folders):
        for j in range(nb_slice_tmp):
            all_files_Im_ordered_tmp[i*nb_slice_tmp+j] = all_files_Im[order_idx[i]*nb_slice_tmp+j]
            all_files_Header_ordered_tmp[i*nb_slice_tmp+j] = all_files_Header[order_idx[i]*nb_slice_tmp+j]
            if((i*nb_slice_tmp+j%1000 == 0 or i*nb_slice_tmp+j == number_of_files - 1)and verbose_precise):
                print("Time Elapsed: ", "{:.2f}".format(time.time()-initial2),'s; % done: ',"{:.1f}".format((i*nb_slice_tmp+j)/number_of_files*100),' %')
    ###
    #textfile = open(path_out+"/files_time_ordered1.txt", "w")
    #for i in range(len(files_all)):
        #textfile.write(str(all_files_Header_ordered_tmp[i].InstanceNumber)+'   '+str(all_files_Header_ordered_tmp[i].FrameReferenceTime)+'\n')
    #textfile.close()
    #Ordering by slices
    all_files_Header_ordered = all_files_Header.copy()
    all_files_Im_ordered = np.zeros((number_of_files),dtype=object)
    for i in range(number_folders):
        for j in range(nb_slice_tmp):
            all_files_Header_ordered[i*nb_slice_tmp+int(all_files_Header_ordered_tmp[i*nb_slice_tmp+j].InstanceNumber-1)] = all_files_Header_ordered_tmp[i*nb_slice_tmp+j]
            all_files_Im_ordered[i*nb_slice_tmp+int(all_files_Header_ordered_tmp[i*nb_slice_tmp+j].InstanceNumber-1)] = all_files_Im_ordered_tmp[i*nb_slice_tmp+j]
            if((i*nb_slice_tmp+j%1000 == 0 or i*nb_slice_tmp+j == number_of_files - 1)and verbose_precise):
                print("Time Elapsed: ", "{:.2f}".format(time.time()-initial2),'s; % done: ',"{:.1f}".format((i*nb_slice_tmp+j)/number_of_files*100),' %')

    #textfile = open(path_out+"/files_time_ordered2.txt", "w")
    #for i in range(len(files_all)):
        #textfile.write(str(all_files_Header_ordered[i].InstanceNumber)+'   '+str(all_files_Header_ordered[i].FrameReferenceTime)+'\n')
    #textfile.close()
    ###
    if verbose:
        print("Extracting times and positions")
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
        try:
            temps[i] = all_files_Header_ordered[i].FrameReferenceTime
        except:
            temps[i] = 1
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
        if temps[i] not in times:
            nb_acq += 1
            times.append(temps[i])
            RescaleSlope.append(rescaleS[i])
            RescaleIntercept.append(rescaleI[i])            
    times=np.array(times)
    RescaleSlope=np.array(RescaleSlope)
    RescaleIntercept=np.array(RescaleIntercept)
    times = (times - times[0])/(times[1]-times[0]) #In min.
    if time_scale == 'sec':
        times = times*60
    elif time_scale == 'hr':
        times = times/60
    elif time_scale == 'ms':
        times = times * 60000

    nb_slice = 1
    #print(len(times))
    #print(sorted(times))
    for i in range(1,number_of_files):
        if(temps[i] == temps[0]):
            nb_slice += 1

    if (nb_slice != number_of_files/nb_acq):
        print('Error in the number of slice: ',nb_slice,' vs ',number_of_files/nb_acq)
        exit()
        nb_slice = int(number_of_files/nb_acq)

    if (np.max(width) != np.min(width) and np.max(length) != np.min(length)):
        print('Error in the width and/or length of the images!')
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
            if rescale:
                Im[i,j,:,:] = Im[i,j,:,:] * RescaleSlope[i] + RescaleIntercept[i]
    ###
    if np.max(voxel_thickness) == np.min(voxel_thickness):
        vt = voxel_thickness[0]
    else:
        vt = 0
    if np.max(voxel_width) == np.min(voxel_width):
        vw = voxel_width[0]
    else:
        vw = 0
    if np.max(voxel_length) == np.min(voxel_length):
        vl = voxel_length[0]
    else:
        vl = 0

    try:
        unit = all_files_Header_ordered[0].Units
    except:
        unit = "None"

    ###
    if verbose:
        print('Creating the class instance')
    dicom = DicomImage(Im,time=times,name=name,rescaleSlope=RescaleSlope,
                        rescaleIntercept = RescaleIntercept,time_scale=time_scale,
                        voxel_thickness=vt,voxel_width=vw,voxel_length=vl,
                        units=unit,
                        mass=mass,Dose_inj=Dose_inj,flat_images=True,Description=Description)
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