import numpy as np
import matplotlib.pyplot as plt
import time

from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF

def Batch_Segmentations(segmentation_type:str='None',Image: DicomImage = None,seed=[[]],k=-1,subimage=[-1],threshold = -1,sigma_Canny=5,
                            combinationCanny = 2, combinationCannyPost = 3,methodCanny = "TaxiCab",CannyThreshLow:float = 0.1,CannyThreshHigh:float = 0.2,
                            sigma_threshold=5,threshold_fill=0.99,
                            centerEllipsoid = np.array([2,2,2]),axesEllipsoid = np.array([1,1,1]),
                            alpha=1e1,max_iter_ICM=100,max_iter_kmean_ICM=100,max_iter_Fill=300,factor_fill = 1,
                            factor_Fill_range=[0.1,2.8],steps_Fill = 1000,growth=-1,min_f_growth=0,
                            name_segmentation = '',path_in='',name_in='',path_out = '',name_out='',show_pre=False,save=True,do_coefficients=True,
                            SaveSegm = True,do_moments=True,do_stats=True,do_Thresh = False,verbose=False,verbose_graph_fill = False):
    '''
    Keyword arguments:\n
    segmentation_type -- type of segmentation to run (default all)\n
    Image -- an instance of DicomImage if it is already loaded (default none)\n
    seed - seed used for the filling segmentation (default [[]])\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes) (default -1)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    threshold -- used to resegment the segmentation. Must be between 0 and 1 to be considered (default -1)\n
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    combinationCanny -- used for the Canny segmentation (default 2)\n
    combinationCannyPost -- used for the Canny fill segmentation (default 3)\n
    CannyThreshLow -- lower threshold for the histeresis in the Canny algorithm (default 0.1)\n
    CannyThreshHigh -- upper threshold for the histeresis in the Canny algorithm (default 0.2)\n
    sigma_threshold -- used for the thresholding (default 5)\n
    alpha -- used for the ICM segmentation (default 1e1)\n
    max_iter_ICM -- used for the ICM segmentation (default 100)\n
    max_iter_Fill -- used for the filling segmentation (default 300)\n
    factor_Fill_range -- factor used for the filling algorithm (default [0.1,2.8])\n
    factor_Fill -- factor used for the filling algorithm (default 1)\n
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
        Canny_Fill_Batch(Image=Image,k=k,subimage=subimage,sigma_Canny=sigma_Canny,combinationCanny=combinationCanny,
                            combinationCannyPost=combinationCannyPost,methodCanny=methodCanny,
                            CannyThreshLow = CannyThreshLow,CannyThreshHigh = CannyThreshHigh,
                            name_segmentation=name_segmentation,do_moments=do_moments,do_Stats=do_stats,
                            SaveSegm=SaveSegm)
    if segmentation_type == 'ICM' or segmentation_type == 'all':
        print('Running the statistics segmentations...')
        ICM_Batch(Image,k,subimage=subimage,alpha=alpha,max_iter_ICM=max_iter_ICM,max_iter_kmean_ICM=max_iter_kmean_ICM,
                    name_segmentation = name_segmentation,save=SaveSegm,do_moments=do_moments,do_stats=do_stats,verbose=verbose)
    if segmentation_type in ['Filling','Filling f (very slow)','all']:
        print('Running the filling segmentations...')
        Filling_Batch_f(Image,k,seed=seed,subimage=subimage,max_iter_Fill=max_iter_Fill,
                        threshold_fill=threshold_fill,
                        factor_Fill=factor_Fill_range,steps_Fill = steps_Fill,
                        growth=growth,min_f_growth=min_f_growth,
                        name_segmentation=name_segmentation,SaveSegm=SaveSegm,
                        verbose_graph_fill = verbose_graph_fill,
                        do_moments=do_moments,do_stats=do_stats)

    if segmentation_type in ['Canny Contour']:
        print('Running the gradient contour...')
        Canny_Contour_Batch(Image,k,subImage=subimage,combinationCanny=combinationCanny,
                            CannyThreshLow = CannyThreshLow,CannyThreshHigh = CannyThreshHigh,
                            sigma_Canny=sigma_Canny,name_segmentation=name_segmentation,
                            SaveSegm=SaveSegm)
    if segmentation_type == "Ellipsoid":
        print('Running the ellipsoid segmentation...')
        Image.add_VOI_ellipsoid(center=centerEllipsoid,axes=axesEllipsoid,name=name_segmentation,do_moments=do_moments,do_stats=do_stats,save=SaveSegm)
    if segmentation_type == "k Mean":
        print('Running the k Mean segmentations...')
        kMean_Batch(Image,k,subimage=subimage,max_iter_kmean=max_iter_kmean_ICM,saveSegm=SaveSegm,name_segmentation=name_segmentation,
                        do_moments=do_moments,do_stats=do_stats,verbose=verbose)
    if segmentation_type == "Filling (very slow)":
        print('Running the filling segmentations...')
        Filling_Batch(Image,k=k,seed=seed,subimage=subimage,factor=factor_fill,max_iter_f=max_iter_Fill,
                            name_segmentation=name_segmentation,SaveSegm=SaveSegm,do_moments=do_moments,
                            do_stats=do_stats,verbose=verbose)
    if threshold > 0 and threshold < 1 and do_Thresh:
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

def Canny_Contour_Batch(Image:DicomImage,k,subImage:list=[-1],combinationCanny:int=2,
                        sigma_Canny:float=5,CannyThreshLow:float = 0.1,CannyThreshHigh:float = 0.2,
                        name_segmentation:str='',SaveSegm:bool=True,
                        do_moments:bool=True,do_Stats:bool=True):
    """
    Runs Canny Contour Segmentations on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny Contour segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.    
    Keyword arguments:\n
    Image -- Image on which to segment\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    combinationCanny -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    CannyThreshLow -- lower threshold for the histeresis in the Canny algorithm (default 0.1)\n
    CannyThreshHigh -- upper threshold for the histeresis in the Canny algorithm (default 0.2)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    do_moments -- compute the moments of the resulting segmentations (default True)\n
    do_stats -- compute the mean and std of the segmentations (default True)\n
    SaveSegm -- save the segmentations in the DicomImage class (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_canny(subinfo=subImage,acq=k[i],combination=combinationCanny,sigma=sigma_Canny,
                        threshLow=CannyThreshLow,threshHigh=CannyThreshHigh,
                        name=f"{name_segmentation} Canny Contour {k[i]}",
                        do_moments=do_moments,save=SaveSegm,do_stats=do_Stats)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def Canny_Fill_Batch(Image:DicomImage,k,subimage:list=[-1],sigma_Canny:float=5,combinationCanny:int=2,
                    combinationCannyPost:int = 3,
                    CannyThreshLow:float = 0.1,CannyThreshHigh:float = 0.2,
                    methodCanny:str="TaxiCab",name_segmentation:str = '',SaveSegm:bool=True,
                    do_moments:bool=True,do_Stats:bool=True):
    """
    Runs Canny Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    Image -- Image on which to segment\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    sigma_Canny -- used for the Canny segmentation (default 5)\n
    combinationCanny -- combination parameter for the number of necessary 2D Canny on a given voxel to make that voxel part of the 
    VOI (default 2)\n
    combinationPost -- combination parameter for the number of necessary 2D filling on a given voxel to make that voxel part of the 
    VOI (default 3)\n
    CannyThreshLow -- lower threshold for the histeresis in the Canny algorithm (default 0.1)\n
    CannyThreshHigh -- upper threshold for the histeresis in the Canny algorithm (default 0.2)\n
    methodCanny -- method to compute the distance between two voxels (default 'TaxiCab')\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    do_moments -- compute the moments of the resulting segmentations (default True)\n
    do_stats -- compute the mean and std of the segmentations (default True)\n
    verbose -- gives the progress of the process (default False)\n
    SaveSegm -- save the segmentations in the DicomImage class (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_Canny_filled(subinfo = subimage,acq=k[i],sigma=sigma_Canny,combination=combinationCanny,
                                combinationPost=combinationCannyPost,
                                threshLow=CannyThreshLow,threshHigh=CannyThreshHigh,
                                method=methodCanny,save=SaveSegm,
                                name=f"{name_segmentation} Canny Filled acq {k[i]}",
                                do_moments=do_moments,do_stats=do_Stats)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def ICM_Batch(Image,k,subimage:list=[-1],alpha:float=1e1,max_iter_ICM:int=100,max_iter_kmean_ICM:int=100,name_segmentation:str = '',save:bool=True,do_moments:bool=True,
                    do_stats:bool=True,verbose:bool=False):
    '''
    Runs ICM Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    Image -- DicomImage class to run the segmentations\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    alpha -- used for the ICM segmentation (default 1e1)\n
    max_iter_ICM -- used for the ICM segmentation (default 100)\n
    max_iter_kmean_ICM -- used for the kMean in the ICM (default 100)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    do_moments -- compute the moments of the resulting segmentations (default True)\n
    do_stats -- compute the mean and std of the segmentations (default True)\n
    verbose -- gives the progress of the process (default False)\n
    SaveSegm -- save the segmentations in the DicomImage class (default True)\n
    '''
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_ICM(subinfo = subimage,alpha=alpha,max_iter=max_iter_ICM,max_iter_kmean=max_iter_kmean_ICM,
                            acq=k[i],name=f"{name_segmentation} ICM acq {k[i]}",
                            do_moments=do_moments,do_stats=do_stats,verbose = verbose,save=save)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def kMean_Batch(Image:DicomImage,k:np.ndarray,subimage:np.ndarray=[-1],max_iter_kmean:int=100,saveSegm:bool = True, name_segmentation:str = '', do_moments:bool=True,
                    do_stats:bool=True, verbose:bool=False):
    """
    Image -- DicomImage class to run the segmentations\n
    do_moments -- compute the moments of the resulting segmentations (default True)\n
    do_stats -- compute the mean and std of the segmentations (default True)\n
    verbose -- gives the progress of the process (default False)\n
    SaveSegm -- save the segmentations in the DicomImage class (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_kMean(acq = k[i],subinfo=subimage,max_iter=max_iter_kmean,
                        save=saveSegm,do_moments=do_moments,do_stats=do_stats,
                        verbose=verbose,name=f"{name_segmentation} kMean acq {k[i]}")
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def Filling_Batch_f(Image:DicomImage,k,seed:list=[[]],subimage:list=[-1],max_iter_Fill:int=300,factor_Fill:list=[0.1,2.8],steps_Fill:int = 1000,
                    threshold_fill:float = 0.99,growth:float=-1,min_f_growth:float=0,name_segmentation:str = '',verbose_graph_fill:bool=False,
                    SaveSegm:bool=True,do_moments:bool=True,do_stats:bool=True):
    '''
    Runs Filling Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    Image -- DicomImage class to run the segmentations\n
    segmentation_type -- type of segmentation to run (default all)\n
    seed - seed used for the filling segmentation (default [[]])\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes) (default -1)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
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
        Image.VOI_filled_f(seed=seed,factor=factor_Fill,steps = steps_Fill,acq=k[i],sub_im=subimage,
                    max_iter=max_iter_Fill,verbose=False,verbose_graphs=verbose_graph_fill,max_number_save=1,
                    save_between=False,growth=growth,min_f_growth=min_f_growth,threshold=threshold_fill,
                    name=f"{name_segmentation} Filled f acq {k[i]}",do_moments=do_moments,do_stats=do_stats,break_after_f=True,
                    numba=False)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")

