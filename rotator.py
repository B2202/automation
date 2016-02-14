import visa
import time
import numpy as np
import threading

baudrate=19200
databit=8


class rotator():
    def __init__(self,adress):
        rm=visa.ResourceManager()
        liste=rm.list_resources()
        j=0
        for i in np.arange(len(liste)):
            if liste[i].find('ASRL'+str(adress)+'::')>-1:
                print "Device found on ", liste[i]
                self._device=rm.open_resource(liste[i])
                j=i
        print "Successfully opened device " + liste[j]
        
        self._device.baud_rate=baudrate
        self._device.data_bits=databit
#        self._device.clear()
    
    def get_angle(self):
        try:
            raw_output=self._device.query('UF[10]')
            return_index=raw_output.find('\r')
            end_index=raw_output[return_index:].find(';')
            output=float(raw_output[return_index+1:return_index+end_index])
            return output
        except:
            print 'Rotator: get_angle: Something fucked up. device.clear()'
#            self._device.clear()
            return None
        
    def rotate(self,target, speed):
        switch=False
        if speed >200 or speed<0:
            print 'Please insert speed between 0 and 200deg/h'
            return None
        try:
            rotate_string='UF[1]='+str(target)+';UF[2]='+str(speed)+';UI[1]=2'
            self._device.write(rotate_string)
            time.sleep(5)
            while not switch:
                helper=self.get_status()
                if isinstance(helper,(bool,)):
                    if helper:
                        switch=False
                    elif not helper:
                        if self.get_status()==False:
                            switch=True
                time.sleep(5)
            return 0
        except:
            print 'Rotator: rotate: Something fucked up. device.clear()'
#            self._device.clear()
            return None
            
    def get_status(self):
        try:
            raw_output=self._device.query('UI[1]')
            return_index=raw_output.find('\r')
            end_index=raw_output[return_index:].find(';')
            output=float(raw_output[return_index+1:return_index+end_index])
            if output==-1:
                return True
            elif output==-2:
                return False
            else:
                print 'Rotator: read_status: Weird reply'
                return None
            
        except:
            print 'Rotator: read_status: Something fucked up. device.clear()'
#            self._device.clear()
            return None            