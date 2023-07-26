try:
    import os
except: 
    pass
import numpy as np
import pydicom #To read Dicom Files
import time #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
from MyFunctions.Pickle_Functions import pickle_save

def Extract_Images(path_in:str,name:str='',path_out:str='',verbose:bool = False,
                    verbose_precise:bool = False,time_scale:str = 'min',Dose_inj:float=0,mass:float=1,total_time:float=60.62,
                    rescale:bool=False,Description:str='',save:bool = True):
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

        if((dicom_file[0:4]=='PET_' or dicom_file.endswith('.dcm')) and dicom_file[0] != "."):
            try:
                ds = pydicom.dcmread(path_in+dicom_file)
                all_files_Im[i-counter] = ds.pixel_array
                all_files_Header.append(ds)
                IntNum[i-counter] = all_files_Header[i-counter].InstanceNumber
            except:
                print(f"Invalid Dicom File, no pixel array present in {dicom_file}")
                counter += 1
        else: #Decreases for each non-dicom file in the folder
            counter += 1
        if((i%1000 == 0 or i == number_of_files)and verbose):
            print("Time Elapsed: ", "{:.2f}".format(time.time()-initial1),'s; % done: ',"{:.1f}".format(i/number_of_files*100),' %')
    ###
    print(number_of_files)
    number_of_files -= counter
    print(counter)
    if verbose_precise:
        print('Number of Files',number_of_files)
    all_files_Im_ordered = np.zeros((number_of_files),dtype=object)
    if verbose:
        print('Ordering Files')
    initial2 = time.time()
    all_files_Header_ordered = all_files_Header.copy()
    print(max(IntNum),min(IntNum))
    for i in range(number_of_files):
        all_files_Im_ordered[int(IntNum[i] - min(IntNum))] = all_files_Im[i]
        all_files_Header_ordered[int(IntNum[i] - min(IntNum))] = all_files_Header[i]
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
    position = np.zeros((number_of_files,3))
    width = np.zeros((number_of_files))
    length = np.zeros((number_of_files))
    rescaleS = np.zeros((number_of_files))
    rescaleI = np.zeros((number_of_files))
    voxel_thickness = np.zeros((number_of_files))
    voxel_width = np.zeros((number_of_files))
    voxel_length = np.zeros((number_of_files))
    initial3 = time.time()
    for i in range(number_of_files):
        try:
            temps[i] = all_files_Header_ordered[i].FrameReferenceTime
        except:
            temps[i] = 1
        Instance[i] = all_files_Header_ordered[i].InstanceNumber
        position[i,:] = all_files_Header_ordered[i].ImagePositionPatient
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
    print(times)
    RescaleSlope=np.array(RescaleSlope)
    RescaleIntercept=np.array(RescaleIntercept)
    """times = (times - times[0])/times[-1]*total_time #In min.
    if time_scale == 'sec':
        times = times*60
    elif time_scale == 'hr':
        times = times/60
    elif time_scale == 'ms':
        times = times * 60000"""
    try:
        times = (times - times[0])/60000
        times += times[1]/2
        print(times)
    except: pass

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
    sliceAxis = position[:nb_slice,2]

    widthAxis = position[0,0] + vw * np.arange(Width)
    lengthAxis = position[0,1] + vl * np.arange(Length)
    try:
        unit = all_files_Header_ordered[0].Units
    except:
        unit = "None"
    try:
        radiopharmaceutical = all_files_Header_ordered[0].RadiopharmaceuticalInformationSequence[0].Radiopharmaceutical
    except:
        radiopharmaceutical = ""
    try:
        radionuclide = all_files_Header_ordered[0].RadiopharmaceuticalInformationSequence[0].RadionuclideCodeSequence[0].CodeMeaning
    except:
        radionuclide = ""
    try:
        dose = all_files_Header_ordered[0].RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose
    except:
        dose = 0
    try:
        weight = all_files_Header_ordered[0].PatientsWeight
    except:
        weight = 0
    ###
    if verbose:
        print('Creating the class instance')
        
    dicom = DicomImage(Im,time=times,name=name,rescaleSlope=RescaleSlope,
                        rescaleIntercept = RescaleIntercept,time_scale=time_scale,
                        voxel_thickness=vt,voxel_width=vw,voxel_length=vl,
                        units=unit, radionuclide = radionuclide, radiopharmaceutical = radiopharmaceutical, 
                        sliceAxis = sliceAxis, widthAxis=widthAxis, lengthAxis= lengthAxis,
                        mass=weight,dose=dose,flat_images = True,Description=Description)
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