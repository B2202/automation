import visa
import time
import numpy as np
import threading


a=0

fcr=0.03499            # field current ratio in T/A, Imax=11.44A

max_sr_low=0.144      # max sweep rate up to 50A / 3T 
max_sr_high=0.072     # max sweep rate up to 68.43A / 4T

wait_before_on=10
wait_after_on=10
wait_before_off=20
wait_after_off=10

curr_sweep_tol=0.0002           # maximum difference between ps_curr and
                                # ulim or llim to be considered equal
output_tolerance=0.0001         #  maximum difference between ps_curr and mag_curr
                                # to open pshtr

class model4g():
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
        time.sleep(2)
 
        try:
            
            b=self._device.query('*IDN?')
            print b
        except:
            print 'some issues...'

        time.sleep(1)
        try:
            b=self._device.write('UNITS G')
            self.llim=self.get_llim()
            self.ulim=self.get_ulim()
        except:
            print 'set units in tesla fucked up?'
            print self._device.query('UNITS?')
        self.target=0
        self.set_range(0,4)
        self.watch_thread_killer=threading.Event()
        self.watch_thread_killer.clear()
 
        self.watch_thread=threading.Thread(target=self.watch_status)

        self.watch_thread.start()

        
    def kill_watch_status(self):
        self.watch_thread_killer.set()
        
    def watch_status(self):
#        self.last_ps_curr=self.get_ps_curr()
        while not self.watch_thread_killer.is_set():
            helper=self.get_switch_htr()

            self.ps_curr_1=self.get_ps_curr()
            if isinstance(self.ps_curr_1,(float,)):
                self.ps_curr=self.ps_curr_1

            self.mag_curr_1=self.get_mag_curr()
            if isinstance(self.mag_curr_1,(float,)):
                self.mag_curr=self.mag_curr_1

            if isinstance(helper,(bool,)):
                if helper:
                    self.pshtr_open=True
                else:
                    self.pshtr_open=False
            
            if abs(self.ps_curr-self.target)<curr_sweep_tol or \
            self.get_sweep()==0:
                self.curr_sweep=False
            else:
                self.curr_sweep=True

#            print 'target = ', self.target, self.curr_sweep
            
            if self.curr_sweep and self.pshtr_open:
                self.mag_sweep=True
            else:
                self.mag_sweep=False
                
            time.sleep(1)

####################################################################
###        get methods


    def get_mag_curr(self):

        try:
            raw_output=self._device.query('IMAG?')
            out=float(raw_output[0:len(raw_output)-3])/10
            return out
        except:
            print '4G: Weird reply to IMAG? Query!'
            return None

    def get_ps_curr(self):

        try:
            raw_output=self._device.query('IOUT?')
            out=float(raw_output[0:len(raw_output)-3])/10
            return out
        except:
            print '4G: Weird reply to IOUT? Query!'
            return None

    def get_switch_htr(self):
        raw_output='get_switch_htr_dummy'
        try:
            raw_output=self._device.query('PSHTR?')
            time.sleep(0.2)
#            print 'pshtr', raw_output
            out=float(raw_output)
            if out==0:
                return False
            elif out==1:
                return True
            else:
                print '4G: Weird reply to PSHTR Query!', raw_output
                return None
        except:
            print '4G exception: Weird reply to PSHTR? Query!'
            return None

    def get_sweep(self):
        try:
            raw_output=self._device.query('SWEEP?')
            time.sleep(0.2)
            out=raw_output
            if out.find('up')>-1:
                return 'UP'
            elif out.find('down')>-1:
                return 'DOWN'
            elif out.find('zero')>-1:
                return 'ZERO'
            elif out.find('Standby')>-1 or out.find('pause')>-1:
                return '0'

            else:
                print '4G: Weird reply to SWEEP Query!', raw_output
                return None
        except:
            print '4G exception: Weird reply to SWEEP? Query!'
            return None        

    def get_llim(self):
        try:
            raw_output=self._device.query('LLIM?')
            out=float(raw_output[0:len(raw_output)-3])/10
            return out
        except:
            print '4G: Weird reply to %s Query!' % 'LLIM?'
            return None        

    def get_ulim(self):
        try:
            raw_output=self._device.query('ULIM?')
            out=float(raw_output[0:len(raw_output)-3])/10
            return out
        except:
            print '4G: Weird reply to %s Query!' % 'LLIM?'
            return None        



