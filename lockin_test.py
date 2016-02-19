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
from egg7265_driver import egg7265
import time
import numpy as np
from matplotlib import pyplot as plt




sleep_time=10


start_time=time.time()
result=np.zeros((1,6))
result1=np.zeros((1,6))

lockin1=egg7265(12)
lockin2=egg7265(14)

while True:

    dummy1=lockin1.get_xy()
    dummy2=lockin2.get_xy()
    
    result1[0,0]=time.time()-start_time
    result1[0,1]=dummy1[0]
    result1[0,2]=dummy1[1]
    result1[0,3]=dummy2[0]*np.sqrt(2)
    result1[0,4]=dummy2[1]*np.sqrt(2)
    result1[0,5]=100*result1[0,1]/(result1[0,3])

    print result1[0,5]
 
    result=np.append(result,result1,axis=0)
    np.savetxt('lockin_therm_holder4.dat',result)
    time.sleep(1)

