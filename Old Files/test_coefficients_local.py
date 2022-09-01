import numpy as np
import os
import matplotlib.pyplot as plt
import time
from scipy.optimize import curve_fit
###
import MyFunctions.Batch_Segmentations as BS
import MyFunctions.Pickle_Functions as PF
import MyFunctions.Graph_Many as GM

from dynesty import NestedSampler
from dynesty import plotting as dyplot
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

#Image1 = PF.pickle_open(full_path_phantom1)
Image2 = PF.pickle_open("/Users/philippelaporte/Desktop/Programmation/Python/Data/Fantome_6_1min_comp_2_I_k_all.pkl")

keys1 = np.arange(1,24)
keys2 = np.arange(1,40)
'''
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
'''
########

t_data=Image2.time
y_data = Image2.voi_statistics_avg[10]
def A2(t,A,gamma_12,gamma_23):
    A0 = max(Image2.voi_statistics_avg[10])
    #V1=Image1.voi_voxels[10]
    V2=Image2.voi_voxels[10]
    #K = A*gamma_12/(gamma_23*V1-gamma_12*V2)
    return A*(np.exp(-gamma_12*t)-np.exp(-gamma_23*t))

popt1, pcov1 = curve_fit(A2, t_data, y_data)

"""print("A0 = ", max(Image2.voi_statistics_avg[10]))
print(f"popt: {popt}")
print(f"pcov: {pcov}")

print(f"pmin: {popt-np.sqrt(np.diag(pcov))}")
print(f"pmax: {popt+np.sqrt(np.diag(pcov))}")"""

b = [1000,1000]

fig8 = plt.figure()
plt.plot(t_data, A2(t_data, *popt1), 'r-',label='fit opt: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt1))
#plt.plot(t_data, A2(t_data, *b), 'b-',label='Test: a=%5.3f, b=%5.3f' % tuple(b))
plt.plot(t_data, A2(t_data, *popt1-np.sqrt(np.diag(pcov1))), 'b-',label='fit low: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt1-np.sqrt(np.diag(pcov1))))
plt.plot(t_data, A2(t_data, *popt1+np.sqrt(np.diag(pcov1))), 'g-',label='fit high: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt1+np.sqrt(np.diag(pcov1))))
plt.plot(t_data,y_data,label="Experimental")
plt.errorbar(Image2.time,Image2.voi_statistics_avg[10],Image2.voi_statistics_std[10],label=f"Seg ICM")
plt.xlabel("Time (min)");plt.ylabel("Signal");plt.title(f"Fitting A2")
plt.grid();plt.legend()
###################################
#Brute Force Parameters Estimation#
###################################
t_data=Image2.time

est_opt = np.zeros((len(Image2.voi_statistics_avg),3))
est_min = np.zeros((len(Image2.voi_statistics_avg),3))
est_max = np.zeros((len(Image2.voi_statistics_avg),3))

for i in range(len(Image2.voi_statistics_avg)):
    y_data = Image2.voi_statistics_avg[i]
    def A2(t,A,gamma_12,gamma_23):
        #V1=Image1.voi_voxels[i]
        V2=Image2.voi_voxels[i]
        #K = A*gamma_12/(gamma_23*V1-gamma_12*V2)
        return A*(np.exp(-gamma_12*t)-np.exp(-gamma_23*t))
    try:
        popt, pcov = curve_fit(A2, t_data, y_data)
        est_opt[i,:] = popt
        est_min[i,:] = popt-np.sqrt(np.diag(pcov))
        est_max[i,:] = popt+np.sqrt(np.diag(pcov))
    except RuntimeError:
        print(f"Error - curve_fit failed for iteration {i}")

fig9,axs = plt.subplots(3,sharex=True)

axs[0].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,0],yerr=[est_opt[:,0]-est_min[:,0],est_max[:,0]-est_opt[:,0]])
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid()

axs[1].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,1],yerr=[est_opt[:,1]-est_min[:,1],est_max[:,1]-est_opt[:,1]])
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid()

axs[2].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,2],yerr=[est_opt[:,2]-est_min[:,2],est_max[:,2]-est_opt[:,2]])
#axs[2].plot(est_opt[:,2],label='Opt');axs[2].plot(est_min[:,2],label='Min');axs[2].plot(est_max[:,2],label='Max')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig9.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig9.suptitle('Estimated Parameters')
###################################
#Dynesty Parameters Estimation (1)#
###################################
t_data=Image2.time
y_data = Image2.voi_statistics_avg[10]
e_data = Image2.voi_statistics_std[10]+1e0
e_data[0:2] += max(Image2.voi_statistics_std[10])
def model(t,param):
    '''
    Param is [A,gamma_12,gamma_23]
    '''
    return param[0]*(np.exp(-param[1]*t)-np.exp(-param[2]*t))
