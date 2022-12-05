import numpy as np
import math

def rayleigh_noise_pdf(value:float = 0,a:float = 0.0,b:float = 1.0,type:str = "icdf") -> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    Rayleigh noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- first parameter for the Rayleigh noise distribution, its lowest value (default 0)\n
    b -- second parameter for the Rayleigh noise distribution, its spread (default 0)\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= a, (2/b)*(value - a) * np.exp(-(value-a)**2/b), 0)
    elif type == "cdf":
        return np.where(value >= a, 1 - np.exp(-(value-a)**2/b), 0)
    elif type == "mu":
        return a + np.sqrt(np.pi * b/4)
    elif type == "sigma":
        return np.sqrt(b*(4-np.pi)/4)
    else: #This is the icdf
        return (-b * np.log(1 - value + 1e-10))**(1/2)+a

def Erlang_noise_pdf(value:float = 0, a:float = 1.0, b:float = 1, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    Erlang (Gamma) noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- first parameter for the Erlang noise distribution\n
    b -- second parameter for the Erlang noise distribution\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= 0, a**b*value**(b-1)*np.exp(-a*value)/math.factorial(b-1), 0)
    elif type == "cdf":
        return np.zeros_like(value)
    elif type == "mu":
        return b/a
    elif type == "sigma":
        return np.sqrt(b)/a
    else: #This is the cdf
        return np.zeros_like(value)

def exponential_noise_pdf(value:float=0, a:float = 1.0, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    exponential noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function\n
    a -- parameter for the exponential noise distribution\n
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where(value >= 0, a*np.exp(-a*value), 0)
    elif type == "cdf":
        return 1 - np.exp(-a*value)
    elif type == "mu":
        return 1/a
    elif type == "sigma":
        return 1/a
    else: #This is the cdf
        return -np.log(1 - value + 1e-10)/a

def uniform_noise_pdf(value:float=0, a:float = 0.0,b:float = 1.0, type:str = "icdf")-> float:
    """
    Probability Density Function (pdf), Cumulative Density Function (cdf) and inverse cdf for the 
    exponential noise.\n
    Keyword arguments:\n
    value -- values for which to compute the function (default 0)\n
    a -- first parameter for the uniform noise distribution, its minimum (default 0)\n
    b -- second parameter for the uniform noise distribution, its maximum (default 1)\n 
    type -- type of function to use: pdf, cdf or icdf (default "icdf")         
    """
    if type == "pdf":
        return np.where((value >= a) & (value <= b), 1/(b-a), 0)
    elif type == "cdf":
        tmp = np.where(value >= a, (value - a)*(b-a), 0)
        return np.where(value <= b, tmp, 1)
    elif type == "mu":
        return (a+b)/2
    elif type == "sigma":
        return (b-a)/np.sqrt(12)
    else: #This is the cdf
        return value/(b-a) + a