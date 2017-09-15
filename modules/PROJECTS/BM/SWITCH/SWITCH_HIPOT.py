from data import *
from EQUIPMENT.Chroma19000Series import NLChroma19000Series

class hipot():
    def __init__(self,argv):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lcok=None
        if lcok:
            with lock:
                self.quip=NLChroma19000Series(argv)
                logV(self.quip.get_info())
        else:
            self.quip = NLChroma19000Series(argv)
            logV(self.quip.get_info())
        pass

    def test_config(self,argv):
        try:
            open('whoareyou')
            import os
            os.remove('whoareyou')
        except:
            return
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        if barrier:
            try:
                if barrier.acquire():
                    r=self.quip.config(argv)
                else:
                    r='barrier pass'
            finally:
                barrier.release()
        else:
            r = self.quip.config(argv)
        if r:
            DATA.op('TEST_CONFIG_EQUIPMENT,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CONFIG_EQUIPMENT,1,FAIL,N/A,N/A')
        logV('config:',r)

    def test_start(self,argv):
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        if barrier:
            try:
                if barrier.acquire():
                    r=self.quip.start(argv)
                else:
                    r='barrier pass'
            finally:
                barrier.release()
        else:
            r = self.quip.start(argv)
        if r:
            DATA.op('TEST_START_EQUIPMENT,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_START_EQUIPMENT,1,FAIL,N/A,N/A')
        logV('start:', r)

        if barrier:
            try:
                if barrier.acquire():
                    r=self.quip.wait_till_finish(argv)
                else:
                    r='barrier pass'
            finally:
                barrier.release()
        else:
            r = self.quip.wait_till_finish(argv)
        if r:
            DATA.op('TEST_WAIT_EQUIPMENT,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_WAIT_EQUIPMENT,1,FAIL,N/A,N/A')
        logV('wait_till_finish:', r)

    def get_hipot(self,argv):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        if lock:
            with lock:
                rt=self.quip.get_result(argv)
        else:
            rt=self.quip.get_result(argv)
        logV(rt)
        if rt['ERROR']=='':
            DATA.op()
        else:
            DATA.op()