def prior_transform(param_unif_0_1,param_limit):
    param = np.ones_like(param_unif_0_1)
    param[0] = param_unif_0_1[0]*(param_limit[0,1]-param_limit[0,0])+param_limit[0,0]
    param[1] = param_unif_0_1[1]*(param_limit[1,1]-param_limit[1,0])+param_limit[1,0]
    param[2] = param_unif_0_1[2]*(param_limit[2,1]-param_limit[2,0])+param_limit[2,0]
    param[0] = param_limit[0,0]*np.exp(param_unif_0_1[0]*np.log(param_limit[0,1]/param_limit[0,0]))
    param[1] = param_limit[1,0]*np.exp(param_unif_0_1[1]*np.log(param_limit[1,1]/param_limit[1,0]))
    param[2] = param_limit[2,0]*np.exp(param_unif_0_1[2]*np.log(param_limit[2,1]/param_limit[2,0]))
    return param
def loglike(param,data_t,data_f,data_e):
    prob = 0
    #First compute the model with the parameters
    m = model(data_t,param)
    #Now compute the probability of the model w.r.t. data
    for j in range(m.shape[0]): #This is a specific point for that model
        prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
    return prob

print('Dynesty starting...')
param_init = np.array([[1e-5,1e4],[1e-5,1e0],[1e-5,1e0]])
labels = ["K", "gamma_12/V1","gamma_23/V2"]
ndim = 3
samplerDynesty = NestedSampler(loglike,prior_transform,ndim,logl_args=[t_data,y_data,e_data],ptform_args=[param_init],nlive=1500)

samplerDynesty.run_nested(maxiter=1e5)

results = samplerDynesty.results

lnz_truth = ndim * -np.log(2 * 10.)  # analytic evidence solution

figu, axes = dyplot.runplot(results, lnz_truth=lnz_truth)  # summary (run) plot
fig, axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels,title_fmt=".4f")
fg, ax = dyplot.cornerplot(results, color='dodgerblue', show_titles=True,quantiles=None, max_n_ticks=3,labels=labels,title_fmt=".4f")

optimal_Dynesty = results.samples[-1,:]
print(f"Dynesty Results: {optimal_Dynesty}")
best_fit_Dynesty = model(t_data,optimal_Dynesty)

K = axes[0,1].title.get_text()
print(K)
print(axes[1,1].title.get_text())
print(axes[2,1].title.get_text())

print("Min K = ",K[K.find("-")+1:K.find("^")-1])
print("Max K = ",K[K.find("+")+1:K.find("}$")])

print("Min gamma_12/V1 = ",axes[1,1].title.get_text()[axes[1,1].title.get_text().find("-")+1:axes[1,1].title.get_text().find("^")-1])
print("Max gamma_12/V1 = ",axes[1,1].title.get_text()[axes[1,1].title.get_text().find("+")+1:axes[1,1].title.get_text().find("}$")])

print("Min gamma_23/V2 = ",axes[2,1].title.get_text()[axes[2,1].title.get_text().find("-")+1:axes[2,1].title.get_text().find("^")-1])
print("Max gamma_23/V2 = ",axes[2,1].title.get_text()[axes[2,1].title.get_text().find("+")+1:axes[2,1].title.get_text().find("}$")])

