import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.pickle_functions as PF
import MyFunctions.Extract_Images_r as Extract_r
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt

os.system('clear')
print('Starting program...')
path ='/Volumes/Backup_Stuff/Python/Data/'
animal = 'S028'
extension = '_CIF.pkl'
initial = time.time()
S029 = PF.pickle_open(path+animal+extension)

each = 10
plt.show()
plt.figure(1)
plt.errorbar(S029.time,S029.mean_stats(np.arange(0,7)),2*S029.std_stats(np.arange(0,7)),label='Canny')
#plt.errorbar(S029.time+0.1,S029.mean_stats(np.arange(10,20)),2*S029.std_stats(np.arange(10,20)),label='ICM')
#plt.errorbar(S029.time-0.1,S029.mean_stats(np.arange(20,30)),2*S029.std_stats(np.arange(20,30)),label='Fill')
plt.xlabel("Time (min)");plt.ylabel("Average Activity (Bq/mL)");plt.grid();plt.legend();plt.title(f"Rat {animal} Left Kidney (Full)")

print(2*S029.std_stats(np.arange(0,7))/S029.mean_stats(np.arange(0,7)))

plt.figure(2)
plt.errorbar(S029.time,S029.mean_stats(np.arange(30,37)),2*S029.std_stats(np.arange(30,37)),label='Canny')
#plt.errorbar(S029.time+0.1,S029.mean_stats(np.arange(40,50)),2*S029.std_stats(np.arange(40,50)),label='ICM')
#plt.errorbar(S029.time-0.1,S029.mean_stats(np.arange(50,60)),2*S029.std_stats(np.arange(50,60)),label='Fill')
plt.xlabel("Time (min)");plt.ylabel("Average Activity (Bq/mL)");plt.grid();plt.legend();plt.title(f"Rat {animal} Left Kidney (Thresh)")

fig, axs = plt.subplots(2,2)
axs[0,0].pcolormesh(S029.dice_all[0:10,0:10]);axs[0,0].set_title("Canny")
axs[1,0].pcolormesh(S029.dice_all[10:20,10:20]);axs[1,0].set_title("ICM")
axs[0,1].pcolormesh(S029.dice_all[20:30,20:30]);axs[0,1].set_title("Fill")
#axs[2,0].pcolormesh(Dice_all_acq);axs[2,0].set_title("All acquisitions")
##axs[2,1].pcolormesh(Dice_all_m);axs[2,1].set_title("All methods")
fig.suptitle(f"Dice coefficients")   

plt.figure()
plt.pcolormesh(S029.dice_all[0:7,0:7]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a gradient-based segmentation on a rat")
plt.xlabel('First timeframe of reference')

plt.figure()
plt.pcolormesh(S029.dice_all[30:40,30:40])
plt.title("Canny Thresh");plt.colorbar()

plt.figure()
plt.pcolormesh(S029.dice_all[10:20,10:20])
plt.title("ICM");plt.colorbar()

fig, ax = plt.subplots(1)
plt.pcolormesh(S029.dice_all[40:40+each,40:40+each])
plt.xlabel("Segmentation de comparaison 1");plt.ylabel("Segmentation de comparaison 2")
ax.set_xticks(np.arange(0,each,1));ax.set_yticks(np.arange(0,each,1))
plt.title("Coefficients de Sørensen-Dice pour une segmentation statistique avec un seuil");plt.colorbar()

plt.figure()
plt.pcolormesh(S029.dice_all[20:30,20:30])
plt.title("Fill");plt.colorbar()

plt.figure()
plt.pcolormesh(S029.dice_all[50:60,50:60])
plt.title("Fill Thresh");plt.colorbar()

plt.figure()
plt.pcolormesh(S029.dice_all)
plt.title("All");plt.colorbar()


fig, axs = plt.subplots(2,2)
axs[0,0].pcolormesh(S029.axial_flat(counter=7));axs[0,0].set_title("Tranches Axiales Combinées");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
axs[1,0].pcolormesh(S029.sagittal_flat(counter=7));axs[1,0].set_title("Tranches Sagitales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
axs[0,1].pcolormesh(S029.coronal_flat(counter=7));axs[0,1].set_title("Tranches Coronales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
fig.suptitle(f"Segmentation Gradient")

fig, axs = plt.subplots(2,2)
axs[0,0].pcolormesh(S029.axial_flat(counter=17));axs[0,0].set_title("Tranches Axiales Combinées");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
axs[1,0].pcolormesh(S029.sagittal_flat(counter=17));axs[1,0].set_title("Tranches Sagitales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
axs[0,1].pcolormesh(S029.coronal_flat(counter=17));axs[0,1].set_title("Tranches Coronales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
fig.suptitle(f"Segmentation Statistiques")

fig, axs = plt.subplots(2,2)
axs[0,0].pcolormesh(S029.axial_flat(counter=27));axs[0,0].set_title("Tranches Axiales Combinées");axs[0,0].set_xlabel("y (voxels)");axs[0,0].set_ylabel("z (voxels)")
axs[1,0].pcolormesh(S029.sagittal_flat(counter=27));axs[1,0].set_title("Tranches Sagitales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("y (voxels)")
axs[0,1].pcolormesh(S029.coronal_flat(counter=27));axs[0,1].set_title("Tranches Coronales Combinées");axs[0,0].set_xlabel("x (voxels)");axs[0,0].set_ylabel("z (voxels)")
fig.suptitle(f"Segmentation Remplissage")

plt.figure()
for i in range(7):
    plt.plot(S029.time,S029.voi_statistics[i],label=f"{i}")
    plt.xlabel('Time (min)');plt.ylabel("Average Activity (Bq/mL)");plt.title("TACs from a gradient-based segmentation on a rat")
    plt.grid()

plt.figure()
plt.pcolormesh(S029.dice_all[0:7,0:7]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \ngradient-based segmentation on a rat")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()