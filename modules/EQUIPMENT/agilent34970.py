import visa
from data import *
import time
class Agilent34970():
    def __init__(self,argv):
        logD(type(argv['t1']), type(argv['t2']))
        try:
            self.rm = visa.ResourceManager()
            if not self._connect(argv['address']):
                return None
        except Exception,e:
            print Exception,e

    def _common(self, argv):
        self.common = argv

    def _connect(self, address=None):
        if address is None:
            address = self.address
        try:
            print address
            self.inst = self.rm.open_resource(address)
            #print(self.inst.query('*IDN?'))
            return True
        except Exception, e:
            print Exception,e
            print address,' not find'
            return False

    def setParametersForResistance(self, channel, integrationtime='1', range='AUTO', o_comp='OFF',
                                   channeldelay='0', autozero='OFF'):
        try:
            cmd='CONF:RES %s,DEF,(@%s);*OPC?' % (range, channel)
            r = self.inst.query(cmd)
            print cmd,r
            if not '1\n' == r:
                return False
            cmd="SENS:RES:NPLC %s,(@%s);*OPC?" % (integrationtime, channel)
            r = self.inst.query(cmd)
            print cmd, r
            if not '1\n' == r:
                return False
            if range in ('100', '1K', '10K'):
                cmd="SENS:RES:OCOM %s,(@%s);*OPC?" % (o_comp, channel)
                r = self.inst.query(cmd)
                print cmd, r
                if not '1\n' == r:
                    return False
            cmd="ROUTe:CHANnel:DELay %s,(@%s);*OPC?" % (channeldelay, channel)
            r = self.inst.query(cmd)
            print cmd, r
            if not '1\n' == r:
                return False
            cmd="SENS:ZERO:AUTO %s,(@%s);*OPC?" % (autozero, channel)
            r = self.inst.query(cmd)
            print cmd, r
            if not '1\n' == r:
                return False
            return True

        except Exception, e:
            print e
            return False

    def setParametersDCVoltage(self,channel,range='DEF',integrationtime='1',channeldelay='0',autozero='OFF'):
        try:
            r = self.inst.query('CONF:VOLT:DC %s,DEF,(@%s);*OPC?' % (range, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("SENS:VOLT:DC:NPLC %s,(@%s);*OPC?" % (integrationtime, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("ROUTe:CHANnel:DELay %s,(@%s);*OPC?" % (channeldelay, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("SENS:ZERO:AUTO %s,(@%s);*OPC?" % (autozero, channel))
            if not '1\n' == r:
                return False
            return True

        except Exception, e:
            print e
            return False

    def setParametersDCCurrent(self,channel,range='DEF',integrationtime='1',channeldelay='0',autozero='OFF'):
        try:
            r = self.inst.query('CONF:CURR:DC %s,DEF,(@%s);*OPC?' % (range, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("SENS:CURRent:DC:NPLC %s,(@%s);*OPC?" % (integrationtime, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("ROUTe:CHANnel:DELay %s,(@%s);*OPC?" % (channeldelay, channel))
            if not '1\n' == r:
                return False
            r = self.inst.query("SENS:ZERO:AUTO %s,(@%s);*OPC?" % (autozero, channel))
            if not '1\n' == r:
                return False
            return True

        except Exception, e:
            print e
            return False

    def getValue(self):
        try:
            r = self.inst.query("READ?")
            print r
            return True, float(r)
        except Exception, e:
            print e
            return False, -1

    def open(self,channel):
        cmd='ROUT:Open (@%s);*OPC?' % channel
        r = self.inst.query(cmd)
        print cmd,r
        if not '1\n' == r:
            return False
        return True

    def close(self,channel):
        cmd='ROUT:Close (@%s);*OPC?' % channel
        r = self.inst.query(cmd)
        print cmd,r
        if not '1\n' == r:
            return False
        return True

    def timeout(self,to):
        self.inst.timeout=to

    def sync_open(self,argv):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        if lock:
            lock.acquire()
        if self.open(argv['channel'][DATA.id]):
            DATA.op(argv['name'] + ',0,' + 'N/A,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,' + 'N/A,N/A,N/A')
        if lock:
            lock.release()

    def sync_close(self,argv):
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None
        if lock:
            lock.acquire()
        if self.close(argv['channel'][DATA.id]):
            DATA.op(argv['name'] + ',0,' + 'N/A,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,' + 'N/A,N/A,N/A')
        if lock:
            lock.release()

    def sync_get_r(self,argv):
        try:
            lock = DATA.locks[argv['lock']]
        except:
            lock = None
        if lock:
            lock.acquire()

        self.setParametersForResistance(argv['channel'][DATA.id],argv['integrationtime'],argv['range'],argv['o_comp'],argv['channeldelay'],argv['autozero'])
        p,v=self.getValue()
        if p:
            if argv.has_key('ul') and argv['ul']!='N/A':
                if v>float(argv['ul']):
                    p=False
            else:
                argv['ul'] = 'N/A'
            if argv.has_key('ll') and argv['ll']!='N/A':
                if v<float(argv['ll']):
                    p=False
            else:
                argv['ll'] != 'N/A'
        if p:
            DATA.op(argv['name'] + ',0,' + str(v)+','+argv['ul']+','+argv['ll'])
        else:
            DATA.op(argv['name'] + ',1,' + str(v) + ',' + argv['ul'] + ',' + argv['ll'])

        if lock:
            lock.release()


if __name__ == '__main__':
    inst1 = Agilent34970({'address':'GPIB0::9::INSTR'})
    # inst2 = Agilent34970('GPIB0::9')

    '''
    print inst1.setParametersDCCurrent(121)
    for i in range(30):
        print inst1.getValue()
'''
    '''
    print inst1.setParametersDCVoltage(101)
    for i in range(30):
        print inst1.getValue()
'''
    print inst1.setParametersForResistance('101')
    print inst1.getValue()
    inst1._common({'lock':'test1'})
    inst1.sync_open({"channel":{"1":"301","2":"302","3":"303","4":"304"}})
    '''

    print inst1.setParametersForResistance(102,'0.01')
    print inst1.getValue()
    print inst1.setParametersForResistance(103, '100')
    inst1.timeout(10000)
    print inst1.getValue()
    print inst1.setParametersForResistance(101)
    print inst1.getValue()
    print inst2.setParametersForResistance(101)
    print inst2.getValue()

    print inst1.open(201)
    print inst1.close(202)
    print inst2.open(301)
    print inst2.close(302)
    '''

