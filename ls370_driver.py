import visa
import time
import numpy as np
from matplotlib import pyplot as plt

a=0
class ls370():
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

    def get_temp(self,channel):
        """
        return the temperature as determined by the lakeshore from channel in kelvin
        """
        global a
        try:
            raw_output=self._device.query('RDGK?'+str(channel))
            out=float(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read Temperature"
            return NaN

    def get_res(self,channel):
        """
        return the resistance in ohmes
        """

        global a
        try:
            raw_output=self._device.query('RDGR?'+str(channel))
            out=float(raw_output[0:len(raw_output)-1])
            return out
        except:
            print "Failed to read Resistance"
            return NaN

    def get_htrrng(self):
        """
        return the heater range in amps and the heater range index
        """


        htrranges={0: 0, 1: 31.6e-6, 2: 100e-6, 3: 316e-6, 4: 1e-3, 5: 3.16e-3, 6: 1e-2, 7: 3.16e-2, 8: 0.1}        

        global a
        range=-1
        try:
            range=self._device.query('HTRRNG?')
            
            if int(range) in htrranges:            
                range1=htrranges[int(range)]
            
            return range1,range

        except:
            a=a

    def set_htrrng(self,htrrange):
        """
        return the heater range in amps and the heater range index
        """

        htrranges={0: 0, 31.6e-6 : 1, 100e-6 : 2, 316e-6 : 3, 1e-3 : 4, 3.16e-3 : 5, 1e-2 : 6, 3.16e-2 : 7, 0.1 : 8 }

        global a

        if htrrange in htrranges:
            index=htrranges[htrrange]
        elif htrrange>-1 and htrrange<9 and htrrange.is_integer():
            index=int(htrrange)
        else:
            return -1

        try:
            raw_range=self._device.write('HTRRNG '+str(index))
            return 0

        except:
            a=a


    def increase_htrrange(self):
        """
        increases htrrange, returns new heater range and index
        """

        htrranges={0: 0, 31.6e-6 : 1, 100e-6 : 2, 316e-6 : 3, 1e-3 : 4, 3.16e-3 : 5, 1e-2 : 6, 3.16e-2 : 7, 0.1 : 8 }

        try:
            range1, range=self.get_htrrng()
            if range<8:
                blub=set_htrrange(range+1)
                return htrranges[range+1], range+1
            else:
                print "Tried to increase heater range, but already at maximum!"
                return None
        except:
            print "Increasing heater range fucked up"



    def decrease_htrrange(self):
        """
        increases htrrange, returns new heater range and index
        """

        htrranges={0: 0, 31.6e-6 : 1, 100e-6 : 2, 316e-6 : 3, 1e-3 : 4, 3.16e-3 : 5, 1e-2 : 6, 3.16e-2 : 7, 0.1 : 8 }

        try:
            range1, range=self.get_htrrng()
            if range>1:
                blub=set_htrrange(range-1)
                return htrranges[range-1], range-1
            else:
                print "Tried to increase heater range, but already at minimum! If you want to turn it off, do that manually!"
                return Null
        except:
            print "decreasing heater range fucked up"


    def htr_off(self):
        """
        turns heater off
        """
        try:
            blub=set_htrrange(0)
            return 0
        except:
            print "Turning heater off didn't work"
            return Null




    def get_heater(self):
        """
        return heater power / current
        """

        global a
        try:
            raw_output=self._device.query('HTR?')
            out=float(raw_output[0:len(raw_output)-1])
            range1, range=self.get_htrrng()

            return out*range1, out/100
        except:
            print "Failed to read Heater"
            return Null

    def get_res_ranges(self, channel):
        """
        returns controlmode (0=voltage or 1=current), excitation, resistance range, whether the system is in autorange mode (0=off, 1=on) and
        whether excitation is on (0=on, 1=off) anyway
        """

        global a
        try:
            raw_output=self._device.query('RDGRNG? ' + str(channel))
            out=raw_output[0:len(raw_output)-1].split(',')
            mode=out[0]
            exc=out[1]
            range=out[2]
            autorange=out[3]
            exc_off=out[4]


            return mode,exc,range,autorange,exc_off
        except:
            print "Failed to read resistance range"
            return Null, Null,Null,Null,Null

    def set_res_range_auto(self, channel, bool):
        """
        set the resistance range to auto (True or False)
        """
        global a
        try:
            raw_output=self._device.query('RDGRNG?')
            out=raw_output[0:len(raw_output)-1].split(',')
            mode=out[0]
            exc=out[1]
            range=out[2]
            autorange=out[3]
            exc_off=out[4]

            if bool:
                raw=self._device.write('RDGRNG '+ str(channel) + ',' + mode + ','+exc + ','+range + ',1,'+exc_off)
            else:
                raw=self._device.write('RDGRNG '+ str(channel) + ',' + mode + ','+exc + ','+range + ',0,'+exc_off)
            return 0
        
        except:
            print "Failed to set autorange"
            return Null

    def set_exc_off(self, channel, bool):
        """
        turn excitation on or off (True or False)
        """
        global a
        try:
            raw_output=self._device.query('RDGRNG? '+ str(channel))
            out=raw_output[0:len(raw_output)-1].split(',')
            mode=out[0]
            exc=out[1]
            range=out[2]
            autorange=out[3]
            exc_off=out[4]

            if bool:
                raw=self._device.write('RDGRNG ' + str(channel) + ',' + mode + ','+exc + ','+range + ','+autorange+',0')
            else:
                raw=self._device.write('RDGRNG '+ str(channel) + ',' + mode + ','+exc + ','+range + ','+autorange+',1')
            return 0
        
        except:
            print "Failed to turn excitation on / off"
            return Null



    def get_channel(self):
        """
        get the channel (int, 1-16) and whether autoscan is on 
        """

        global a
        try:
            raw_output=self._device.query('SCAN?')
            out=raw_output[0:len(raw_output)-1].split(',')
            channel=out[0]
            auto=out[1]


            return channel,auto
        except:
            print "Failed to read Heater"
            return Null, Null



    def set_channel(self,channel):
        """
        Set the channel (int, 1-16)
        """
        channel1,auto=self.get_channel()

        try:        
            if auto==0:
                raw=self._device.write('SCAN ' + str(channel) + ',0')
            else:
                raw=self._device.write('SCAN ' + str(channel) + ',1')

        except:
            print "Failed to change channel"
            return Null




    def set_temp(self, T,channel):
        """
        set the Temperature T for channel 
        """

        global a
        try:
            range1,range=self.get_htrrng()
            cset_str='CSET '+str(channel)+',1,1,1,1,'+str(range)+',100'
            raw_output=self._device.write(cset_str)
 
            ramp_str='RAMP 0,1'
            raw_output=self._device.write(ramp_str)

            setp_str='SETP '+str(T)
            raw_output=self._device.write(setp_str)
            return T

        except:
            a=a
            return Null



    def ramp_temp(self,T,rate,channel):
        """
        Ramp the temperature to setpoint T (Kelvin) with rate (K/min), determined by channel 
        """

        global a
        try:
            range1,range=self.get_htrrng()
            cset_str='CSET '+str(channel)+',1,1,1,1,'+str(range)+',100'
            raw_output=self._device.write(cset_str)
 
            ramp_str='RAMP 1,'+str(rate)
            raw_output=self._device.write(ramp_str)

            setp_str='SETP '+str(T)
            raw_output=self._device.write(setp_str)
            return T

        except:
            a=a
            return Null

            
