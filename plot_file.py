import time
import numpy as np
from matplotlib import pyplot as plt

plt.ion()
fig=plt.figure()
ax1=fig.add_subplot(111)


#ax.plot(result[:,0]-np.min(result[:,0]),np.abs(result[:,1]))
plt.show()



while True:
    try:
        result=np.loadtxt('lockin_therm_holder4.dat')
    except:
        print 'loading collision'

    ax1.clear()
#    ax1.set_autoscaley_on(False)
#    ax1.set_ylim([0,0.00001])
    ax1.plot(result[:,0],np.abs(result[:,5]))
    plt.draw()
    time.sleep(2)
    