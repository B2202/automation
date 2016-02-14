import visa
import numpy as np
import time

#addresse=4
#l_wait=300
#s_wait=15

#check=0
a=0

class lm500():
    def __init__(self,adress):
        rm=visa.ResourceManager()
        liste=rm.list_resources()
        j=0
        for i in np.arange(len(liste)):
            if liste[i].find('::'+str(adress)+'::')>-1:
                print "Device found on ", liste[i]
                self._device=rm.open_resource(liste[i])
                j=i
        print "Successfully opened Device " + liste[j]
        print self._device.query('*IDN?')

    def read(self):
        global a
        
        try:
            raw_output=self._device.query('MEAS?')
            level=float(raw_output[0:len(raw_output)-4])
            return level    
        except:
            print "Could not read device lm500"
            return -1

    def measure(self):
        global a
        try:
            raw_output=self._device.query('MEAS')
        except:
            a=a
        
        try:
            raw_output=self._device.query('MEAS?')
            level=float(raw_output[0:len(raw_output)-4])
            return level    
        except:
            print "Could not read device lm500"
            return -1


