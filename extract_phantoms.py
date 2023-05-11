import numpy as np
import os
import matplotlib.pyplot as plt
from MyFunctions.DicomImage import DicomImage #Custom Class
import MyFunctions.Pickle_Functions as PF
import time
###
import numpy as np
import time
import matplotlib.pyplot as plt

os.system('clear')
print('Starting program...')
path ='/Volumes/Backup_Stuff/Python/Data/'
Fantome = 'Fantome_5_1min'
ext = '.pkl'

initial = time.time()
Fan = PF.pickle_open(path+Fantome+ext)

print(f"Image size: {Fan.Image.shape}")

seed_a = [2,30,75,130]
seed_b = [10,30,95,102]
seed_c = [25,30,107,68]

show_pre = True
if show_pre:
    print("Showing seed positionning")
    Fan.show_point(seed_a,star=True)
    Fan.show_curves(seed_a)
    Fan.show_point(seed_b,star=True)
    Fan.show_curves(seed_b)
    Fan.show_point(seed_c,star=True)
    Fan.show_curves(seed_c)

seed_1 = [[23,36],[70,82],[125,135]]
seed_2 = [[5,55],[87,100],[91,112]]
seed_3 = [[9,55],[100,116],[53,88]]

if show_pre:
    print("Showing sub regions")
    Fan.show_point(seed_a,star=True,sub_im=seed_1)
    Fan.show_point(seed_b,star=True,sub_im=seed_2)
    Fan.show_point(seed_c,star=True,sub_im=seed_3)
    plt.show()
seed_a = [seed_a[1:]]
seed_b = [seed_b[1:]]
seed_c = [seed_c[1:]]

print(f"Starting segmentations...")
k = 10
start_1 = 0
start_2 = 7
start_3 = 20
for i in range(k):
    print(f"Iteration {i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Canny underway...")
    Fan.VOI_Canny_filled(subinfo = seed_1,acq=start_1+i,name=f"Compartiment 1 Canny Filled acq {start_1+i}",do_moments=True,do_stats=True)
for i in range(k):
    print(f"Iteration {k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"ICM underway...")
    Fan.VOI_ICM(subinfo = seed_1,alpha=1e1,max_iter=100,
                            acq=start_1+i,name=f"Compartiment 1 ICM acq {start_1+i}",do_moments=True,do_stats=True,verbose = False)
for i in range(k):
    print(f"Iteration {2*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Filling underway...")
    Fan.VOI_filled_f(seed=seed_a,factor=[0.1,2.8],steps = 1000,acq=start_1+i,max_iter=300,verbose=False,verbose_graphs=True,max_number_save=1,
                    save_between=False,threshold=0.9,sub_im=seed_1,
                    voxels_f=[min([Fan.voi_voxels[i],Fan.voi_voxels[i+1]])*0.6,max([Fan.voi_voxels[i],Fan.voi_voxels[i+1]])*1.4],
                    name='Compartiment 1 Filled',do_moments=True,do_stats=True)

for i in range(k):
    print(f"Iteration {3*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Canny underway...")
    Fan.VOI_Canny_filled(subinfo = seed_2,acq=start_2+i,name=f"Compartiment 2 Canny Filled acq {start_2+i}",do_moments=True,do_stats=True)
for i in range(k):
    print(f"Iteration {4*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"ICM underway...")
    Fan.VOI_ICM(subinfo = seed_2,alpha=1e1,max_iter=100,
                            acq=start_2+i,name=f"Compartiment 2 ICM acq {start_2+i}",do_moments=True,do_stats=True,verbose = False)
for i in range(k):
    print(f"Iteration {5*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Filling underway...")
    Fan.VOI_filled_f(seed=seed_b,factor=[0.1,2.8],steps = 1000,acq=start_2+i,max_iter=300,verbose=False,verbose_graphs=True,max_number_save=1,
                    save_between=False,threshold=0.9,sub_im=seed_2,
                    voxels_f=[min([Fan.voi_voxels[i+3*k],Fan.voi_voxels[i+1+3*k]])*0.6,max([Fan.voi_voxels[i+3*k],Fan.voi_voxels[i+1+3*k]])*1.4],
                    name='Compartiment 2 Filled',do_moments=True,do_stats=True)

for i in range(k):
    print(f"Iteration {2*3*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Canny underway...")
    Fan.VOI_Canny_filled(subinfo = seed_3,acq=start_3+i,name=f"Compartiment 3 Canny Filled acq {start_3+i}",do_moments=True,do_stats=True)
for i in range(k):
    print(f"Iteration {7*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"ICM underway...")
    Fan.VOI_ICM(subinfo = seed_3,alpha=1e1,max_iter=100,
                            acq=start_3+i,name=f"Compartiment 3 ICM acq {start_3+i}",do_moments=True,do_stats=True,verbose = False)
for i in range(k):
    print(f"Iteration {8*k+i+1} of {3*3*k}, done in {(time.time()-initial):.3f}s")
    print(f"Filling underway...")
    Fan.VOI_filled_f(seed=seed_c,factor=[0.1,2.8],steps = 1000,acq=start_3+i,max_iter=300,verbose=False,verbose_graphs=False,max_number_save=1,
                    save_between=False,threshold=0.9,sub_im=seed_3,
                    voxels_f=[min([Fan.voi_voxels[i+6*k],Fan.voi_voxels[i+1+6*k]])*0.6,max([Fan.voi_voxels[i+6*k],Fan.voi_voxels[i+1+6*k]])*1.4],
                    name='Compartiment 3 Filled',do_moments=True,do_stats=True)

print(Fan.voi_voxels)

print(f"Showing Curves...")

for i in range(Fan.voi_counter):
    Fan.show_flats(key=i)

plt.figure()
for i in range(Fan.voi_counter):
    plt.plot(Fan.time,Fan.voi_statistics[i],label=f"{Fan.voi_name[i]}")
plt.xlabel('Time');plt.ylabel('Activity');plt.title(f"Comp1");plt.grid();plt.legend()
Fan.Dice_all()
Fan.Jaccard_all()

PF.pickle_save(Fan,path+Fantome+'_CIF'+ext)

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()