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

path ='/Volumes/Backup_Stuff/Python/Data_Results/'
name_phantom=np.array(['Fantome_1_1min','Fantome_5_1min','Fantome_6_1min','Fantome_7_1min','Fantome_8_1min'])
name_type = np.array(['_C_k_all','_I_k_all','_F_k_all'])
name_comp = np.array(['_comp_1','_comp_2','_comp_3'])
name_rat = np.array(['S025','S026','S027','S028','S029'])
devices = np.array(['rat','phantom'])
seg_method = {'_C_k_all':'Canny',
            '_I_k_all':'ICM',
            '_F_k_all':'Filling'
    }

name = name_rat[2]
comp = name_comp[1]
seg = name_type[0]
device = devices[0]
full_name_phantom = name+comp+seg+'.pkl'
full_name_rat = name+seg+'.pkl'
full_path_rat = path+name+'/'+full_name_rat
full_path_phantom = path+name+'/'+full_name_phantom
full_path = full_path_rat

order = 3
d=3

full_path_out_phantom = path+name+'/'+name+comp+seg+'_'+str(order)+'_Errors.pkl'
full_path_out_rat = path+name+'/'+name+seg+'_'+str(order)+'_Errors.pkl'

full_path_out=full_path_out_rat
keys = np.array([10,11,12])

keys = np.arange(12,21)

print(full_path)
print(full_path_out)
print(keys)
print(keys.shape)
Image = PF.pickle_open(full_path)
Image.voi_statistics_avg = []
Image.voi_statistics_std = []

fig1 = Image.show_coeff(keys,title=f"{seg_method[seg]} {name}")

Image.linear_shifts_errors(keys=keys,order=order,d=d,verbose=True,verbose_precise=True)

#mean, error,error2 = Image.std_stats(keys=keys,type_stat = 'linear')
vol, mean = Image.curve_common_vol(keys)
fig2 = plt.figure()
plt.plot(Image.time,mean,label=f"TAC of the common volume")
for i in range(len(Image.voi_statistics_avg)): 
    plt.errorbar(Image.time+i*0.1,Image.voi_statistics_avg[i],Image.voi_statistics_std[i],label=f"Seg {keys[i]}")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with uncertainties for {device} {name} with {seg_method[seg]}")
plt.grid();plt.legend()

fig3 = plt.figure()
for i in range(len(Image.voi_statistics_avg)): 
    plt.errorbar(Image.time+i*0.1,Image.voi_statistics_avg[i],Image.voi_statistics_std[i],label=f"Seg {keys[i]}")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with uncertainties for {device} {name} with {seg_method[seg]}")
plt.grid();plt.legend()

fig1.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/{name}_{seg_method[seg]}{comp}_{order}_{d}_D")
fig2.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/{name}_{seg_method[seg]}{comp}_{order}_{d}_e_VC")
fig3.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/{name}_{seg_method[seg]}{comp}_{order}_{d}_e")

#PF.pickle_save(Image,full_path_out)
print(f"Number of errors computed: {len(Image.voi_statistics_avg)}")

print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()