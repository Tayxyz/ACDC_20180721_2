import visa
import time
from data import *

class pph():
    def __init__(self, argv):
        try:
            self.rm = visa.ResourceManager()
            if not self._connect(argv['address']):
                return None
        except Exception, e:
            logE( Exception, e)


    def _connect(self, address=None):
        if address is None:
            address = self.address
        try:
            self.inst = self.rm.open_resource(address)
            # print(self.inst.query('*IDN?'))
            return True
        except Exception, e:
            logE(Exception, e)
            logE(address, ' not find')
            return False

    def get_info(self):
        try:
            return self.inst.query('*IDN?')#Chroma,19020-4,0,2.10
        except:
            return ''

    def power_on(self,argv):
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        try:
            v=argv['v']
        except:
            v='0'
        try:
            i=argv['i']
        except:
            i='0'
        cmds=['VOLTage %s;*OPC?'%v,
              'CURRent %s;*OPC?'%i,
              'OUTPUT ON;*OPC?']
        for cmd in cmds:
            if barrier:
                try:
                    if barrier.acquire():
                        rt=self.inst.query(cmd)
                    else:
                        rt='1\n'
                finally:
                    barrier.release()
                    time.sleep(2)
            else:
                rt = self.inst.query(cmd)
            logV(cmd,'==>',rt)
            if not '1\n' == rt:
                return False

        return True
        pass

    def power_off(self,argv):
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        if barrier:
            try:
                if barrier.acquire():
                    rt = self.inst.query('OUTPUT OFF;*OPC?')
                else:
                    rt = '1\n'
            finally:
                barrier.release()
        else:
            rt = self.inst.query('OUTPUT OFF;*OPC?')
        logV('OUTPUT OFF;*OPC?', '==>', rt)
        if not '1\n' == rt:
            return False
        return True