####################################################################
###        set methods

    def set_llim(self, field):
        self.llim=field
        field=field*10                  # kG instead of T
        try:
            llim_string='LLIM ' + str(field)+'\n'
            self._device.write(llim_string)
        except:
            print '4G: Weird reply to %s Query!' % (llim_string)
            return None

    def set_ulim(self, field):
        self.ulim=field
        field=field*10                  # kG instead of T
        try:
            ulim_string='ULIM ' + str(field)+'\n'
            self._device.write(ulim_string)
        except:
            print '4G: Weird reply to %s Query!' % (ulim_string)
            return None

    def set_range(self, number, limit):
        limit=limit/fcr
        try:
            range_string='RANGE ' + str(number)+' '+str(limit)+'\n'
            self._device.write(range_string)
        except:
            print '4G: Weird reply to %s Query!' % (range_string)
            return None            

    def set_rate(self, number, rate):
        """
        rate in T/min!! NOTE: if the UNITS of the powersupply are in kG / G the 
        rate passed to the PS is kG/s NOT as stated in the manual A/s
        """
        rate=rate*100
#        rate=rate/(fcr*60)
        try:
            rate_string='RATE ' + str(number)+' '+str(rate)+'\n'
            self._device.write(rate_string)
        except:
            print '4G: Weird reply to %s Query!' % (rate_string)
            return None     

    def sweep(self,direction, rate):
        
        if direction=='UP':
            self.target=self.ulim
            print "Set new target from ulim: ", self.target
        elif direction=='DOWN':
            self.target=self.llim
            print "Set new target from llim: ", self.target

        
        if rate=='FAST':
            sweep_string='SWEEP '+direction+' FAST'
        else:
            sweep_string='SWEEP '+direction

        try:
            self._device.write(sweep_string)
        except:
            print '4G: Weird reply to %s Query!' % (sweep_string)
            return None     

    def set_switch_htr(self, switch):
        if switch:
            switch_string='PSHTR ON'
        elif not switch:
            switch_string='PSHTR OFF'

        try:
            self._device.write(switch_string)
        except:
            print '4G: Weird reply to %s Query!' % (switch_string)
            return None     
        

    def adjust_current(self):
        if self.mag_curr>self.ps_curr and self.pshtr_open==False:
            self.set_ulim(self.mag_curr)
            self.sweep('UP', 'FAST')
        elif self.mag_curr<self.ps_curr and self.pshtr_open==False:
            self.set_llim(self.mag_curr)
            self.sweep('DOWN', 'FAST')
        
        time.sleep(2)
        while self.curr_sweep:
            time.sleep(2)
        print 'Current adjusted'

    def zero_current(self):
        if self.pshtr_open:
            self._device.write('SWEEP ZERO')
        else:
            self._device.write('SWEEP ZERO FAST')
            

    def set_persistent():
        if self.pshtr_open==True:
            time.sleep(wait_before_off)
            while self.pshtr_open==True:
                self.set_switch_htr(False)
                time.sleep(1)
            time.sleep(wait_after_off)
            self.zero_current()
            while self.surr_sweep==True:
                time.sleep(2)

    def sweep_field_watch(self,driven):
        print 'entered sweep_field_watch', self.curr_sweep
        time.sleep(10)
        while self.curr_sweep :
            time.sleep(2)
        
        if driven==False:
            self.set_persistent()

    def sweep_field(self, target, rate, driven=False):
        if not self.pshtr_open:
            self.adjust_current()
            print 'Wait before on'
            time.sleep(wait_before_on)
                
            if np.abs(self.mag_curr-self.ps_curr)< output_tolerance:
                while not self.pshtr_open:
                    self.set_switch_htr(True)
                    print "Tried to open switch heater"
                    time.sleep(1)
            else:
                print "Else bit, recall myself"
                self.sweep_field(target,rate)
                return 0
            
#            if not self.pshtr_open:
#                self.sweep_field(target,rate)
#                return 0
        print 'Wait after on'
        time.sleep(wait_after_on)
        
        self.set_rate(0,rate)        
        if self.get_mag_curr()<target:
            self.set_ulim(target)
            self.sweep('UP',rate)
        else:
            self.set_llim(target)
            self.sweep('DOWN',rate)
        
        sweep_thread=threading.Thread(target=self.sweep_field_watch, args=(driven,))
        sweep_thread.setDaemon(True)
        sweep_thread.start()
        