def Filling_Batch(Image:DicomImage,k:np.ndarray,seed:list=[[]],subimage:list = [-1],factor:float=1,
                    max_iter_f:int = 100, 
                    name_segmentation:str = '',
                    SaveSegm:bool=True,do_moments:bool=True,do_stats:bool=True,verbose:bool=False):
    """
    Runs Filling Segmentation on many timeframes. Useful to run everything in a single command.\n
    The parameters passed for each Canny segmentation will be the same, only the timeframe of interest will vary, according to the
    array k.
    Keyword arguments:\n
    Image -- DicomImage class to run the segmentations\n
    seed - seed used for the filling segmentation (default [[]])\n
    k -- timeframes on which to base the static segmentations (must be an array or -1 for all timeframes) (default -1)\n
    subimage -- smaller region upon which to do the segmentations (default [-1], i.e. the whole image will be considered)\n
    max_iter_f -- used for the filling segmentation (default 100)\n
    factor -- factor used for the filling algorithm (default 1)\n
    name_segmentation -- used to name all the segmentations saved (default '')\n
    do_moments -- compute the moments of the resulting segmentations (default True)\n
    do_stats -- compute the mean and std of the segmentations (default True)\n
    verbose -- gives the progress of the process (default False)\n
    SaveSegm -- save the segmentations in the DicomImage class (default True)\n
    """
    initial = time.time()
    for i in range(k.shape[0]):
        Image.VOI_filled(seed=seed,sub_im=subimage,factor=factor,acq=k[1],max_iter=max_iter_f,
                            name=f"{name_segmentation} Filled acq {k[i]}",do_moments=do_moments,do_stats=do_stats,break_after_f=True,
                            SaveSegm=SaveSegm,verbose=verbose)
        print(f"Part done: {(i+1)/k.shape[0]*100:.2f} % in {(time.time() - initial):.1f} s at {time.strftime('%H:%M:%S')}")