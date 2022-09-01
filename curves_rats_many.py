import numpy as np
import os
import matplotlib.pyplot as plt

import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt

os.system('clear')
print('Starting program...')
path ='/Volumes/Backup_Stuff/Python/Data_Results/'

extension = '_CIF_k_all.pkl'

path_result = '/Volumes/Backup_Stuff/Python/Results/'
initial = time.time()
rats = 5
all_rats_Dice = np.zeros(rats,dtype=object)
all_rats_Jaccard = np.zeros(rats,dtype=object)
rat = PF.pickle_open(path+'S025'+extension);print(f"Opened the first file after {time.time()-initial:.2f} s")
all_rats_Dice[0] = rat.dice_all
all_rats_Jaccard[0] = rat.jaccard_all
del rat
rat = PF.pickle_open(path+'S026'+extension);print(f"Opened the second file after {time.time()-initial:.2f} s")
all_rats_Dice[1] = rat.dice_all
all_rats_Jaccard[1] = rat.jaccard_all
del rat
rat = PF.pickle_open(path+'S027'+extension);print(f"Opened the third file after {time.time()-initial:.2f} s")
all_rats_Dice[2] = rat.dice_all
all_rats_Jaccard[2] = rat.jaccard_all
del rat
rat = PF.pickle_open(path+'S028'+extension);print(f"Opened the fourth file after {time.time()-initial:.2f} s")
all_rats_Dice[3] = rat.dice_all
all_rats_Jaccard[3] = rat.jaccard_all
del rat
rat = PF.pickle_open(path+'S029'+extension);print(f"Opened the fifth file after {time.time()-initial:.2f} s")
all_rats_Dice[4] = rat.dice_all
all_rats_Jaccard[4] = rat.jaccard_all
del rat

rats_name=np.array(['S025','S026','S027','S028','S029'])
types_name = np.array(['Gradient','Statistics','Filling','Gradient Threshold','Statistics Threshold','Filling Threshold'])
each = 26

timeframes = np.arange(26)

Canny = 0
ICM = each
Fill = 2*each
Canny_thresh = 3*each
ICM_thresh = 4*each
Fill_thresh = 5*each

GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= Canny,name1="Dice Coefficients for Gradient Segmentation for all rats"
                        ,path_out=path_result,name_out='Dice_Canny_all_Rats')
GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= ICM,name1="Dice Coefficients for Statistics Segmentation for all rats"
                        ,path_out=path_result,name_out='Dice_ICM_all_Rats')
GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= Fill,name1="Dice Coefficients for Filling Segmentation for all rats"
                        ,path_out=path_result,name_out='Dice_Filling_all_Rats')

GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= Canny_thresh,name1="Dice Coefficients for Gradient Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Dice_Canny_thresh_all_Rats')
GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= ICM_thresh,name1="Dice Coefficients for Statistics Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Dice_ICM_thresh_all_Rats')
GM.graph_all_specimens(all_rats_Dice,rats_name,rats,timeframes,begin= Fill_thresh,name1="Dice Coefficients for Filling Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Dice_Filling_thresh_all_Rats')

GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= Canny,name1="Jaccard Coefficients for Gradient Segmentation for all rats"
                        ,path_out=path_result,name_out='Jaccard_Canny_all_Rats')
GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= ICM,name1="Jaccard Coefficients for Statistics Segmentation for all rats"
                        ,path_out=path_result,name_out='Jaccard_ICM_all_Rats')
GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= Fill,name1="Jaccard Coefficients for Filling Segmentation for all rats"
                        ,path_out=path_result,name_out='Jaccard_Filling_all_Rats')

GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= Canny_thresh,name1="Jaccard Coefficients for Gradient Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Jaccard_Canny_thresh_all_Rats')
GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= ICM_thresh,name1="Jaccard Coefficients for Statistics Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Jaccard_ICM_thresh_all_Rats')
GM.graph_all_specimens(all_rats_Jaccard,rats_name,rats,timeframes,begin= Fill_thresh,name1="Jaccard Coefficients for Filling Segmentation with threshold for all rats"
                        ,path_out=path_result,name_out='Jaccard_Filling_thresh_all_Rats')

for i in range(rats_name.shape[0]):
    GM.graph_all_types(all_rats_Dice[i],rats_name[i],types_name,timeframes,path_out=path_result,name_out=f"{rats_name[i]}_all_Types_Dice")
    GM.graph_all_types(all_rats_Jaccard[i],rats_name[i],types_name,timeframes,path_out=path_result,name_out=f"{rats_name[i]}_all_Types_Jaccard")

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()