import numpy as np
import os
import threading
import sys
sys.path.append('H:\public_html\python')
from egg7265_driver import egg7265
from levelmeter_driver import lm500
from ls370_driver import ls370
from cs4_driver import cs4
from model_4g_driver import model4g
from rotator import rotator
import time

########################################################
# initialize egg1
egg1_addr=12
#egg1=egg7265(egg1_addr)

########################################################
# initialize egg2
egg2_addr=14
#egg2=egg7265(egg2_addr)

########################################################
# initialize levelmeter
lm_addr=4
#lm=lm500(lm_addr)

########################################################
# initialize ls370_th
#ls370_th_addr=13
#ls_th=ls370(ls370_th_addr)
#ru_channel=1
#cx_channel=2				# whatever

########################################################
# initialize cs4
hps_addr=1
#hps=cs4(hps_addr)


########################################################
# initialize model4g
mod4g_addr=2
#vps=model4g(mod4g_addr)

########################################################
# initialize rotator (address is COM Port)
rot_addr=4
#rot=rotator(rot_addr)


global a

class measure():


    def __init__(self, filepath1, filename1):
        self.filepath=filepath1
        self.filename=filename1

        self.header='time temp_ru temp_cx Ux1 Uy1 Ux2 Uy2 hps_mag hps_curr hps_switch vps_mag vps_curr vps_switch angle heater_pw he_level\n'
        self.stable_crit=0.005


        self.start_time=time.time()
        self.log_switch=threading.Event()           # data gets logged to file
        self.log_switch.clear()

        self.logging_switch=threading.Event()       # data gets logged at all
        self.logging_switch.set()

        ##########################################################
        ##    Instantiate Devices as child classes of measure()
        
        self.egg1=egg7265(egg1_addr)
        self.egg2=egg7265(egg2_addr)
        
        self.lm=lm500(lm_addr)
       
       #self.ls_th=ls370(ls370_th_addr)
       #ru_channel=1
       #cx_channel=2				# whatever     
       
        self.hps=cs4(hps_addr)
        self.vps=model4g(mod4g_addr)

        self.rot=rotator(rot_addr)
        
        #############################################################

        j=0

        files=os.listdir(self.filepath)
        for file in files:
            if self.filename==file:           # look for a datafile with the same name, set j as a switch
                j=1

        if j==1:                         # if there was a datafile with the same name, call method again with new filename
            self.filename=self.filename+str(int(time.time()))
        self.handler=open(self.filepath+self.filename+'.dat','a')



    def logg(self,switch):
        """
        Set the threading.Event log_switch or unset it to start / stop it writing data
        to the datafile
        """
        if switch==True:
            self.log_switch.set()
            return self.log_switch.is_set()

        elif switch==False:
            self.log_switch.clear()
            return self.log_switch.is_set()

        else:
            print "Unknown log_switch"
            return -1


    def set_filepath(self,filepath):
        """
        set the filepath to the folder where datafiles live
        """
        
        self.filepath=filepath
        return self.filepath

    def set_filename(self,filename):
        """
        Set the filename of the current datafile. if it is already known, a '1' gets appended
        and the method is called again
        """

        global a        
        
        try:
            self.handler.close()         # try to close the old datafile. If it doesn't work, there was none
        except:
            a=a    

        j=0

        files=os.listdir(self.filepath)
        for file in files:
            if self.filename==file:           # look for a datafile with the same name, set j as a switch
                j=1

        if j==1:                         # if there was a datafile with the same name, call method again with new filename
            
            self.set_filename(self.filename + str(time.time()))

        self.handler=open(self.filepath+self.filename+'.dat','a')
                                         # ...open the file in append mode
        self.handler.write(self.header)
                                         # and plug a header o top of it
        return self.filename



    def start_logging(self):

#        print 'initialized1'
        self.log_thread=threading.Thread(target=self.log_data)
#        self.log_thread=threading.Thread(target=self.test_method())
#        print 'initialized2'
        self.log_thread.start()
#        print 'started logging (after log_thread.start())1'

#        self.log_thread.join(timeout=0.1)
#        print 'started logging (after log_thread.start())2'


    def log_data(self):
        """
        log data method, this will hopefully be called as a thread, controlled by the event
        log_switch. the method basically just querys all the devices, and if log_switch is set, it writes it to datafile
        """
        print 'start logging (the log_data(self))'


        len_hist=100
        self.time_hist=time.time()-self.start_time

        self.ux1,self.uy1=self.egg1.get_xy()
        self.ux1_hist=self.ux1
        self.uy1_hist=self.uy1
        self.ux2,self.uy2=self.egg2.get_xy()
        self.ux2_hist=self.ux2
        self.uy2_hist=self.uy2

        print 'lockin worked'


#        self.hps_mag=self.hps.get_mag_field()
        self.hps_mag=self.hps.get_mag_field()

        self.hps_mag_field_hist=self.hps_mag
        self.hps_curr=self.hps.get_ps_field()
        self.hps_curr_field_hist=self.hps_curr

        print 'hps worked'
        
        self.vps_mag=self.vps.get_mag_field()
        self.vps_mag_field_hist=self.vps_mag
        self.vps_curr=self.vps.get_ps_field()
        self.vps_curr_field_hist=self.vps_curr

        i=0
        while self.logging_switch.is_set():
            print i, 'log_data'
            i=i+1
            self.time=time.time()-self.start_time
            self.time_hist=np.append(self.time_hist,self.time)
            if len(self.time_hist)>len_hist:
                self.time_hist=np.delete(self.time_hist,0)


