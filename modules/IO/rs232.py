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

    def connect(self):
        self.com = serial.Serial(self.comnub, self.baudrate, parity=self.parity, timeout=0)

    def disconnect(self, argv=None):
        try:
            self.com.close()
        except Exception, e:
            print Exception, e
            logE(Exception, e)

    def wr(self, cmd, end, has='', timeout=3):
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

    def wr_bytes(self, cmd, end, has='', timeout=3):
        try:
            self.com.write(cmd)
            buf = ''
            t0 = time.time()
            while time.time() - t0 < timeout:
                buf += self.com.readall()
                logD(buf)
                try:
                    if buf.endswith(end) and buf.find(has) >= 0:
                        return True, buf
                except:
                    pass
            return False, buf
        except Exception, e:
            logE(Exception, e)
            return False, e

    def wr_getfixlen(self, cmd, length, has='', timeout=1):
        try:
            self.com.readall()
            self.com.write(cmd)
            buf = ''
            t0 = time.time()
            while time.time() - t0 < timeout:
                buf += self.com.readall()
                if len(buf)==length and buf.find(has) >= 0:
                    return True, buf
            return False, buf
        except Exception, e:
            logE(Exception, e)
            return False, e

    def wr_hex(self, hexcmds, hexends, hexhas='', timeout=1):

        cmds=''
        for hexcmd in hexcmds:
            cmds+=chr(int( hexcmd,16))

        end = ''
        for hexend in hexends:
            end += chr(int(hexend,16))

        has = ''
        for hexha in hexhas:
            has += chr(int(hexha, 16))

        rt,v = self.wr(cmds, end, has, timeout)
        try:
            v=self.hex2str(v)
        except:
            pass

        return rt,v
