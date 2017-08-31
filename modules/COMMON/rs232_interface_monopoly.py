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

    def _connect(self):
        try:
            self.com = serial.Serial(self.comnub, 115200, timeout=0)
            logV(self.comnub, 'connected')
        except Exception, e:
            logE(Exception, e)

    def connect(self, argv=None):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        if lock:
            with lock:
                pass
                logV('with lock')
                #self._connect()
        else:
            self._connect()
            return True


    def disconnect(self, argv=None):
        try:
            self.com.close()
        except Exception, e:
            print Exception, e

    def wr(self, cmd, end, has='', timeout=1):
        try:
            self.com.write(cmd)
            buf = ''
            t0 = time.time()
            while time.time() - t0 < timeout:
                buf += self.com.readall()
                if buf.endswith(end) and buf.find(has) >= 0:
                    return True, buf
            return False, buf
        except Exception, e:
            logE(Exception, e)
            return False, e

    def sendCmd(self,argv):
        cmd=argv['cmd'].encode('ascii')
        end=argv['end'].encode('ascii')
        try:
            has=argv['has'].encode('ascii')
        except:
            has=''
        try:
            timeout=int(argv['timeout'].encode('ascii'))
        except:
            timeout=1

        logV(argv)

        rt = self.wr(cmd, end, has, timeout)
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