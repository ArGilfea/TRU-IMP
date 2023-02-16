import numpy as np
import os
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

Image.reflection_ROI(counter = 0,axisNumber= 0)
print(f"Reflection 1 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
Image.reflection_ROI(counter = 0,axisNumber= 1)
print(f"Reflection 2 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
Image.reflection_ROI(counter = 0,axisNumber= 2)
print(f"Reflection 3 done in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")

for i in range(Image.voi_counter):
    Image.show_flats(key=i)

print(f"Program ran until the end in {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
plt.show()