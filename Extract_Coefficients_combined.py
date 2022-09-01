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

name = name_phantom[2]
comp = [name_comp[0],name_comp[1],name_comp[2]]
compar = comp[1]
seg = name_type[0]
device = devices[1]

full_name_rat = name+seg+'.pkl'
full_path_rat = path+name+'/'+full_name_rat

full_name_phantom = name+compar+seg+'_Errors.pkl'
full_path_phantom = path+name+'/'+full_name_phantom
full_path = full_path_phantom

name_out = f"/Volumes/Backup_Stuff/Python/Results/{name}/{name+compar}_All_methods_Coefficients_Pause.png"
titles = np.array([r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$",r"$\gamma_{12}/V_1$",r"$\gamma_{23}/V_2$"])

keys1 = np.arange(7,40)-0.1
keys2 = np.arange(5,40)
keys3 = np.array([34,37,38,39])+0.1

print(path+name+'/'+name+compar+name_type[2]+'_Errors.pkl')

print(f"Opening first image after {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
Image1 = PF.pickle_open(path+name+'/'+name+compar+name_type[0]+'_Errors.pkl')
print(f"Opening second image after {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
Image2 = PF.pickle_open(path+name+'/'+name+compar+name_type[1]+'_Errors.pkl')
print(f"Opening third image after {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
Image3 = PF.pickle_open(path+name+'/'+name+compar+name_type[2]+'_Errors.pkl')

if len(Image1.voi_statistics_avg) != keys1.shape[0]:
    raise Exception(f"Invalid choice, the dimensions don't fit\nLen Keys1 = {keys1.shape[0]} != {len(Image1.voi_statistics_avg)} = Nbr of errors")
if len(Image2.voi_statistics_avg) != keys2.shape[0]:
    raise Exception(f"Invalid choice, the dimensions don't fit\nLen Keys2 = {keys2.shape[0]} != {len(Image2.voi_statistics_avg)} = Nbr of errors")
if len(Image3.voi_statistics_avg) != keys3.shape[0]:
    raise Exception(f"Invalid choice, the dimensions don't fit\nLen Keys3 = {keys3.shape[0]} != {len(Image3.voi_statistics_avg)} = Nbr of errors")

dyn_opt1, dyn_max1, dyn_min1 = Image1.Bayesian_analyses(key=-1,curves='Errors',method='Dynesty',verbose = True,model='2_Comp_A2')
dyn_opt2, dyn_max2, dyn_min2 = Image2.Bayesian_analyses(key=-1,curves='Errors',method='Dynesty',verbose = True,model='2_Comp_A2')
dyn_opt3, dyn_max3, dyn_min3 = Image3.Bayesian_analyses(key=-1,curves='Errors',method='Dynesty',verbose = True,model='2_Comp_A2')

fig1,axs = plt.subplots(dyn_opt1.shape[1],sharex=True)
titles = np.array([r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$",r"$\gamma_{12}/V_1$",r"$\gamma_{23}/V_2$",r"$t_1$",r"$\Delta t$"])
for i in range(dyn_opt1.shape[1]):
    axs[i].errorbar(keys1,dyn_opt1[:,i],yerr=[dyn_min1[:,i],dyn_max1[:,i]],fmt='ko',label='Canny')
    axs[i].errorbar(keys2,dyn_opt2[:,i],yerr=[dyn_min2[:,i],dyn_max2[:,i]],fmt='ro',label='ICM')
    axs[i].errorbar(keys3,dyn_opt3[:,i],yerr=[dyn_min3[:,i],dyn_max3[:,i]],fmt='bo',label='Filling')
    #axs[i].errorbar(keys3,dyn_opt3[i],yerr=[dyn_min3[i],dyn_max3[i]],fmt='bo',label='Filling')
    axs[i].set_title(titles[i]);axs[i].grid();axs[i].legend()

plt.xlabel("Segmentation of Reference")
fig1.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig1.suptitle('Estimated Parameters with Dynesty')
fig1.savefig(name_out)
########
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()