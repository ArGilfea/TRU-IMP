import numpy as np

def rayleigh_noise_pdf(value:float,a:float = 0.0,b:float = 1.0,type:str = "icdf") -> float:
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
    else: #This is the icdf
        return (-b * np.log(1 - value + 1e-10))**(1/2)+a