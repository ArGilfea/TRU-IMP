import os
import numpy as np
import matplotlib.pyplot as plt
import pydicom #To read Dicom Files
import time #To monitor time to run program
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Segmentations(segmentation_type:str='all',Image: DicomImage = None,seed=[[]],k=-1,subimage=[-1],threshold = -1,sigma_Canny=5,
                            combinationCanny = 2, methodCanny = "Taxicab",sigma_threshold=5,
                            alpha=1e1,max_iter_ICM=100,max_iter_kmean_ICM=100,max_iter_Fill=300,factor_Fill=[0.1,2.8],steps_Fill = 1000,growth=-1,min_f_growth=0,
                            name_segmentation = '',path_in='',name_in='',path_out = '',name_out='',show_pre=False,save=True,do_coefficients=True,
                            SaveSegm = True,do_moments=True,do_stats=True,verbose=False):
    '''
    Keyword arguments:\n
    segmentation_type -- type of segmentation to run (default all)\n
    Image -- an instance of DicomImage if it is already loaded (default none)\n
    seed - seed used for the filling segmentation (default [[]])\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes) (default -1)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    threshold -- used to resegment the segmentation. Must be between 0 and 1 to be considered (default -1)\n
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    sigma_threshold -- used for the thresholding (default 5)\n
    alpha -- used for the ICM segmentation (default 1e1)\n
    max_iter_ICM -- used for the ICM segmentation (default 100)\n
    max_iter_Fill -- used for the filling segmentation (default 300)\n
    factor_Fill -- factor used for the filling algorithm (default [0.1,2.8])\n
    steps_Fill -- steps for the filling algorithm (default 1000)\n
    growth -- growth factor for the filling algorithm(default -1)\n
    min_f_growth -- minimal index of f for the growth factor in the filling algorithm(default 0)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    path_in -- path from where to get the image, as a DicomImage class (default '')\n    
    name_in -- name of the DicomImage opened (default '')\n
    path_out -- path to save the result, as long as save is True (default '')\n    
    name_out -- name of the new DicomImage saved (if save is set to True).
            That name will be appended to name_in (default '')\n
    show_pre -- show the subimage and the seed if set to True, before the long computations (default False)\n
    do_coefficients -- compute all Jaccard and Dice coefficients (default True)\n
    save -- save the final result as a new instance of a DicomImage class (default True)\n
    SaveSegm -- save segmentations in the DicomImage instance(default True)\n
    do_moments -- do and save the moments in the DicomImage instance(default True)\n
    do_stats -- do and save the stats in the DicomImage instance(default True)\n
    verbose -- describes where the process presently is (default False)\n
    '''
    initial = time.time()
    try: 
        a = Image.version
        del a
    except:
        if path_in == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if name_in == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if name_out == '':
            raise Exception("path_in must be specified.\\It is recommended that the path be absolute")
        if path_out == '':
            path_out = path_in
        Image = PF.pickle_open(path_in+name_in+'.pkl')
    if k == -1:
        k = np.arange(Image.nb_acq)
    else:
        k = np.array(k)
    print(k)
    if show_pre:
        print("Showing seed positionning")
        Image.show_point(seed,star=True)
        Image.show_point(seed,star=True,log=True)
        Image.show_curves(seed)
        print("Showing sub regions")
        Image.show_point(seed,star=True,sub_im=subimage)
        plt.show()

    if segmentation_type == 'Canny' or segmentation_type == 'Canny Filled' or segmentation_type == 'all':
        print('Running the gradient segmentations...')
        Canny_Batch(Image=Image,k=k,subimage=subimage,sigma_Canny=sigma_Canny,combinationCanny=combinationCanny,methodCanny=methodCanny,
                            name_segmentation=name_segmentation)
    if segmentation_type == 'ICM' or segmentation_type == 'all':
        print('Running the statistics segmentations...')
        ICM_Batch(Image,k,subimage=subimage,alpha=alpha,max_iter_ICM=max_iter_ICM,max_iter_kmean_ICM=max_iter_kmean_ICM,
                    name_segmentation = name_segmentation,save=SaveSegm,do_moments=do_moments,do_stats=do_stats,verbose=verbose)
    if segmentation_type == 'Filling' or segmentation_type == 'all':
        print('Running the filling segmentations...')
        Filling_Batch(Image,k,seed=seed,subimage=subimage,max_iter_Fill=max_iter_Fill,
                        factor_Fill=factor_Fill,steps_Fill = steps_Fill,growth=growth,min_f_growth=min_f_growth,name_segmentation=name_segmentation)

    if threshold > 0 and threshold < 1:
        print('Doing the thresholding...')
        inter = time.time()
        for i in range(k.shape[0]):
            Image.VOI_threshold(acq=k[i],key=i,sigma=sigma_threshold,threshold=threshold,
            name=f"{Image.voi_name[i]}, thresh = {threshold}",do_moments=True,do_stats=True)
            print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - inter):.1f} s, for a total of {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

    if do_coefficients:
        Image.Dice_all()
        Image.Jaccard_all()

    if save:
        PF.pickle_save(Image,path_out+name_in+name_out+'.pkl')
    print(f"All the segmentations were done in {(time.time() - initial):.2f} s.")

def Canny_Batch(Image:DicomImage,k,subimage=[-1],sigma_Canny=5,combinationCanny=2,methodCanny="Taxicab",name_segmentation = ''):
    """
    Runs Canny Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    Image -- Image on which to segment\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_Canny_filled(subinfo = subimage,acq=k[i],sigma=sigma_Canny,combination=combinationCanny,method=methodCanny,
                                name=f"{name_segmentation} Canny Filled acq {k[i]}",do_moments=True,do_stats=True)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def ICM_Batch(Image,k,subimage=[-1],alpha=1e1,max_iter_ICM=100,max_iter_kmean_ICM=100,name_segmentation = '',save=True,do_moments=True,
                    do_stats=True,verbose=False):
    '''
    Runs ICM Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    alpha -- used for the ICM segmentation (default 1e1)\n
    max_iter_ICM -- used for the ICM segmentation (default 100)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    '''
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_ICM(subinfo = subimage,alpha=alpha,max_iter=max_iter_ICM,max_iter_kmean=max_iter_kmean_ICM,
                            acq=k[i],name=f"{name_segmentation} ICM acq {k[i]}",
                            do_moments=do_moments,do_stats=do_stats,verbose = verbose,save=save)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def Filling_Batch(Image,k,seed=[[]],subimage=[-1],max_iter_Fill=300,factor_Fill=[0.1,2.8],steps_Fill = 1000,
                    growth=-1,min_f_growth=0,name_segmentation = ''):
    '''
    Runs Filling Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    segmentation_type -- type of segmentation to run (default all)\n
    seed - seed used for the filling segmentation (default [[]])\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes) (default -1)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    threshold -- used to resegment the segmentation. Must be between 0 and 1 to be considered (default -1)\n
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    sigma_threshold -- used for the thresholding (default 5)\n
    alpha -- used for the ICM segmentation (default 1e1)\n
    max_iter_ICM -- used for the ICM segmentation (default 100)\n
    max_iter_Fill -- used for the filling segmentation (default 300)\n
    factor_Fill -- factor used for the filling algorithm (default [0.1,2.8])\n
    steps_Fill -- steps for the filling algorithm (default 1000)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    path_in -- path from where to get the image, as a DicomImage class (default '')\n    
    name_in -- name of the DicomImage opened (default '')\n
    path_out -- path to save the result, as long as save is True (default '')\n    
    name_out -- name of the new DicomImage saved (if save is set to True).
            That name will be appended to name_in (default '')\n
    show_pre -- show the subimage and the seed if set to True, before the long computations (default False)\n
    save -- save the final result as a new instance of a DicomImage class (default True)\n
    '''
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_filled_f(seed=[seed[1:]],factor=factor_Fill,steps = steps_Fill,acq=k[i],sub_im=subimage,
                    max_iter=max_iter_Fill,verbose=False,verbose_graphs=True,max_number_save=1,
                    save_between=False,growth=growth,min_f_growth=min_f_growth,
                    name=f"{name_segmentation} Filled acq {k[i]}",do_moments=True,do_stats=True,break_after_f=True)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")
