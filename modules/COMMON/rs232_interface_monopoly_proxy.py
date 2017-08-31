import serial
import time
from data import *

class RS232:
    def __init__(self, argv):
        try:
            self.comnub = argv['COM'].encode("ascii")
            logV (self.comnub)
            #self.connect()
        except Exception, e:
            logE(Exception, e)

    def askmonopoly(self,argv):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        if lock:
            with lock:
                DATA.c2s_io.put(argv)
                rt= DATA.s2c_io.get()
        elif barrier:
            try:
                if barrier.acquire():
                    DATA.c2s_io.put(argv)
                    rt= DATA.s2c_io.get()

                else:
                    rt='barrier bypass'
                    #print DATA.id,'barrier bypass'
            finally:
                barrier.release()

        logV(rt)
        return rt

    def fakeitem(self,argv):
        for i in range(2):
            logV('fake log')
            DATA.op('FAKEITEM,0,0,NA,NA')
            time.sleep(0.5)


if __name__=='__main__':
    rs232=RS232({'COM':'/dev/tty.usbmodem1412'})
    rs232.connect()
    print rs232.wr('root\n', '#')