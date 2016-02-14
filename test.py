from measurement_test import measure
import threading

def test_thread():
    i=0
    while i<5:
        i=i+1
        print i



meas=measure('H:\\public_html\\python\\', 'testfile')
#meas.filepath='H:\\public_html\\python\\'
print meas.filepath

#meas.filename='testfile'
print meas.filename

t=threading.Thread(target=test_thread)
t.start()
print 'test thread started'

meas.start_logging()
print 'should have started logging1'
meas.logg(True)
i=0
print 'should have started logging2'

while i<11:
    print meas.ux1, '  ', meas.ux2
    i=i+1
    time.sleep(1)
meas.logg(False)
meas.close_datafile()