import numpy as np
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import matplotlib.pyplot as plt
import time
###
import MyFunctions.Pickle_Functions as PF
####
###

os.system('clear')
print(f"Starting program at {time.strftime('%H:%M:%S')}")
initial = time.time()

Image = PF.pickle_open("/Users/philippelaporte/Desktop/Test/FanDyn9_DicomImage.pkl")
print(f"Loading done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.VOI_ICM(acq = 20,subinfo=[[10,70],[88,100],[90,112]],do_moments= True, do_stats= True, save= True)
print(f"ICM done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

#Image.add_VOI_ellipsoid(center = [45,94,101],axes = [35,6,11],do_moments= True, do_stats= True, save= True)
print(f"Ellispoid done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

angle = np.pi/4

Image.rotation_VOI(angles = [angle,0,0], counter = 0)
print(f"Rotation 1 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.rotation_VOI(angles = [0,angle,0], counter = 0)
print(f"Rotation 2 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.rotation_VOI(angles = [0,0,angle], counter = 0)
print(f"Rotation 3 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

for i in range(Image.voi_counter):
    Image.show_flats(key=i)

print(f"Program ran until the end in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
plt.show()