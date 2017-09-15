from data import *
import serial
import time
import COMMON.dialog as dialog

class led():
    def __init__(self,argv):
        try:
            self.comnub=argv['COM']
        except Exception,e:
           logE(Exception,e)
        try:
            self.baudrate = int(argv['baudrate'])
        except:
            self.baudrate = 115200
        try:
            self.parity = argv['parity'].encode("ascii")
        except:
            self.parity = serial.PARITY_NONE
        self._connect()
        self.wr('root\r','# ')

    def _connect(self):
        try:
            self.com = serial.Serial(self.comnub, self.baudrate,parity=self.parity ,timeout=0)
            logV(self.comnub, 'connected')
        except Exception, e:
            logE(Exception, e)

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

    def test_led(self,argv):
        cmds=['r\r',
              'g\r',
              'b\r',
              'w\r',
              'off']
        rts=[1,2,3,4,5]
        items=['RING_LED_ALL_RED',
                'RING_LED_ALL_GREEN',
                'RING_LED_ALL_BLUE',
                'RING_LED_ALL_WHITE',
                'RING_LED_ALL_OFF']

        for ix in range(len(cmds)):
            rt,buf=self.wr(cmds[ix],'# ')
            logV(cmds[ix],'-->',rt,buf)
            d = dialog.dialog({})
            rt=d.ledForM1({})
            if rt==rts[ix]:
                DATA.op(items[ix]+',0,PASS,N/A,N/A')
            else:
                DATA.op(items[ix] + ',1,FAIL,N/A,N/A')