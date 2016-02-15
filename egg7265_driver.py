import visa
import time
import numpy as np
from matplotlib import pyplot as plt

a=0
class egg7265():
    def __init__(self,adress):
        rm=visa.ResourceManager()
        liste=rm.list_resources()
        j=0
        for i in np.arange(len(liste)):
            if liste[i].find('::'+str(adress)+'::')>-1:
                print "Device found on ", liste[i]
                self._device=rm.open_resource(liste[i])
                j=i
        print "Successfully opened device " + liste[j]
        print self._device.query('*IDN?')

    def read_adc1(self):
        global a
        try:
            raw_output=self._device.query('ADC1')
            out=float(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read ADC1"
            return None
        

    def read_adc2(self):
        global a
        try:
            raw_output=self._device.query('ADC2')
            out=float(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read ADC2"
            return None

    def get_xy(self):
        global a
        try:
            raw_output=self._device.query('XY.')
            index=raw_output.find(',')
            x=float(raw_output[0:index])
            y=float(raw_output[index+1:len(raw_output)-2])

            return x,y
        except:
            print "Failed to read XY"
            a=a
            return None, None



    def set_sensitivity(self,sens):
        """
        Supports 2nV, 5nV, 10nV, 20nV, 50nV,....500mV, 1V Sensitivity. To be passed
        as string like '10mV'
        """
        global a

        sensitivities={'2nV' : 1, '5nV' : 2, '10nV' : 3, '20nV' : 4, '50nV' : 5, '100nV' : 6, '200nV' : 7, '500nV' : 8, '1uV' : 9, '2uV' : 10}
        sensitivities.update({'5uV' : 11, '10uV' : 12, '20uV' : 13, '50uV' : 14, '100uV' : 15, '200uV' : 16, '500uV' : 17, '1mV' : 18})
        sensitivities.update({'2mV' : 19, '5mV' : 20, '10mV' : 21, '20mV' : 22, '50mV' : 23, '100mV' : 24, '200mV' : 25, '500mV' : 26, '1V' : 27})

        if sens in sensitivities:
            sensn=sensitivities[sens]
        elif isinstance(sens, int):
            if 0>sens or 28<sens:
                print 'Failed to set new sensitivity, I dont know ', sens
                return None
            else:
                sensn=sens
        else:
            print 'Failed to set new sensitivity, I dont know ', sens
            return None

        try:
            raw_output=self._device.write('Sen '+str(sensn))
            return sensn
        except:
            print 'setting sensitivity somehow failed'
            return None    

    def increase_sensitivity(self):
        
        try:
            sens=self.read_sensitivity()
            if sens<27:
                dummy=self.set_sensitivity(sens+1)
                return sens+1
            else:
                print 'Tried to increase sensitivity, but was already maxed'        
                return None
        except:
            print 'Increasing sensitivity failed'
            return None

    def decrease_sensitivity(self):

        try:
            sens=self.read_sensitivity()
            if sens>1:
                dummy=self.set_sensitivity(sens-1)
                return sens-1
            else:
                print 'Tried to decrease sensitivity, but was already maxed'        
                return None
        except:
            print 'Decreasing sensitivity failed'
            return None


    def read_sensitivity(self):
        global a
        try:
            raw_output=self._device.query('SEN')
            out=int(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read Sensitivity"
            return NaN        

    def set_U(self,U):
        """
        This method sets the Oscillator Amplitude (float) in Volt
        """
        global a

        try:
            raw_output=self._device.write('OA. '+str(U))
        except:
#            print "Failed to set Oscillator Amplitude"
            a=a
        return a

    def set_f(self,f):
        """
        This method sets the Oscillator frequency (float) in Hertz.
        Note: The string passed to the Lockin includes the frequency in mHz!
        """

        global a

        try:
            raw_output=self._device.write('OF. '+str(f))
        except:
#            print "Failed to set Oscillator frequency"
            a=a
        return a


    def set_tc(self, tc):
        tcs={'10us': 0, '20us': 1, '40us': 2, '80us': 3, '160us': 4, '320us': 5, '640us': 6, '5ms': 7, '10ms': 8, '20ms': 9,  '50ms': 10}
        tcs.update({'100ms' : 11, '200ms' : 12, '500ms' : 13, '1s' : 14, '2s' : 15, '5s' : 16, '10s' : 17, '20s' : 18, '50s' : 19, '100s' : 20})
        tcs.update({'200s' : 21, '500s' : 22, '1ks' : 23, '2ks' : 24, '5ks' : 25, '10ks' : 26, '20ks' : 27, '50ks' : 28, '100ks' : 29})

        if tc in tcs:
            tcn=tcs[tc]
        elif tc.is_integer():
            if tc<0 or tc>29:
                print 'I dont know the timeconstant ', tc,' you want to set'
                return None
            else:
               tcn=tc
        else:
            print 'I dont know the timeconstant ', tc,' you want to set'

        try:
            raw_output=self._device.write('TC'+str(tcn))
            return tcn
        except:
            print 'setting time constant somehow failed'
            return None    

    def read_tc(self):
        global a
        try:
            raw_output=self._device.query('TC')
            out=int(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read TC"
            return NaN
               