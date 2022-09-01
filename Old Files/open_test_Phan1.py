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

t_0 = 5/3 #début écoulement d'eau
t=np.arange(t_0,39.1,0.1)
t_inj = 2/3 #fin injection
t_inj_all = np.arange(0,t_inj,0.01)
t_inter = np.arange(t_inj,t_0,0.001)
A_star_0 = 39.10 #MBq
k_1 = 0.05*60 #mL/s
k_2 = 0.05*60
V_1 = 17 #mL
V_2 = 125 #mL
weight = 0.142 #kg

t_demie = 109.8 #min
delta_t = 16 #min
A_star = A_star_0*np.exp(-np.log(2)*delta_t/t_demie)

A_1_0 = A_star/(2/3)*t_inj_all
A_1_inter = np.max(A_1_0)*np.ones_like(t_inter)
A_2_0 = 0*t_inj_all
A_3_0 = 0*t_inj_all
A_2_inter = 0*t_inter
A_3_inter = 0*t_inter
A_1 = A_star * np.exp(-k_1/V_1*(t-t_0))
A_2 = A_star*k_1*V_2/(k_1*V_2-k_2*V_1)*(np.exp(-k_2/V_2*(t-t_0))-np.exp(-k_1/V_1*(t-t_0)))
A_3 = A_star/(k_1*V_2-k_2*V_1)*(k_2*V_1*np.exp(-k_1/V_1*(t-t_0))-k_1*V_2*np.exp(-k_2/V_2*(t-t_0)))+A_star
###
os.system('clear')
#Extract_r.Extract_Images('/Users/philippelaporte/Desktop/École/Université/Ph D/Thèse/Fantôme/Acq1_1min/',path_out='/Users/philippelaporte/Desktop/Programmation/Python',mass=0.142,Dose_inj=35.34,name='Fantome_1_1min',verbose=True)

initial = time.time()
Fan1 = PF.pickle_open(os.path.dirname(os.path.realpath(__file__))+'/Fantome_1_1min.pkl')
print('Opening took ',"{:.2f}".format(time.time()-initial),' s')
print("Name",Fan1.name,"\nVersion: ",Fan1.version,'\nNumber of VOI: ',Fan1.voi_counter,'\nMethods: ',Fan1.voi_methods,' in ',Fan1.time_scale)
print("Dimensions: ",Fan1.nb_acq,Fan1.nb_slice,Fan1.width,Fan1.length)
print(f"Voxel size {Fan1.voxel_volume} mm^3, units {Fan1.units}")

print('Testing ellipsoid VOI')
now = time.time()
Fan1.add_VOI_ellipsoid(infos = np.array([[53,93,120],[3,3,3]]),name='Vial Ellipsoid',do_moments=True,do_stats=True) #Les chiffres sont inversés par rapport à MatLab
Fan1.add_VOI_ellipsoid(infos = np.array([[51,103,92],[20,10,10]]),name='Poche Ellipsoid',do_moments=True,do_stats=True) 

Fan1.VOI_Canny_filled(subinfo = [[45,58],[89,102],[116,122]],acq=3,name='Vial Canny',do_moments=True,do_stats=True) 
Fan1.VOI_Canny_filled(subinfo = [[15,80],[104,112],[82,100]],acq=11,name='Poche Canny',do_moments=True,do_stats=True) 
Fan1.VOI_Canny_filled(subinfo = [[6,101],[118,128],[49,82]],acq=39,name='Vidange Canny',do_moments=True,do_stats=True) 
print("Running the VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',Fan1.voi_counter,' VOIs, with ',Fan1.voi_voxels,' voxels')
print('Testing the average over the VOI')
now = time.time()

figure1 = plt.figure(1)
plt.plot(Fan1.time,Fan1.voi_statistics[2]/1000,label=Fan1.voi_name[2])
plt.plot(Fan1.time,Fan1.voi_statistics[3]/1000,label=Fan1.voi_name[3])
plt.plot(Fan1.time,Fan1.voi_statistics[4]/1000,label=Fan1.voi_name[4])
print(f"{np.max(Fan1.voi_statistics[2]-Fan1.voi_statistics[2][0])/np.max(A_1)},{np.max(Fan1.voi_statistics[3]-Fan1.voi_statistics[3][0])/np.max(A_2)},{np.max(Fan1.voi_statistics[4]-Fan1.voi_statistics[4][0])/np.max(A_3)}")
print(f"{1/np.max(Fan1.voi_statistics[2])*np.max(A_1)},{1/np.max(Fan1.voi_statistics[3])*np.max(A_2)},{1/np.max(Fan1.voi_statistics[4])*np.max(A_3)}")

plt.plot(t,A_1,'b',label='Vial Theorique');plt.plot(t_inj_all,A_1_0,'b');plt.plot(t_inter,A_1_inter,'b')
plt.plot(t,A_2,'r',label='Comp 1 Theorique');plt.plot(t_inj_all,A_2_0,'r');plt.plot(t_inter,A_2_inter,'r')
plt.plot(t,A_3,'m',label='Comp 2 Theorique');plt.plot(t_inj_all,A_3_0,'m');plt.plot(t_inter,A_3_inter,'m')
#plt.plot(t,A_1+A_2+A_3,'g',label='Total Theorique');plt.plot(t_inj_all,A_3_0,'g');plt.plot(t_inter,A_3_inter,'g')
plt.legend()
plt.xlabel('Time (min)')
plt.ylabel('MBq')
plt.grid()
plt.title(Fan1.name)
print("Running the curve took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',Fan1.voi_counter,' VOIs with ',Fan1.voi_voxels,' voxels')
print(f"Size of compartments: {Fan1.voxel_volume*Fan1.voi_voxels[2]/1000} mL, {Fan1.voxel_volume*Fan1.voi_voxels[3]/1000} and {Fan1.voxel_volume*Fan1.voi_voxels[4]/1000}")
print('Testing cuts')
now = time.time()
acq = 39
Fan1.show_flats(acq=3)
fig, axs = plt.subplots(2,2)
axs[0,0].pcolormesh(Fan1.axial_flat(counter=2)+Fan1.axial_flat(counter=3)+Fan1.axial_flat(counter=4));axs[0,0].set_title("Axial VOI")
axs[1,0].pcolormesh(Fan1.sagittal_flat(counter=2)+Fan1.sagittal_flat(counter=3)+Fan1.sagittal_flat(counter=4));axs[1,0].set_title("Sagittal VOI")
axs[0,1].pcolormesh(Fan1.coronal_flat(counter=2)+Fan1.coronal_flat(counter=3)+Fan1.coronal_flat(counter=4));axs[0,1].set_title("Coronal VOI")
print('Testing the slices took ',"{:.2f}".format(time.time()-now),' s')

plt.figure()
plt.plot(Fan1.time,Fan1.voi_statistics[2]*Fan1.convert_units('SUVbw'),label=Fan1.voi_name[2])
plt.plot(Fan1.time,Fan1.voi_statistics[3]*Fan1.convert_units('SUVbw'),label=Fan1.voi_name[3])
plt.plot(Fan1.time,Fan1.voi_statistics[4]*Fan1.convert_units('SUVbw'),label=Fan1.voi_name[4])
plt.legend()
plt.xlabel('Time (min)');plt.ylabel('SUV');plt.grid()

PF.pickle_save(Fan1,os.path.dirname(os.path.realpath(__file__))+'/Fantome_1_1min_2.pkl')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()
