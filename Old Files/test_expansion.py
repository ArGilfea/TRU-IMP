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

if True:
    Image.add_VOI_ellipsoid(center = [45,94,101],axes = [10,25,35],do_moments= True, do_stats= True, save= True)
    print(f"Ellipsoid done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.expand_VOI(factors = [0.5,1,1], counter = 0)
print(f"Expansion 1 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.expand_VOI(factors = [0.5,2,1], counter = 0)
print(f"Expansion 2 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

Image.expand_VOI(factors = [1,1,0.5], counter = 0)
print(f"Expansion 3 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

for i in range(Image.voi_counter):
    Image.show_flats(key=i)

print(f"Program ran until the end in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
plt.show()