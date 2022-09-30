import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Extract_Images_R as Extract_r
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt
###
os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

name_phantom=np.array(['Fantome_1_1min','Fantome_5_1min','Fantome_6_1min','Fantome_7_1min','Fantome_8_1min'])
name_type = np.array(['_C_k_all','_I_k_all','_F_k_all'])
name_comp = np.array(['_comp_1','_comp_2','_comp_3'])
name_rat = np.array(['S025','S026','S027','S028','S029'])
devices = np.array(['rat','phantom'])
seg_method = {'_C_k_all':'Canny',
            '_I_k_all':'ICM',
            '_F_k_all':'Filling'
    }

path_rat = '/Volumes/Backup_Stuff/Python/Data/S029.pkl'
path_phantom_ICM = '/Volumes/Backup_Stuff/Python/Data_Results/Fantome_6_1min/Fantome_6_1min_comp_2_I_k_all.pkl'
path_phantom_Canny = '/Volumes/Backup_Stuff/Python/Data_Results/Fantome_6_1min/Fantome_6_1min_comp_2_C_k_all.pkl'
path_phantom_Filling = '/Volumes/Backup_Stuff/Python/Data_Results/Fantome_6_1min/Fantome_6_1min_comp_2_F_k_all.pkl'

full_path_Out = '/Users/philippelaporte/Desktop/Results_tmp/'

print(full_path_Out)

Image_I = PF.pickle_open(path_phantom_ICM)
print(f"First opened after {(time.time()-initial):.1f} s.")
Image_C = PF.pickle_open(path_phantom_Canny)
print(f"Second opened after {(time.time()-initial):.1f} s.")
Image_F = PF.pickle_open(path_phantom_Filling)
print(f"Third opened after {(time.time()-initial):.1f} s.")
###
print("Getting Dice graphs")
fig1 = plt.figure()
x = np.arange(5,40)
plt.pcolormesh(x,x,Image_I.dice_all[5:40,5:40]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \nstatistics-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
fig1.savefig(f"{full_path_Out}/Dice_I.png")
plt.close()

fig1 = plt.figure()
x = np.arange(7,40)
plt.pcolormesh(x,x,Image_C.dice_all[7:40,7:40]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \ngradient-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
fig1.savefig(f"{full_path_Out}/Dice_C.png")
plt.close()

fig1,ax = plt.subplots()
x = np.array([35,37,38])
Dice = np.array([[Image_F.dice_all[38,38],Image_F.dice_all[38,37],Image_F.dice_all[38,35]],
                [Image_F.dice_all[37,38],Image_F.dice_all[37,37],Image_F.dice_all[37,35]],
                [Image_F.dice_all[35,38],Image_F.dice_all[35,37],Image_F.dice_all[35,35]]])
plt.pcolormesh(Dice);plt.colorbar()
plt.suptitle("Sørensen-Dice coefficients for a \nfilling-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
ax.xaxis.set(ticks=np.arange(0.5, x.shape[0]),ticklabels=x)
ax.yaxis.set(ticks=np.arange(0.5, x.shape[0]),ticklabels=x)
fig1.savefig(f"{full_path_Out}/Dice_F.png")
plt.close()
###
print("Getting TACs graphs")
fig1 = plt.figure()
Image_I.voi_statistics_avg = []
Image_I.voi_statistics_std = []
Image_I.linear_shifts_errors(keys=np.arange(5,40),verbose=True)
for i in range(len(Image_I.voi_statistics_avg)):
    plt.errorbar(Image_I.time+i*0.1,Image_I.voi_statistics_avg[i],Image_I.voi_statistics_std[i])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with errors for a statistics segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TACs_I_e.png")
plt.close()
print(f"First Done in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
fig1 = plt.figure()
Image_C.voi_statistics_avg = []
Image_C.voi_statistics_std = []
Image_C.linear_shifts_errors(keys=np.arange(7,40),verbose=True)
for i in range(len(Image_C.voi_statistics_avg)):
    plt.errorbar(Image_C.time+i*0.1,Image_C.voi_statistics_avg[i],Image_C.voi_statistics_std[i])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with errors for a gradient segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TACs_C_e.png")
plt.close()
print(f"Second Done in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
fig1 = plt.figure()
Image_F.voi_statistics_avg = []
Image_F.voi_statistics_std = []
Image_F.linear_shifts_errors(keys=np.array([34,37,38]),verbose=True)
for i in range(len(Image_F.voi_statistics_avg)):
    plt.errorbar(Image_F.time+i*0.1,Image_F.voi_statistics_avg[i],Image_F.voi_statistics_std[i])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with errors for a filling segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TACs_F_e.png")
plt.close()
###
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()