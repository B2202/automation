import visa
import time
import numpy as np
import threading


a=0

fcr=0.0585            # field current ratio in T/A

max_sr_low=0.144      # max sweep rate up to 50A / 3T 
max_sr_high=0.072     # max sweep rate up to 68.43A / 4T

wait_before_on=20
wait_after_on=15
wait_before_off=20
wait_after_off=25

curr_sweep_tol=0.0002           # maximum difference between ps_curr and
                                # ulim or llim to be considered equal

output_tolerance=0.001


class cs4():
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
        # initialize attributes
        self.mag_field=0
        self.ps_field=0
        self.pshtr=False
        self.ulim=0
        self.llim=0
        self.rate=0
        self.target=0
        self.sweep_status=''
        self.command_queue=[]
        # just to make sure, set usually used range to full range
        self.set_range(0,4)

        self.mag_sweep=False                
        #make sure units are properly set
        try:
            b=self._device.write('UNITS G')
        except:
            print 'set units in gauss fucked up?'
            print self._device.query('UNITS?')


        #initialize threading stuff
        self.watch_thread_killer=threading.Event()
        self.watch_thread_killer.clear()
        self.watch_thread=threading.Thread(target=self.watch_status)
        self.watch_thread.start()

        self.time1=0
        self.time2=0
        
    def kill_watch_status(self):
        self.watch_thread_killer.set()
        
    def watch_status(self):
#        self.last_ps_curr=self.get_ps_field()
        my_time=time.time()
        while not self.watch_thread_killer.is_set():

            time.sleep(0.2)
            l=len(self.command_queue)
            if l>0:
                exec(self.command_queue.pop())
                time.sleep(0.1)
            else:
                time.sleep(0.1)

            if time.time()-my_time>1.5:
                self._get_mag_field()
                self._get_ps_field()
                self._get_switch_htr()
                self._get_sweep()
                my_time=time.time()

            if np.abs(self.ps_field-self.target)>curr_sweep_tol and self.pshtr:
                self.mag_sweep=True
            else:
                self.mag_sweep=False

 


####################################################################
###        get methods
####################################################################

    def p_get_mag_field(self):

        try:
            raw_output=self._device.query('IMAG?')
            out=float(raw_output[0:len(raw_output)-3])/10
            self.mag_field=out
            return None
        except:
            print 'CS4: Weird reply to IMAG? Query!'
            return None

    def _get_mag_field(self):
        self.command_queue.insert(0,'self.p_get_mag_field()')
        return None

    def get_mag_field(self):
        return self.mag_field


    def p_get_ps_field(self):

        try:
            raw_output=self._device.query('IOUT?')
            out=float(raw_output[0:len(raw_output)-3])/10
            self.ps_field=out
            return None
        except:
            print 'CS4: Weird reply to IOUT? Query!'
            return None

    def _get_ps_field(self):
        self.command_queue.insert(0,'self.p_get_ps_field()')
        return None

    def get_ps_field(self):
        return self.ps_field


    def p_get_switch_htr(self):
        raw_output='get_switch_htr_dummy'
        try:
            raw_output=self._device.query('PSHTR?')
            time.sleep(0.2)
#            print 'pshtr', raw_output
            out=float(raw_output)
            if out==0:
                self.pshtr=False
                return None
            elif out==1:
                self.pshtr=True
                return None
            else:
                print 'CS4: Weird reply to PSHTR Query!', raw_output
                return None
        except:
            print 'CS4 exception: Weird reply to PSHTR? Query!'
            return None

    def _get_switch_htr(self):
        self.command_queue.insert(0,'self.p_get_switch_htr()')
        return None

    def get_switch_htr(self):
        return self.pshtr


    def p_get_sweep(self):
        try:
            raw_output=self._device.query('SWEEP?')
            time.sleep(0.2)
            out=raw_output
            if out.find('up')>-1:
                self.sweep_status='UP'
                return None
            elif out.find('down')>-1:
                self.sweep_status='DOWN'
                return None
            elif out.find('zero')>-1:
                self.sweep_status='ZERO'
                return None
            elif out.find('Standby')>-1 or out.find('pause')>-1:
                self.sweep_status='0'
                return None

            else:
                print 'CS4: Weird reply to SWEEP Query!', raw_output
                return None
        except:
            print 'CS4 exception: Weird reply to SWEEP? Query!'
            return None        

    def _get_sweep(self):
        self.command_queue.insert(0,'self.p_get_sweep()')
        return None

    def get_sweep(self):
        return self.sweep_status


    def p_get_llim(self):
        try:
            raw_output=self._device.query('LLIM?')
            out=float(raw_output[0:len(raw_output)-3])/10
            self.llim=out
            return None
        except:
            print 'CS4: Weird reply to %s Query!' % 'LLIM?'
            return None        
    def _get_llim(self):
        self.command_queue.insert(0,'self.p_get_llim()')
        return None

    def get_llim(self):
        return self.llim
        

    def p_get_ulim(self):
        try:
            raw_output=self._device.query('ULIM?')
            out=float(raw_output[0:len(raw_output)-3])/10
            self.ulim=out
            return None
        except:
            print 'CS4: Weird reply to %s Query!' % 'LLIM?'
            return None        

    def _get_ulim(self):
        self.command_queue.insert(0,'self.p_get_ulim()')
        return None

    def get_ulim(self):
        return self.ulim

####################################################################
###        set methods

    def p_set_llim(self, field):
