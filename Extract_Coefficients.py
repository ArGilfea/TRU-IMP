import numpy as np
import os
import matplotlib.pyplot as plt
import time
from scipy.optimize import curve_fit
###
import MyFunctions.Batch_Segmentations as BS
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM
#import MyFunctions.DicomImage #Custom Class
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

name = name_rat[4]
comp = [name_comp[0],name_comp[1],name_comp[2]]
compar = comp[1]
seg = name_type[2]
device = devices[0]

full_name_rat = name+seg+'_Errors.pkl'
full_path_rat = path+name+'/'+full_name_rat

full_name_phantom = name+compar+seg+'_Errors.pkl'
full_path_phantom = path+name+'/'+full_name_phantom
full_path = full_path_rat

name_out = f"/Volumes/Backup_Stuff/Python/Results/{name+'/'+name+seg}_Coefficients.png"

print(full_path)
print(name_out)

Image = PF.pickle_open(full_path)

print(Image.nb_acq)
print(Image.voi_counter)

print("Number of error: ",len(Image.voi_statistics_avg))

dyn_opt, dyn_max, dyn_min = Image.Bayesian_analyses(key=-1,curves='Errors',method='Dynesty',verbose = True)

fig1,axs = plt.subplots(3,sharex=True)

axs[0].errorbar(np.arange(len(Image.voi_statistics_avg)),dyn_opt[:,0],yerr=[dyn_min[:,0],dyn_max[:,0]],label='Dynesty')
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid();axs[0].legend()

axs[1].errorbar(np.arange(len(Image.voi_statistics_avg)),dyn_opt[:,1],yerr=[dyn_min[:,1],dyn_max[:,1]],label='Dynesty')
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid();axs[1].legend()

axs[2].errorbar(np.arange(len(Image.voi_statistics_avg)),dyn_opt[:,2],yerr=[dyn_min[:,2],dyn_max[:,2]],label='Dynesty')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid();axs[2].legend()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig1.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig1.suptitle('Estimated Parameters with Dynesty')
fig1.savefig(name_out)
########
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()