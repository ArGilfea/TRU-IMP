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
seg = name_type[1]
device = devices[1]

full_name_rat = name+seg+'.pkl'
full_path_rat = path+name+'/'+full_name_rat

full_name_phantom1 = name+comp[0]+seg+'.pkl'
full_name_phantom2 = name+comp[1]+seg+'.pkl'
full_name_phantom3 = name+comp[2]+seg+'.pkl'
full_path_phantom1 = path+name+'/'+full_name_phantom1
full_path_phantom2 = path+name+'/'+full_name_phantom2
full_path_phantom3 = path+name+'/'+full_name_phantom3
full_path = full_path_phantom1

print(full_path_phantom2)

Image1 = PF.pickle_open(full_path_phantom1)
Image2 = PF.pickle_open("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")

keys1 = np.arange(1,24)
keys2 = np.arange(1,40)

fig1 = Image1.show_coeff(keys1,title=f"{seg_method[seg]} {comp[0]} {name}")
fig2 = Image2.show_coeff(keys2,title=f"{seg_method[seg]} {comp[1]} {name}")

print(f"Number of errors computed: {len(Image1.voi_statistics_avg)}")
print(f"Number of errors computed: {len(Image2.voi_statistics_avg)}")

fig3 = plt.figure()
for i in range(len(Image1.voi_statistics_avg)): 
    plt.errorbar(Image1.time+i*0.04,Image1.voi_statistics_avg[i],Image1.voi_statistics_std[i],label=f"Seg {keys1[i]}")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with uncertainties for {device} {name} with {seg_method[seg]}")
plt.grid();plt.legend()

fig4 = plt.figure()
for i in range(len(Image2.voi_statistics_avg)): 
    plt.errorbar(Image2.time+i*0.04,Image2.voi_statistics_avg[i],Image2.voi_statistics_std[i],label=f"Seg {keys2[i]}")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"TACs with uncertainties for {device} {name} with {seg_method[seg]}")
plt.grid();plt.legend()

fig5 = plt.figure()
for i in range(len(Image1.voi_statistics_avg)): 
    for j in range(len(Image2.voi_statistics_avg)): 
        A21 = Image2.voi_statistics_avg[j]/(Image1.voi_statistics_avg[i]+0.001)
        plt.plot(Image2.time+i*0.04,A21)
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"Relative TACs for {device} {name} with {seg_method[seg]}")
plt.grid()

fig6 = plt.figure()
for i in range(len(Image1.voi_statistics_avg)): 
    for j in range(len(Image2.voi_statistics_avg)): 
        A21 = Image2.voi_statistics_avg[j]/(Image1.voi_statistics_avg[i]+0.001)
        delta_V = Image2.voi_voxels[keys2[j]]-Image1.voi_voxels[keys1[i]]
        courbe = np.log(delta_V*A21/Image1.voi_voxels[keys1[i]]+1)
        plt.plot(Image2.time+i*0.04,courbe)
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"Relative TACs for {device} {name} with {seg_method[seg]}")
plt.grid()

########

t_data=Image2.time
y_data = Image2.voi_statistics_avg[10]/(Image1.voi_statistics_avg[10]+0.001)
def A21(t,k1,k2):
    V1=Image1.voi_voxels[10]
    V2=Image2.voi_voxels[10]
    K = (k1*V2-k2*V1)/V1
    return k1/K*(np.exp(K*t/V2)-1)

popt, pcov = curve_fit(A21, t_data, y_data)
"""print(f"popt: {popt}")
print(f"pcov: {pcov}")

print(f"pmin: {popt-np.sqrt(np.diag(pcov))}")
print(f"pmax: {popt+np.sqrt(np.diag(pcov))}")"""

