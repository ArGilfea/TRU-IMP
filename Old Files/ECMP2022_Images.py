import numpy as np
import os
import matplotlib.pyplot as plt
import time
###
import MyFunctions.Batch_Segmentations as BS
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
####
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

full_path_Out = '/Users/philippelaporte/Desktop/Ecole/Université/Conférences/ECMP-2022'

print(full_path_Out)

Image_R = PF.pickle_open(path_rat)
################
#GIF phantom
print(f"Getting GIF of the rat in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
GIFs = np.zeros((Image_R.nb_acq,Image_R.coronal_flats.shape[1],Image_R.coronal_flats.shape[2],1))
for i in range(Image_R.nb_acq): 
    fig1 = plt.figure()
    GIFs[i,:,:,0] = (Image_R.coronal_flats[i,:,:])
    plt.pcolormesh(Image_R.coronal_flats[i,:,:])
    plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Rat at timeframe {i}")
    if i < 10:
        fig1.savefig(f"{full_path_Out}/Rat-Gif/Rat-Gif-{i}.png")
    else:
        fig1.savefig(f"{full_path_Out}/Rat-Gif/Rat-Gif-{i}.png")
    plt.close()
GIFs = GIFs/np.max(GIFs)*255
from moviepy.editor import ImageSequenceClip
clip = ImageSequenceClip(list(GIFs), fps=3)
clip.write_gif(f"{full_path_Out}/Rat_Gif.gif", fps=3)

#clip = ImageSequenceClip(f"{full_path_Out}/Rat-Gif/", fps=10)
#clip.write_gif(f"{full_path_Out}/Rat_Gif2.gif", fps=10)
################
print(f"Getting rat slices in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")

fig1 = plt.figure()
plt.pcolormesh(Image_R.coronal_flats[15,:,:])
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Rat at timeframe {i}")
fig1.savefig(f"{full_path_Out}/Rat_Coro_Flat.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(Image_R.sagittal_flats[15,:,:])
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Sagittal View of a Rat at timeframe {i}")
fig1.savefig(f"{full_path_Out}/Rat_Sag_Flat.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(Image_R.axial_flats[15,:,:])
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Axial View of a Rat at timeframe {i}")
fig1.savefig(f"{full_path_Out}/Rat_Ax_Flat.png")
plt.close()
#################

del Image_R
#################
Image_I = PF.pickle_open(path_phantom_ICM)
Image_C = PF.pickle_open(path_phantom_Canny)
Image_F = PF.pickle_open(path_phantom_Filling)

#################
print(f"Getting bad segmentations of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
for i in range(3):
    fig1 = plt.figure()
    plt.pcolormesh(np.sum(Image_F.voi[f"{30+i}"][:,:,:],axis=0))
    plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Phantom at timeframe {i}")
    fig1.savefig(f"{full_path_Out}/Bad_Seg_{i}.png")
    plt.close()
################
print(f"Getting region and subregion of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
fig1 = plt.figure()
plt.pcolormesh(Image_I.coronal_flats[7,:,:])
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Phantom at timeframe {7}")
fig1.savefig(f"{full_path_Out}/Phantom.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(np.sum(Image_I.Image[7,10:44,90:104,94:111],axis=2))
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Phantom at timeframe {7}")
fig1.savefig(f"{full_path_Out}/Subphantom.png")
plt.close()
#################
seg = 37
print(f"Getting region and subregion of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
fig1 = plt.figure()
plt.pcolormesh(np.sum(Image_I.voi[f"{seg}"][10:44,90:104,94:111],axis=1))
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Statistics Segmentation based on timeframe {seg}")
fig1.savefig(f"{full_path_Out}/Seg_I.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(np.sum(Image_C.voi[f"{seg}"][10:44,90:104,94:111],axis=1))
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Gradient Segmentation based on timeframe {seg}")
fig1.savefig(f"{full_path_Out}/Seg_C.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(np.sum(Image_F.voi[f"{seg}"][10:44,90:104,94:111],axis=1))
plt.xlabel("Pixel");plt.ylabel("Pixel");plt.title(f"Coronal View of a Filling Segmentation based on timeframe {seg}")
fig1.savefig(f"{full_path_Out}/Seg_F.png")
plt.close()
#################
print(f"Getting normal and error TACs of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")

fig1 = plt.figure()
plt.plot(Image_I.time,Image_I.voi_statistics[20])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TAC for a segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TAC.png")
plt.close()

fig1 = plt.figure()
Image_I.voi_statistics_avg = []
Image_I.voi_statistics_std = []
Image_I.linear_shifts_error(key=20)
plt.errorbar(Image_I.time,Image_I.voi_statistics_avg[0],Image_I.voi_statistics_std[0])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TAC with error for a segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TAC_e.png")
plt.close()
#################
print(f"Getting Dice Coefficients of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")

fig1 = plt.figure()
plt.pcolormesh(Image_I.dice_all[5:40,5:40]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \nstatistics-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
fig1.savefig(f"{full_path_Out}/Dice_I.png")
plt.close()

fig1 = plt.figure()
plt.pcolormesh(Image_C.dice_all[7:40,7:40]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \ngradient-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
fig1.savefig(f"{full_path_Out}/Dice_C.png")
plt.close()

fig1 = plt.figure()
Dice = np.array([[Image_F.dice_all[38,38],Image_F.dice_all[38,37],Image_F.dice_all[38,35]],
                [Image_F.dice_all[37,38],Image_F.dice_all[37,37],Image_F.dice_all[37,35]],
                [Image_F.dice_all[35,38],Image_F.dice_all[35,37],Image_F.dice_all[35,35]]])
plt.pcolormesh(Dice);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \nfilling-based segmentation of a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')
fig1.savefig(f"{full_path_Out}/Dice_F.png")
plt.close()
#################
print(f"Getting many TACs of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
"""
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
Image_F.linear_shifts_errors(keys=np.array([34,37,38,39]),verbose=True)
for i in range(len(Image_F.voi_statistics_avg)):
    plt.errorbar(Image_F.time+i*0.1,Image_F.voi_statistics_avg[i],Image_F.voi_statistics_std[i])
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with errors for a filling segmentation on a phantom")
plt.grid()
fig1.savefig(f"{full_path_Out}/TACs_F_e.png")
plt.close()"""
#################
print(f"Getting Dynesty parameters of the phantom in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
print("This part is done somewhere else... too long")
#################
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()