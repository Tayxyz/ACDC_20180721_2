from data import *
from IO.rs232 import RS232
import time
class fct():
    def __init__(self,argv):
        self.dut = RS232(argv)


    def send_cmd(self,argv):
        self.dut._connect()
        try:
            name = argv['name']
        except:
            name = 'UNKNOW'
        try:
            cmd = argv['cmd'].encode('ascii')
        except:
            cmd = 'root\r'
        try:
            end = argv['end']
        except:
            end = '# '
        try:
            has = argv['has']
        except:
            has = 'root@ '
        try:
            timeout = float(argv['timeout'])
        except:
            timeout = 1
        rt, v = self.dut.wr(cmd,end, has, timeout)
        logV(rt,v)
        if rt:
            DATA.op(name+',0,PASS,N/A,N/A')
        else:
            DATA.op(name + ',1,FAIL,N/A,N/A')
        self.dut.disconnect()

    def readIF(self,argv):
        self.dut._connect()
        try:
            name = argv['name']
        except:
            name = 'UNKNOW'
        try:
            cmd = argv['cmd'].encode('ascii')
        except:
            cmd = 'root\r'
        try:
            end = argv['end']
        except:
            end = '# '
        try:
            has = argv['has']
        except:
            has = 'root@ '
        try:
            timeout = float(argv['timeout'])
        except:
            timeout = 1
        time.sleep(1)
        v_pir = ['N/A', 'N/A']
        name_pir = ['PIR1', 'PIR2']

        def getpir():
            rt, v = self.dut.wr(cmd, end, has, timeout)
            logV(rt,v)
            vs=v.split()
            if len(vs)>=3:
                values=vs[-2].strip().split(',')
                if len(values)==2:
                    return values

        for ix in range(3):
            v_pir=getpir()
            if v_pir[0].strip()!='0' and v_pir[0].strip()!='16383' and v_pir[1].strip()!='0' and v_pir[1].strip()!='16383':
                break

        for ix in range(2):
            if v_pir[ix]=='N/A':
                DATA.op(name_pir[ix]+',1,FAIL,N/A,N/A')
            else:
                DATA.op(name_pir[ix] + ',0,%s,N/A,N/A'%v_pir[ix])
        self.dut.disconnect()

    def readIA(self, argv):
        self.dut._connect()
        try:
            name = argv['name']
        except:
            name = 'UNKNOW'
        try:
            cmd = argv['cmd'].encode('ascii')
        except:
            cmd = 'root\r'
        try:
            end = argv['end']
        except:
            end = '# '
        try:
            has = argv['has']
        except:
            has = 'root@ '
        try:
            timeout = float(argv['timeout'])
        except:
            timeout = 1
        time.sleep(1)
        rt, v = self.dut.wr(cmd, end, has, timeout)
        logV(rt,repr(v))
        vs = v.split('\n')
        logD(vs)
        v_itfc=['N/A','N/A','N/A']
        name_itfc=['ITFC1','ITFC2','ITFC3']
        v_flex=['N/A','N/A','N/A']
        name_flex=['FLEX1','FLEX2','FLEX3']
        if len(vs)>3:
            ITFCs = vs[-3].strip().split(':')
            logD(ITFCs)
            if len(ITFCs)==2:
                itfcv=ITFCs[1].split(',')
                if len(itfcv)==3:
                    v_itfc=itfcv
            FLEXs = vs[-2].strip().split(':')
            logD(FLEXs)
            if len(FLEXs)==2:
                flexv=FLEXs[1].split(',')
                if len(flexv)==3:
                    v_flex=flexv
        for ix in range(3):
            if v_itfc[ix]=='N/A':
                DATA.op(name_itfc[ix]+',1,N/A,N/A,N/A')
            else:
                DATA.op(name_itfc[ix] + ',0,%s,N/A,N/A'%v_itfc[ix])
        for ix in range(3):
            if v_flex[ix]=='N/A':
                DATA.op(name_flex[ix]+',1,N/A,N/A,N/A')
            else:
                DATA.op(name_flex[ix] + ',0,%s,N/A,N/A'%v_flex[ix])
        self.dut.disconnect()

    def readIP(self, argv):
        self.dut._connect()
        try:
            name = argv['name']
        except:
            name = 'UNKNOW'
        try:
            cmd = argv['cmd'].encode('ascii')
        except:
            cmd = 'root\r'
        try:
            end = argv['end']
        except:
            end = '# '
        try:
            has = argv['has']
        except:
            has = 'root@ '
        try:
            timeout = float(argv['timeout'])
        except:
            timeout = 1
        time.sleep(1)
        rt, v = self.dut.wr(cmd, end, has, timeout)
        logV(rt,v)
        vs = v.split()
        v_ip=['N/A','N/A','N/A','N/A','N/A']
        name_ip=['IP1','IP2','IP3','IP4','IP5']
        if len(vs)>3:
            values = vs[-2].strip().split(',')
            if len(values)==5:
                v_ip=values
        for ix in range(5):
            if v_ip[ix]=='N/A':
                DATA.op(name_ip[ix]+',1,FAIL,N/A,N/A')
            else:
                DATA.op(name_ip[ix] + ',0,%s,N/A,N/A'%v_ip[ix])
        self.dut.disconnect()
