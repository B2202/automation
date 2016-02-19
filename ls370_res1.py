# -*- coding: utf-8 -*-
"""
Created on Mon Feb 08 11:56:32 2016

@author: Kellerkind
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import visa
from ls370_driver import ls370
import time
import numpy as np
from matplotlib import pyplot as plt




sleep_time=10
start_time=time.time()


result=np.zeros((1,2))
result1=np.zeros((1,2))

ls=ls370(13)


while True:
 
    time.sleep(1)
    result1[0,0]=time.time()-start_time
    result1[0,1]=ls.get_res(10)
    print result1[0,1]
    
    result=np.append(result,result1,axis=0)
    np.savetxt('r_therm_holder.dat',result)

