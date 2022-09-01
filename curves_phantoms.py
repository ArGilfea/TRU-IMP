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
phantom = 'Fantome_8_1min_CIF'
extension = '.pkl'
initial = time.time()
Fan = PF.pickle_open(path+phantom+extension)
print(f"Loaded the file in {time.time()-initial:.1f} s")
each = 10
print(Fan.voi_counter)

plt.figure(1)
plt.errorbar(Fan.time,Fan.mean_stats(np.arange(1,10)),2*Fan.std_stats(np.arange(1,10)),label='Canny')
#plt.errorbar(Fan.time+0.1,Fan.mean_stats(np.arange(10,20)),2*Fan.std_stats(np.arange(10,20)),label='ICM')
#plt.errorbar(Fan.time-0.1,Fan.mean_stats(np.arange(20,30)),2*Fan.std_stats(np.arange(20,30)),label='Fill')
plt.xlabel("Time (min)");plt.ylabel("Average Activity (Bq/mL)");plt.grid();plt.legend();plt.title(f"Phantom {phantom} 1st compartment")
print(2*Fan.std_stats(np.arange(1,10))/Fan.mean_stats(np.arange(1,10)))

plt.figure(2)
plt.errorbar(Fan.time,Fan.mean_stats(np.arange(30,39)),2*Fan.std_stats(np.arange(30,39)),label='Canny')
#plt.errorbar(Fan.time+0.1,Fan.mean_stats(np.arange(40,50)),2*Fan.std_stats(np.arange(40,50)),label='ICM')
#plt.errorbar(Fan.time-0.1,Fan.mean_stats(np.arange(50,60)),2*Fan.std_stats(np.arange(50,60)),label='Fill')
plt.xlabel("Time (min)");plt.ylabel("Average Activity (Bq/mL)");plt.grid();plt.legend();plt.title(f"Phantom {phantom} 2nd compartment")

plt.figure(3)
plt.errorbar(Fan.time,Fan.mean_stats(np.arange(60,70)),2*Fan.std_stats(np.arange(60,70)),label='Canny')
plt.errorbar(Fan.time+0.1,Fan.mean_stats(np.arange(70,80)),2*Fan.std_stats(np.arange(70,80)),label='ICM')
#plt.errorbar(Fan.time-0.1,Fan.mean_stats(np.arange(80,90)),2*Fan.std_stats(np.arange(80,90)),label='Fill')
plt.xlabel("Time (min)");plt.ylabel("Average Activity (Bq/mL)");plt.grid();plt.legend();plt.title(f"Phantom {phantom} 3rd compartment")

plt.figure()
plt.pcolormesh(Fan.dice_all[1:10,1:10]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a gradient-based segmentation");plt.colorbar()
plt.xlabel('First timeframe of reference');plt.xlabel('Second timeframe of reference')

for i in range(3):
    step = i*30
    fig, axs = plt.subplots(2,2)
    axs[0,0].pcolormesh(Fan.dice_all[step+0:step+10,step+0:step+10]);axs[0,0].set_title(f"Canny Compartment {i+1}")
    axs[1,0].pcolormesh(Fan.dice_all[step+10:step+20,step+10:step+20]);axs[1,0].set_title(f"ICM Compartment {i+1}")
    axs[0,1].pcolormesh(Fan.dice_all[step+20:step+30,step+20:step+30]);axs[0,1].set_title(f"Fill Compartment {i+1}")
    axs[1,1].pcolormesh(Fan.dice_all[step+0:step+30,step+0:step+30]);axs[1,1].set_title(f"All Compartment {i+1}")
    fig.suptitle(f"Dice coefficients Compartment {i+1}")   


plt.figure()
for i in range(30,40):
    plt.plot(Fan.time,Fan.voi_statistics[i],label=f"{i}")
    plt.legend()

plt.figure()
for i in range(30,39):
    plt.plot(Fan.time,Fan.voi_statistics[i],label=f"{i}")
    plt.xlabel('Time (min)');plt.ylabel("Average Activity (Bq/mL)");plt.title("TACs from a gradient-based segmentation on a phantom")
    plt.grid()

plt.figure()
plt.pcolormesh(Fan.dice_all[30:39,30:39]);plt.colorbar()
plt.title("Sørensen-Dice coefficients for a \ngradient-based segmentation on a phantom")
plt.xlabel('First timeframe of reference');plt.ylabel('Second timeframe of reference')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()