fig10 = plt.figure()
plt.errorbar(t_data,y_data,e_data,label='Measured')
plt.plot(t_data, A2(t_data, *popt1), 'r-',label='Brute fit opt: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt1))
plt.plot(t_data,best_fit_Dynesty,label='Dynesty')
plt.xlabel('Time (min)');plt.ylabel('Signal');plt.title('Dynesty Parameter Estimation')
plt.grid();plt.legend()
#plt.show()
#####################################
#Dynesty Parameters Estimation (all)#
#####################################

dyn_opt = np.zeros((len(Image2.voi_statistics_avg),3))
dyn_min = np.zeros((len(Image2.voi_statistics_avg),3))
dyn_max = np.zeros((len(Image2.voi_statistics_avg),3))

param_init = np.array([[1e-5,1e4],[1e-5,1e0],[1e-5,1e0]])
labels = ["K", "gamma_12/V1","gamma_23/V2"]
ndim = 3
initial = time.time()
for i in range(len(Image2.voi_statistics_avg)):
    print(f"Iter {i+1} of {len(Image2.voi_statistics_avg)} after {(time.time()-initial):.2f} s at {time.strftime('%H:%M:%S')}")
    def model(t,param):
        '''
        Param is [A,gamma_12,gamma_23]
        '''
        return param[0]*(np.exp(-param[1]*t)-np.exp(-param[2]*t))
    def prior_transform(param_unif_0_1,param_limit):
        param = np.ones_like(param_unif_0_1)
        param[0] = param_limit[0,0]*np.exp(param_unif_0_1[0]*np.log(param_limit[0,1]/param_limit[0,0]))
        param[1] = param_limit[1,0]*np.exp(param_unif_0_1[1]*np.log(param_limit[1,1]/param_limit[1,0]))
        param[2] = param_limit[2,0]*np.exp(param_unif_0_1[2]*np.log(param_limit[2,1]/param_limit[2,0]))
        return param
    def loglike(param,data_t,data_f,data_e):
        prob = 0
        #First compute the model with the parameters
        m = model(data_t,param)
        #Now compute the probability of the model w.r.t. data
        for j in range(m.shape[0]): #This is a specific point for that model
            prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
        return prob
    y_data = Image2.voi_statistics_avg[i]
    e_data = Image2.voi_statistics_std[i]+1e0
    e_data[0:2] += max(Image2.voi_statistics_std[10])

    samplerDynesty = NestedSampler(loglike,prior_transform,ndim,logl_args=[t_data,y_data,e_data],ptform_args=[param_init],nlive=1500)
    samplerDynesty.run_nested(maxiter=1e5)
    results = samplerDynesty.results

    fig,axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=labels,title_fmt=".4f")

    param1 = axes[0,1].title.get_text()
    param2 = axes[1,1].title.get_text()
    param3 = axes[2,1].title.get_text()

    param1_min = float(param1[param1.find("-")+1:param1.find("^")-1])
    param1_max = float(param1[param1.find("+")+1:param1.find("}$")])
    param2_min = float(param2[param2.find("-")+1:param2.find("^")-1])
    param2_max = float(param2[param2.find("+")+1:param2.find("}$")])
    param3_min = float(param3[param3.find("-")+1:param3.find("^")-1])
    param3_max = float(param3[param3.find("+")+1:param3.find("}$")])

    dyn_opt[i,:] = results.samples[-1,:]
    dyn_min[i,:] = np.array([param1_min,param2_min,param3_min])
    dyn_max[i,:] = np.array([param1_max,param2_max,param3_max])


fig11,axs = plt.subplots(3,sharex=True)

axs[0].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,0],yerr=[est_opt[:,0]-est_min[:,0],est_max[:,0]-est_opt[:,0]],label="Brute")
axs[0].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,0],yerr=[dyn_min[:,0],dyn_max[:,0]],label='Dynesty')
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid();axs[0].legend()

axs[1].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,1],yerr=[est_opt[:,1]-est_min[:,1],est_max[:,1]-est_opt[:,1]],label="Brute")
axs[1].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,1],yerr=[dyn_min[:,1],dyn_max[:,1]],label='Dynesty')
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid();axs[1].legend()

axs[2].errorbar(np.arange(len(Image2.voi_statistics_avg)),est_opt[:,2],yerr=[est_opt[:,2]-est_min[:,2],est_max[:,2]-est_opt[:,2]],label="Brute")
axs[2].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,2],yerr=[dyn_min[:,2],dyn_max[:,2]],label='Dynesty')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid();axs[2].legend()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig11.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig11.suptitle('Estimated Parameters with Dynesty and Brute Force')
########
fig12,axs = plt.subplots(3,sharex=True)

axs[0].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,0],yerr=[dyn_min[:,0],dyn_max[:,0]],label='Dynesty')
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid();axs[0].legend()

axs[1].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,1],yerr=[dyn_min[:,1],dyn_max[:,1]],label='Dynesty')
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid();axs[1].legend()

axs[2].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,2],yerr=[dyn_min[:,2],dyn_max[:,2]],label='Dynesty')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid();axs[2].legend()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig12.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig12.suptitle('Estimated Parameters with Dynesty')
########