#        print "p_set_llim ", field
        self.llim=field
        field=field*10                  # kG instead of T
        try:
            llim_string='LLIM ' + str(field)+'\n'
            self._device.write(llim_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (llim_string)
            return None

    def set_llim(self, field):
        self.command_queue.insert(len(self.command_queue),'self.p_set_llim('+str(field)+')')
        return None


    def p_set_ulim(self, field):
#        print "p_set_ulim ", field
        self.ulim=field
        field=field*10                  # kG instead of T
        try:
            ulim_string='ULIM ' + str(field)+'\n'
            self._device.write(ulim_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (ulim_string)
            return None

    def set_ulim(self, field):
        self.command_queue.insert(len(self.command_queue),'self.p_set_ulim('+str(field)+')')
        return None



    def p_set_range(self, number, limit):
        limit=limit/fcr
        try:
            range_string='RANGE ' + str(number)+' '+str(limit)+'\n'
            self._device.write(range_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (range_string)
            return None            

    def set_range(self, number, limit):
        self.command_queue.insert(len(self.command_queue),'self.p_set_range('+str(number)+','+str(limit)+')')
        return None


    def p_set_rate(self, number, rate):
        """
        rate in T/min!! NOTE: if the UNITS of the powersupply are in kG / G the 
        rate passed to the PS is kG/s NOT as stated in the manual A/s
        """
        rate=rate
#        rate=rate/(fcr*60)
        try:
            rate_string='RATE ' + str(number)+' '+str(rate)+'\n'
            self._device.write(rate_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (rate_string)
            return None     

    def set_rate(self, number, rate):
        self.command_queue.insert(len(self.command_queue),'self.p_set_rate('+str(number)+','+str(rate)+')')
        return None

    def p_sweep(self,direction, rate):
#        print 'sweep direction, rate, ulim, llim' , direction, rate, self.ulim, self.llim
        
        if direction=='UP':
            self.target=self.ulim
#            print "Set new target from ulim: ", self.target, self.ulim
        elif direction=='DOWN':
            self.target=self.llim
#            print "Set new target from llim: ", self.target, self.llim

        
        if rate.find('FAST')>-1:
            sweep_string='SWEEP '+direction+' FAST'
        else:
            sweep_string='SWEEP '+direction

        try:
#            print "sweep string ", sweep_string 
            self._device.write(sweep_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (sweep_string)
            return None     

    def sweep(self, direction, rate):
#        print 'sweep ulim, llim', self.ulim, self.llim 
        self.command_queue.insert(len(self.command_queue),'self.p_sweep(\''+str(direction)+'\' , \''+str(rate)+'\')')
        return None


    def p_set_switch_htr(self, switch):
        if switch:
            switch_string='PSHTR ON'
        elif not switch:
            switch_string='PSHTR OFF'

        try:
            self._device.write(switch_string)
        except:
            print 'CS4: Weird reply to %s Query!' % (switch_string)
            return None     
        
    def set_switch_htr(self, switch):
        self.command_queue.insert(len(self.command_queue),'self.p_set_switch_htr('+str(switch)+')')
        return None

    def p_zero_current(self):
        print 'zero Current'
        if self.pshtr:
            self._device.write('SWEEP ZERO')
        else:
            self._device.write('SWEEP ZERO FAST')

    def zero_current(self):
        self.command_queue.insert(len(self.command_queue),'self.p_zero_current()')
        return None




    ################################################
    ##      Higher level methods
    ################################################


    def adjust_current(self):
        if self.mag_field>self.ps_field and self.pshtr==False:
            self.set_ulim(self.mag_field)
            time.sleep(1)
            self.sweep('UP', 'FAST')
        elif self.mag_field<self.ps_field and self.pshtr==False:
            self.set_llim(self.mag_field)
            time.sleep(1)
            self.sweep('DOWN', 'FAST')
        
        time.sleep(2)
        while self.mag_sweep:
            time.sleep(2)
        print 'Current adjusted'


    def set_persistent(self):
        if self.pshtr==True:
            self.time2=time.time()
            print "sweep duration", self.time2-self.time1
            print "CS4: Wait before OFF"
            time.sleep(wait_before_off)
            while self.pshtr==True:
                self.set_switch_htr(False)
                time.sleep(1)
            print "CS4: Wait after OFF"
            time.sleep(wait_after_off)
            self.zero_current()
            while self.mag_sweep==True:
                time.sleep(2)

    def sweep_field_watch(self,driven):
#        print 'CS4: entered sweep_field_watch', self.mag_sweep
        time.sleep(10)
        while self.mag_sweep :
            time.sleep(2)
        
        if driven==False:
            self.set_persistent()

    def sweep_field(self, target, rate, driven=False):
        if not self.pshtr:
            self.adjust_current()
            print 'CS4: Wait before ON'
            time.sleep(wait_before_on)
                
            if np.abs(self.mag_field-self.ps_field)< output_tolerance:
                while not self.pshtr:
                    self.set_switch_htr(True)
                    print "CS4: Tried to open switch heater"
                    time.sleep(1)
            else:
                print "CS4: Else bit, recall myself"
                self.sweep_field(target,rate)
                return 0
            
#            if not self.pshtr:
#                self.sweep_field(target,rate)
#                return 0
        print 'CS4: Wait after ON'
        time.sleep(wait_after_on)
        
        self.set_rate(0,rate)

        if self.mag_field<target:
            self.set_ulim(target)
            time.sleep(1)
            self.sweep('UP',rate)
        else:
            self.set_llim(target)
            time.sleep(1)
            self.sweep('DOWN',rate)
        
        self.time1=time.time()
        sweep_thread=threading.Thread(target=self.sweep_field_watch, args=(driven,))
        sweep_thread.setDaemon(True)
        sweep_thread.start()
        sweep_thread.join()
        