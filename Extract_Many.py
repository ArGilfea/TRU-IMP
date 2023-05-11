import MyFunctions.Extract_Images as Extract
import MyFunctions.Extract_Images_R as Extract_r
import os
import math

os.system('clear')

def dose_cal(D_m,t_m,D_rmd = 0,t_rmd=0):
    if t_rmd ==0:
        t_rmd = t_m
    t_half = 109.8*60
    D_cal = D_m*math.exp(-t_m*math.log(2)/t_half)-D_rmd*math.exp(t_rmd*math.log(2)/t_half)
    return D_cal

print('Dose: ',dose_cal(21.7,60,6.47,120))

path_in = '/Volumes/Backup_Stuff/These/Fantôme/'
path_out ='/Volumes/Backup_Stuff/Python/Data'

############################################################
#Phantom
############################################################
"""Extract_r.Extract_Images(path_in+'FantDyn1/Acq1_1min/',path_out=path_out,mass=0.142,Dose_inj=35.34,
                        name='Fantome_1_1min',verbose=True,
                        Description='À ajouter',verbose_precise=True)
#Extract.Extract_Images(path_in+'FantDyn3/PET-AC-DYN-1-MIN/',path_out=path_out,mass=0.142,Dose_inj=35.34,name='Fantome_3_1min',verbose=True,Description='À ajouter',verbose_precise=True)

Extract.Extract_Images(path_in+'FantDyn5/PET-AC-DYN-1-MIN/',path_out=path_out,mass=0.14,Dose_inj=35.34,
                        name='Fantome_5_1min',verbose=True,
                        Description='Acquisition Statique de 40min. Problème écoulement de 2-8 min.',verbose_precise=True)
Extract.Extract_Images(path_in+'FantDyn6/PET-AC-DYN-1-MIN/',path_out=path_out,mass=0.14,Dose_inj=35.34,
                        name='Fantome_6_1min',verbose=True,
                        Description='Acquisition Statique de 40min. La fiole a penché de 90 à 30 degré sur la durée',verbose_precise=True)
Extract.Extract_Images(path_in+'FantDyn7/PET-AC-DYN-1-MIN/',path_out=path_out,mass=0.13,Dose_inj=35.34,
                        name='Fantome_7_1min',verbose=True,
                        Description='Acquisition Dynamique de 40min.',verbose_precise=True)
Extract.Extract_Images(path_in+'FantDyn8/PET-AC-DYN-1-MIN/',path_out=path_out,mass=0.13,Dose_inj=35.34,
                        name='Fantome_8_1min',verbose=True,
                        Description='Acquisition Dynamique de 40min. Petit écoulement de la fiole sur la base',verbose_precise=True)"""
Extract.Extract_Images("/Users/philippelaporte/Desktop/FantDYN9/PET-AC-DYN-1-MIN/",path_out="/Users/philippelaporte/Desktop/",mass=0.13,Dose_inj=35.34,
                        name='Fantome_9_1min',verbose=True,total_time=40,
                        Description='Acquisition Dynamique sans mouvement de 40min.',verbose_precise=True)
Extract.Extract_Images("/Users/philippelaporte/Desktop/FantDYN10/PET-AC-DYN-1-MIN/",path_out="/Users/philippelaporte/Desktop/",mass=0.13,Dose_inj=35.34,
                        name='Fantome_10_1min',verbose=True,total_time=40,
                        Description='Acquisition Dynamique sans mouvement de 40min.',verbose_precise=True)
############################################################
#Rats (CUSM)
############################################################
"""
Extract.Extract_Images('/Volumes/Backup_Stuff/These/Données CUSM/S025/PET_En_Ordre/',path_out=path_out,mass=0.239,Dose_inj=dose_cal(31.3,60,10.43,120), name='S025',verbose=True,rescale=True,Description='Control')
Extract.Extract_Images('/Volumes/Backup_Stuff/These/Données CUSM/S026/PET_En_Ordre/',path_out=path_out,mass=0.262,Dose_inj=dose_cal(32.2,60,13.26,120), name='S026',verbose=True,rescale=True,Description='PD')
Extract.Extract_Images('/Volumes/Backup_Stuff/These/Données CUSM/S027/PET_En_Ordre/',path_out=path_out,mass=0.274,Dose_inj=dose_cal(32.4,60,11.80,120), name='S027',verbose=True,rescale=True,Description='PD')
Extract.Extract_Images('/Volumes/Backup_Stuff/These/Données CUSM/S028/PET_En_Ordre/',path_out=path_out,mass=0.248,Dose_inj=dose_cal(32.0,60,8.23,180), name='S028',verbose=True,rescale=True,Description='Losartan')
Extract.Extract_Images('/Volumes/Backup_Stuff/These/Données CUSM/S029/PET_En_Ordre/',path_out=path_out,mass=0.254,Dose_inj=dose_cal(21.7,60,6.47,120), name='S029',verbose=True,rescale=True,Description='PD')
"""