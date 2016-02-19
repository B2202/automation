# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 14:07:23 2016

@author: Kellerkind
"""

from measurement_test import measure
import numpy as np
import time

m=measure('.','ps_test_log')
m.start_logging()

rates=np.array([0.01,0.005,0.001,0.0005])

for i in np.arange(len(rates)):
    print 'run: ',i
    B=0.001*(-1)**i
    time1=time.time()
    m.hps.sweep_field(B,rates[i])
    time2=time.time()
    m.wait('hps',5)
    print "rate= ", rates[i], "actual rate= ", 60*0.002/(time2-time1), "ratio= ", rates[i]*(time2-time1)/(60*0.002)
    
for i in np.arange(len(rates)):
    print 'run: ',i
    B=0.001*(-1)**i
    time1=time.time()
    m.vps.sweep_field(B,rates[i])
    time2=time.time()
    m.wait('vps',5)
    print "rate= ", rates[i], "actual rate= ", 60*0.002/(time2-time1), "ratio= ", rates[i]*(time2-time1)/(60*0.002)
    
    
m.finish()