#fig9.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/Coefficients_{name}_{seg_method[seg]}{comp}_Brute.png")
#fig11.savefig(f"/Volumes/Backup_Stuff/Python/Results/{name}/Coefficients_{name}_{seg_method[seg]}{comp}_Dynesty_Brute.png")
fig9.savefig(f"/Users/philippelaporte/Desktop/Programmation/Python/Data/Result_1.png")
fig11.savefig(f"/Users/philippelaporte/Desktop/Programmation/Python/Data/Result_2.png")
fig12.savefig(f"/Users/philippelaporte/Desktop/Programmation/Python/Data/Result_3.png")
#plt.close('all')
#####################################
#Dynesty Parameters Estimation (avg)#
#####################################
t_data = np.arange(len(Image2.voi_statistics_avg))
param_estim_avg = np.zeros(ndim)
param_estim_std = np.zeros((ndim,2))
for i in range(ndim):
    y_data = est_opt[:,i]
    e_data = dyn_min[:,i]
    param_init = np.array([0,1e4])
    def model(t,param):
        '''
        Param is [A]
        '''
        return np.ones_like(t)*param
    def prior_transform(param_unif_0_1,param_limit):
        param = param_unif_0_1*(param_limit[1]-param_limit[0])+param_limit[0]
        return param
    def loglike(param,data_t,data_f,data_e):
        prob = 0
        #First compute the model with the parameters
        m = model(data_t,param)
        #Now compute the probability of the model w.r.t. data
        for j in range(m.shape[0]): #This is a specific point for that model
            prob += np.log(2*np.pi*data_e[j])/2-((m[j]-data_f[j])/data_e[j])**2
        return prob
    samplerDynesty = NestedSampler(loglike,prior_transform,ndim=1,logl_args=[t_data,y_data,e_data],ptform_args=[param_init],nlive=1500)
    samplerDynesty.run_nested(maxiter=1e5)
    results = samplerDynesty.results

    fig,axes = dyplot.traceplot(results, show_titles=True,trace_cmap='viridis', connect=True,connect_highlight=range(5),labels=[labels[i]],title_fmt=".4f")
    print(axes)
    print(axes[0])
    print(axes[0].title.get_text())
    print(param1)
    param1 = axes[0].title.get_text()
    param1_min = float(param1[param1.find("-")+1:param1.find("^")-1])
    param1_max = float(param1[param1.find("+")+1:param1.find("}$")])

    param_estim_avg[i] = results.samples[-1,:]
    param_estim_std[i,:] = [param1_min,param1_max]

print(f"Values found: {param_estim_avg}")
print(f"Errors found: {param_estim_std}")

fig13,axs = plt.subplots(3,sharex=True)

axs[0].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,0],yerr=[dyn_min[:,0],dyn_max[:,0]],label='Dynesty',color='r')
axs[0].axhline(y=param_estim_avg[0],color='b');axs[0].axhline(y=param_estim_avg[0]-param_estim_std[0,0],color='b');axs[0].axhline(y=param_estim_avg[0]+param_estim_std[0,1],color='b')
axs[0].set_title(r"$Q_0 \left(\frac{\gamma_{12}}{\gamma_{23} V_1 - \gamma_{12} V_2}\right)$");axs[0].grid();axs[0].legend()

axs[1].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,1],yerr=[dyn_min[:,1],dyn_max[:,1]],label='Dynesty',color='r')
axs[1].axhline(y=param_estim_avg[1],color='b');axs[1].axhline(y=param_estim_avg[1]-param_estim_std[1,0],color='b');axs[1].axhline(y=param_estim_avg[1]+param_estim_std[1,1],color='b')
axs[1].set_title(r"$\gamma_{12}$");axs[1].grid();axs[1].legend()

axs[2].errorbar(np.arange(len(Image2.voi_statistics_avg)),dyn_opt[:,2],yerr=[dyn_min[:,2],dyn_max[:,2]],label='Dynesty',color='r')
axs[2].axhline(y=param_estim_avg[2],color='b');axs[2].axhline(y=param_estim_avg[2]-param_estim_std[2,0],color='b');axs[2].axhline(y=param_estim_avg[2]+param_estim_std[2,1],color='b')
axs[2].set_title(r"$\gamma_{23}$");axs[2].grid();axs[2].legend()

plt.xlabel("Segmentation of Reference")#;plt.ylabel("Estimated Parameter")
fig13.text(0.05,0.5, "Estimated Parameter", ha="center", va="center", rotation=90)
fig13.suptitle('Estimated Parameters with Dynesty')
fig13.savefig(f"/Users/philippelaporte/Desktop/Programmation/Python/Data/Result_4.png")
########
print(f"Program ran until the end in {(time.time()-initial):.2f},' s at {time.strftime('%H:%M:%S')}")
plt.show()