#            self.temp_ru=self.ls_th.get_temp(ru_channel)
#            self.temp_ru_hist=np.append(self.temp_ru_hist,self.temp_ru)
#            if len(self.temp_ru_hist)>len_hist:
#                self.temp_ru_hist=np.delete(self.temp_ru_hist,0)

#            self.temp_cx=self.ls_th.get_temp(cx_channel)
#            self.temp_cx_hist=np.append(self.temp_cx_hist,self.temp_cx)
#            if len(self.temp_cx_hist)>len_hist:
#               self.temp_cx_hist=np.delete(self.temp_cx_hist,0)

#            self.htr_pw=self.ls_th.get_heater(cx_channel)
#            self.htr_pw_hist=np.append(self.htr_pw_hist,self.htr_pw)
#            if len(self.htr_pw_hist)>len_hist:
#               self.htr_pw_hist=np.delete(self.htr_pw_hist,0)

            self.level=self.lm.read()

            self.ux1,self.uy1=self.egg1.get_xy()
            self.ux1_hist=np.append(self.ux1_hist,self.ux1)
            if len(self.ux1_hist)>len_hist:
                self.ux1_hist=np.delete(self.ux1_hist,0)
            self.uy1_hist=np.append(self.uy1_hist,self.uy1)
            if len(self.uy1_hist)>len_hist:
                self.uy1_hist=np.delete(self.uy1_hist,0)

            self.ux2,self.uy2=self.egg2.get_xy()
            self.ux2_hist=np.append(self.ux2_hist,self.ux2)
            if len(self.ux2_hist)>len_hist:
                self.ux2_hist=np.delete(self.ux2_hist,0)
            self.uy2_hist=np.append(self.uy2_hist,self.ux1)
            if len(self.uy2_hist)>len_hist:
                self.uy2_hist=np.delete(self.uy2_hist,0)

            self.hps_mag=self.hps.get_mag_field()
            self.hps_mag_field_hist=np.append(self.hps_mag_field_hist,self.hps_mag)
            if len(self.hps_mag_field_hist)>len_hist:
                self.hps_mag_field_hist=np.delete(self.hps_mag_field_hist,0)

            self.hps_curr=self.hps.get_ps_field()
            self.hps_curr_field_hist=np.append(self.hps_curr_field_hist,self.hps_curr)
            if len(self.hps_curr_field_hist)>len_hist:
                self.hps_curr_field_hist=np.delete(self.hps_curr_field_hist,0)

            self.hps_pshtr=self.hps.get_switch_htr()

            self.vps_mag=self.vps.get_mag_field()
            self.vps_mag_field_hist=np.append(self.vps_mag_field_hist,self.vps_mag)
            if len(self.vps_mag_field_hist)>len_hist:
                self.vps_mag_field_hist=np.delete(self.vps_mag_field_hist,0)

            self.vps_curr=self.vps.get_ps_field()
            self.vps_curr_field_hist=np.append(self.vps_curr_field_hist,self.vps_curr)
            if len(self.vps_curr_field_hist)>len_hist:
                self.vps_curr_field_hist=np.delete(self.vps_curr_field_hist,0)

            self.vps_pshtr=self.vps.get_switch_htr()

            self.angle=self.rot.get_angle()


            if not self.log_switch.is_set():
                
                string=str(self.time)+' '
                string=string+str(self.ux1)+' '+str(self.uy1)+' '+str(self.ux2)+' '
                string=string+str(self.uy2)+' '+str(self.hps_mag)+' '+str(self.hps_curr)+' '
                string=string+str(self.hps_pshtr)+' '+str(self.vps_mag)+' '+str(self.vps_curr)+' '
                string=string+' '+str(self.vps_pshtr)+' '+str(self.angle)+' '+str(self.level)+'\n'
                self.handler.write(string)

            time.sleep(1)


    def wait(self,what,how_long):

        start_mean=np.mean(what[0:10])
        end_mean=np.mean(what[89:99])
        while abs(1-start_mean/end_mean)>self.stable_crit:       
            start_mean=np.mean(what[0:10])
            end_mean=np.mean(what[89:99])
            time.sleep(1)    
        
        return 0


    def sweep_field(self,start, stop, rate, phi, theta):

        dummy=self.rot.rotate(phi)
        dummy2=True
        while dummy2:
            dummy2=False
            if self.rot.get_status==True:
                dummy2=True
            time.sleep(2)

        time.sleep(20)

        hps_start=start*np.cos(start)
        vps_start=start*np.sin(start)
        hps_stop=stop*np.cos(stop)
        vps_stop=stop*np.sin(stop)

        hps_rate=rate*np.cos(rate)
        vps_rate=rate*np.sin(rate)

        hps_depersist=threading.Thread(target=self.hps.sweep_field,\
        args=(hps_start,0.4),kwargs={'driven':True})

        vps_depersist=threading.Thread(target=self.vps.sweep_field,\
        args=(vps_start,0.4),kwargs={'driven':True})

        hps_depersist.start()
        vps_depersist.start()
        hps_depersist.join()
        vps_depersist.join()


    def close_datafile(self):
        self.handler.close()


    def test_method(self):
        i=0
        while i<5:
            i=i+1
            print i
            time.sleep(1)


    def start_test_method(self):
        testm=threading.Thread(target=self.test_method())
        
        testm.start()
        print 'threading just started'
        
    def finish(self):
        self.hps.kill_watch_status()
        self.vps.kill_watch_status()
        self.logging_switch.clear()