import serial
import time
from data import *

class RS232:
    def __init__(self, argv):
        try:
            self.comnub = argv['COM'][str(DATA.id)].encode("ascii")
            logV (self.comnub)
            #self.connect()
        except Exception, e:
            logE(Exception, e)
        try:
            self.baudrate=int(argv['baudrate'])
        except:
            self.baudrate=115200
        try:
            self.parity=argv['parity'].encode("ascii")
        except:
            self.parity=serial.PARITY_NONE

    def hex2str(self,argv):
        result = ''
        hLen = len(argv)
        for i in xrange(hLen):
            hvol = ord(argv[i])
            hhex = '%02x' % hvol
            result += hhex + ' '
        return result

    def _connect(self):
        try:
            self.com = serial.Serial(self.comnub, self.baudrate,parity=self.parity ,timeout=0)
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
                self._connect()
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

    def sendHexCmad(self,argv):
        hexcmds=argv['cmd'].split()
        cmds=''
        for hexcmd in hexcmds:
            cmds+=chr(int( hexcmd,16))

        hexends = argv['end'].split()
        end = ''
        for hexend in hexends:
            end += chr(int(hexend,16))

        hexhas = argv['has'].split()
        has = ''
        for hexha in hexhas:
            has += chr(int(hexha, 16))

        try:
            timeout=float(argv['timeout'].encode('ascii'))
        except:
            timeout=1

        rt,v = self.wr(cmds, end, has, timeout)
        try:
            v=self.hex2str(v)
        except:
            pass
        logV(rt,v)
        if rt:
            DATA.op(argv['name']+',0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')

    def readtemp(self,argv):
        hexcmds=argv['cmd'].split()
        cmds=''
        for hexcmd in hexcmds:
            cmds+=chr(int( hexcmd,16))

        hexends = argv['end'].split()
        end = ''
        for hexend in hexends:
            end += chr(int(hexend,16))

        hexhas = argv['has'].split()
        has = ''
        for hexha in hexhas:
            has += chr(int(hexha, 16))

        try:
            timeout=int(argv['timeout'].encode('ascii'))
        except:
            timeout=1

        rt,v = self.wr(cmds, end, has, timeout)
        tempv=-99

        try:
            if len(v)==9:
                tempv=(ord(v[5])*16*16+ord(v[6]))/10
        except:
            pass
        try:
            v=self.hex2str(v)
        except:
            pass
        logV(rt,v,str(tempv))
        return tempv






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
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        logV(argv)
        if lock:
            with lock:
                self._connect()
                rt,v=self.wr(cmd,end,has,timeout)
                self.disconnect()
        elif barrier:
            try:
                if barrier.acquire():
                    logV('barrier.acquire')
                    self._connect()
                    rt,v= self.wr(cmd, end, has, timeout)
                    self.disconnect()
                    #print 'i do it'
                else:
                    rt,v=True,'barrier bypass'
                    #print DATA.id,'barrier bypass'
            finally:
                barrier.release()
        else:
            rt,v = self.wr(cmd, end, has, timeout)
        logV(rt,v)
        if rt:
            DATA.op(argv['name']+',0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')

        return rt


    def fakeitem(self,argv):
        for i in range(2):
            logV('fake log')
            DATA.op('FAKEITEM,0,0,N/A,N/A')
            time.sleep(0.5)

if __name__=='__main__':
    rs232=RS232({'COM':'/dev/tty.usbmodem1412'})
    rs232.connect()
    print rs232.wr('root\n', '#')