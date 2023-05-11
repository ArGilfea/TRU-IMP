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
name_rat = 'S029'
ext = '.pkl'
initial = time.time()
Animal = PF.pickle_open(path+name_rat+ext)

print(f"Image size: {Animal.Image.shape}")
show_pre = False

seed = [17,60,108,62]
region = [[40,88],[88,128],[40,92]]

if show_pre:
    print("Showing seed positionning")
    Animal.show_point(seed,star=True)
    Animal.show_point(seed,star=True,log=True)
    Animal.show_curves(seed)
    print("Showing sub regions")
    Animal.show_point(seed,star=True,sub_im=region)
    plt.show()

print(f"Starting segmentations...")
k = 10
start_1 = 10
for i in range(k):
    iter_time = time.time()
    print(f"Iteration {i+1} of {3*k}, done in {(time.time()-initial):.1f}s")
    Animal.VOI_Canny_filled(subinfo = region,acq=start_1+i,sigma=5,name=f"Left Kidney Canny Filled acq {start_1+i}",do_moments=True,do_stats=True)
    print(f"Canny {i+1} done after {(time.time()-iter_time):.1f}s")

for i in range(k):
    iter_time = time.time()
    print(f"Iteration {k+i+1} of {3*k}, done in {(time.time()-initial):.1f}s")
    Animal.VOI_ICM(subinfo = region,alpha=1e1,max_iter=100,
                            acq=start_1+i,name=f"Left Kidney ICM acq {start_1+i}",do_moments=True,do_stats=True,verbose = False)
    print(f"ICM {i+1} done after {(time.time()-iter_time):.1f}s")

for i in range(k):
    iter_time = time.time()
    print(f"Iteration {2*k+i+1} of {3*k}, done in {(time.time()-initial):.1f}s")
    Animal.VOI_filled_f(seed=[seed[1:]],factor=[0.1,2.8],steps = 1000,acq=start_1+i,sub_im=region,
                    max_iter=300,verbose=False,verbose_graphs=True,max_number_save=1,
                    save_between=False,threshold=1.5*max([Animal.voi_voxels[i],Animal.voi_voxels[i+1]])/(Animal.length*Animal.width*Animal.nb_slice),
                    voxels_f=[min([Animal.voi_voxels[i],Animal.voi_voxels[k+i]])*0.6,max([Animal.voi_voxels[i],Animal.voi_voxels[k+i]])*1.4],
                    name=f"Left Kidney Filled acq {start_1+i}",do_moments=True,do_stats=True,break_after_f=True)
    print(f"Filling {i+1} done after {(time.time()-iter_time):.1f}s")

print(Animal.voi_voxels)
print(f"Saving...")
thresh = 0.5
for i in range(k):
    print(f"Thresholding {3*i+1} of {3*k}, done in {(time.time()-initial):.1f}s")
    Animal.VOI_threshold(acq=start_1+i,key=i,sigma=5,threshold=thresh,
    name=f"{Animal.voi_name[i]}, thresh = {thresh}",do_moments=True,do_stats=True)
for i in range(k):
    Animal.VOI_threshold(acq=start_1+i,key=k+i,sigma=5,threshold=thresh,
    name=f"{Animal.voi_name[k+i]}, thresh = {thresh}",do_moments=True,do_stats=True)
for i in range(k):
    Animal.VOI_threshold(acq=start_1+i,key=2*k+i,sigma=5,threshold=thresh,
    name=f"{Animal.voi_name[2*k+i]}, thresh = {thresh}",do_moments=True,do_stats=True)

Animal.Dice_all()
Animal.Jaccard_all()
print(Animal.voi_counter)

PF.pickle_save(Animal,path+name_rat+'_CIF'+ext)


print(f"Showing Curves...")
for i in range(Animal.voi_counter):
    Animal.show_flats(key=i,name=f"{Animal.voi_name[i]}")
plt.figure()
for i in range(Animal.voi_counter):
    plt.plot(Animal.time,Animal.voi_statistics[i],label=f"{Animal.voi_name[i]}")
plt.xlabel('Time');plt.ylabel('Activity');plt.title(f"Left Kidney");plt.grid();plt.legend()

print('Program ran until the end in ',"{:.1f}".format(time.time()-initial),' s')
plt.show()