fig7 = plt.figure()
plt.plot(t_data, A21(t_data, *popt), 'r-',label='fit opt: a=%5.3f, b=%5.3f' % tuple(popt))
plt.plot(t_data, A21(t_data, *popt-np.sqrt(np.diag(pcov))), 'b-',label='fit low: a=%5.3f, b=%5.3f' % tuple(popt-np.sqrt(np.diag(pcov))))
plt.plot(t_data, A21(t_data, *popt+np.sqrt(np.diag(pcov))), 'g-',label='fit high: a=%5.3f, b=%5.3f' % tuple(popt+np.sqrt(np.diag(pcov))))
plt.plot(t_data,y_data,label="Experimental")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"Fitting A21")
plt.grid();plt.legend()

########

t_data=Image2.time
y_data = Image2.voi_statistics_avg[10]
def A2(t,A,gamma_12,gamma_23):
    A0 = max(Image2.voi_statistics_avg[10])
    V1=Image1.voi_voxels[10]
    V2=Image2.voi_voxels[10]
    K = A*gamma_12/(gamma_23*V1-gamma_12*V2)
    return A*(np.exp(-gamma_12/V1*t)-np.exp(-gamma_23/V2*t))

popt, pcov = curve_fit(A2, t_data, y_data)

"""print("A0 = ", max(Image2.voi_statistics_avg[10]))
print(f"popt: {popt}")
print(f"pcov: {pcov}")

print(f"pmin: {popt-np.sqrt(np.diag(pcov))}")
print(f"pmax: {popt+np.sqrt(np.diag(pcov))}")"""

b = [1000,1000]

fig8 = plt.figure()
plt.plot(t_data, A2(t_data, *popt), 'r-',label='fit opt: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
#plt.plot(t_data, A2(t_data, *b), 'b-',label='Test: a=%5.3f, b=%5.3f' % tuple(b))
plt.plot(t_data, A2(t_data, *popt-np.sqrt(np.diag(pcov))), 'b-',label='fit low: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt-np.sqrt(np.diag(pcov))))
plt.plot(t_data, A2(t_data, *popt+np.sqrt(np.diag(pcov))), 'g-',label='fit high: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt+np.sqrt(np.diag(pcov))))
plt.plot(t_data,y_data,label="Experimental")
plt.errorbar(Image2.time,Image2.voi_statistics_avg[10],Image2.voi_statistics_std[10],label=f"Seg ICM")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"Fitting A2")
plt.grid();plt.legend()
########

t_data=Image2.time

est_opt = np.zeros((len(Image2.voi_statistics_avg),3))
est_min = np.zeros((len(Image2.voi_statistics_avg),3))
est_max = np.zeros((len(Image2.voi_statistics_avg),3))

for i in range(len(Image2.voi_statistics_avg)):
    print(i)
    y_data = Image2.voi_statistics_avg[i]
    def A2(t,A,gamma_12,gamma_23):
        V1=Image1.voi_voxels[i]
        V2=Image2.voi_voxels[i]
        K = A*gamma_12/(gamma_23*V1-gamma_12*V2)
        return A*(np.exp(-gamma_12/V1*t)-np.exp(-gamma_23/V2*t))
    try:
        popt, pcov = curve_fit(A2, t_data, y_data)
        est_opt[i,:] = popt
        est_min[i,:] = popt-np.sqrt(np.diag(pcov))
        est_max[i,:] = popt+np.sqrt(np.diag(pcov))
    except RuntimeError:
        print(f"Error - curve_fit failed for iteration {i}")

fig9,axs = plt.subplots(3,sharex=True)

axs[0].plot(est_opt[:,0],label='Opt');axs[0].plot(est_min[:,0],label='Min');axs[0].plot(est_max[:,0],label='Max')
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid()

axs[1].plot(est_opt[:,1],label='Opt');axs[1].plot(est_min[:,1],label='Min');axs[1].plot(est_max[:,1],label='Max')
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid()

axs[2].plot(est_opt[:,2],label='Opt');axs[2].plot(est_min[:,2],label='Min');axs[2].plot(est_max[:,2],label='Max')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig9.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig9.suptitle('Estimated Parameters')

########
fig9.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/Coefficients_{name}_{seg_method[seg]}{comp}.png")

########
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()