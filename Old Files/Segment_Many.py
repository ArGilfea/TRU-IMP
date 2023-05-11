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
path ='/Volumes/Backup_Stuff/Python/Data'

initial = time.time()
Fan1 = PF.pickle_open(path+'/Fantome_1_1min.pkl')
Fan5 = PF.pickle_open(path+'/Fantome_5_1min.pkl')
Fan6 = PF.pickle_open(path+'/Fantome_6_1min.pkl')
Fan7 = PF.pickle_open(path+'/Fantome_7_1min.pkl')
Fan8 = PF.pickle_open(path+'/Fantome_8_1min.pkl')
print('Opening took ',"{:.2f}".format(time.time()-initial),' s')

print('Testing ellipsoid VOI')
now = time.time()
#3
#11
#39
maxi = 15
for k in range(maxi):
    print(f"Part done: {k} of {maxi}: {k/maxi*100}%. Time elpased: {time.time()-initial} s")
    Fan1.VOI_Canny_filled(subinfo = [[45,58],[89,102],[116,122]],acq=0+k,name='Vial Canny',do_moments=True,do_stats=True) 
    Fan1.VOI_Canny_filled(subinfo = [[15,80],[104,112],[82,100]],acq=1+k,name='Poche Canny',do_moments=True,do_stats=True) 
    Fan1.VOI_Canny_filled(subinfo = [[6,101],[118,128],[49,82]],acq=25+k,name='Vidange Canny',do_moments=True,do_stats=True) 

    Fan5.VOI_Canny_filled(subinfo = [[24,34],[68,82],[126,134]],acq=0+k,name='Vial Canny',do_moments=True,do_stats=True) 
    Fan5.VOI_Canny_filled(subinfo = [[5,50],[80,90],[90,112]],acq=1+k,name='Poche Canny',do_moments=True,do_stats=True) 
    Fan5.VOI_Canny_filled(subinfo = [[5,46],[100,110],[51,87]],acq=25+k,name='Vidange Canny',do_moments=True,do_stats=True) 

    Fan6.VOI_Canny_filled(subinfo = [[22,29],[80,90],[126,137]],acq=0+k,name='Vial Canny',do_moments=True,do_stats=True) 
    Fan6.VOI_Canny_filled(subinfo = [[12,39],[83,102],[92,114]],acq=1+k,name='Poche Canny',do_moments=True,do_stats=True) 
    Fan6.VOI_Canny_filled(subinfo = [[1,50],[109,120],[58,90]],acq=25+k,name='Vidange Canny',do_moments=True,do_stats=True) 

    Fan7.VOI_Canny_filled(subinfo = [[18,28],[72,82],[120,128]],acq=0+k,name='Vial Canny',do_moments=True,do_stats=True) 
    Fan7.VOI_Canny_filled(subinfo = [[10,48],[78,96],[85,108]],acq=1+k,name='Poche Canny',do_moments=True,do_stats=True) 
    Fan7.VOI_Canny_filled(subinfo = [[7,50],[90,112],[47,82]],acq=25+k,name='Vidange Canny',do_moments=True,do_stats=True) 

    Fan8.VOI_Canny_filled(subinfo = [[22,37],[73,86],[126,135]],acq=0+k,name='Vial Canny',do_moments=True,do_stats=True) 
    Fan8.VOI_Canny_filled(subinfo = [[11,52],[84,96],[90,115]],acq=1+k,name='Poche Canny',do_moments=True,do_stats=True) 
    Fan8.VOI_Canny_filled(subinfo = [[10,53],[101,115],[55,90]],acq=25+k,name='Vidange Canny',do_moments=True,do_stats=True) 
print("Running the VOI took ","{:.2f}".format(time.time()-now),' s\nWith a total of ',Fan1.voi_counter,' VOIs, with ',Fan1.voi_voxels,' voxels')

PF.pickle_save(Fan1,path+'/Fantome_1_1min_Canny.pkl')
PF.pickle_save(Fan5,path+'/Fantome_5_1min_Canny.pkl')
PF.pickle_save(Fan6,path+'/Fantome_6_1min_Canny.pkl')
PF.pickle_save(Fan7,path+'/Fantome_7_1min_Canny.pkl')
PF.pickle_save(Fan8,path+'/Fantome_8_1min_Canny.pkl')

print('Program ran until the end in ',"{:.2f}".format(time.time()-initial),' s')
plt.show()
