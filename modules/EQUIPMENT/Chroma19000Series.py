import time
from data import *
from IO.rs232 import RS232

class NLChroma19000Series():
    def __init__(self, argv):
        self.io=RS232(argv)



    def get_info(self):
        try:
            self.io._connect()
            r,v=self.io.wr('*IDN?\r\n','\r\n')#Chroma,19020-4,0,2.10
            self.io.disconnect()
            logV(r,v)
        except Exception,e:
            logE(Exception,e)

    def config(self,argv):
        self.get_info()
        if not argv.has_key('ac_hightlimit'):
            argv['ac_hightlimit']='0.0029'
        if not argv.has_key('ac_lowlimit'):
            argv['ac_lowlimit']='0.00003'
        if not argv.has_key('ac_time'):
            argv['ac_time']='3'
        if not argv.has_key('ac_voltage'):
            argv['ac_voltage']='3000'
        if not argv.has_key('arc_limit'):
            argv['arc_limit']='0.01'
        if not argv.has_key('channel'):
            argv['channel']='001,002,003,004'
        if not argv.has_key('script_index'):
            argv['script_index']='1'
        if not argv.has_key('script_name'):
            argv['script_name']='test'
        if not argv.has_key('time_fall'):
            argv['time_fall']='0'
        if not argv.has_key('time_ramp'):
            argv['time_ramp']='0'

        cmds=['*CLS;*OPC?\r\n',
              'SAF:STEP1:AC %s;*OPC?\r\n'%argv['ac_voltage'].encode("ascii"),
              'SAF:STEP1:AC:LIM %s;*OPC?\r\n'%argv['ac_hightlimit'].encode("ascii"),
              'SAF:STEP1:AC:LIM:LOW %s;*OPC?\r\n'%argv['ac_lowlimit'].encode("ascii"),
              'SAF:STEP1:AC:TIME %s;*OPC?\r\n'%argv['ac_time'].encode("ascii"),
              'SAF:STEP1:AC:LIM:ARC %s;*OPC?\r\n'%argv['arc_limit'].encode("ascii"),
              'SAF:STEP1:AC:TIME:FALL %s;*OPC?\r\n'%argv['time_fall'].encode("ascii"),
              'SAF:STEP1:AC:TIME:RAMP %s;*OPC?\r\n'%argv['time_ramp'].encode("ascii"),
              #'SAF:STEP1:AC:CHAN (@%s);*OPC?\r\n'%argv['channel'].encode("ascii"),
              'MEM:DEL:LOC %s;*OPC?\r\n'%argv['script_index'].encode("ascii"),
              '*SAV %s;*OPC?\r\n'%argv['script_index'].encode("ascii"),
              'MEM:STAT:DEF %s,%s;*OPC?\r\n'%(argv['script_name'].encode("ascii"),argv['script_index'].encode("ascii"))
              ]
        self.io._connect()
        try:
            for cmd in cmds:
                r,v=self.io.wr(cmd,'1\r\n')
                logV(cmd,'==>',r,v)
                if not r:
                    return False
            self.io.disconnect()
        finally:
            self.io.disconnect()
        return True

    def start(self,argv):
        if not argv.has_key('script_index'):
            argv['script_index']='1'

        cmds=['*RCL %s;*OPC?\r\n'%argv['script_index'].encode("ascii"),
              'SAF:STAR;*OPC?\r\n']
        try:
            self.io._connect()
            for cmd in cmds:
                r,v = self.io.wr(cmd,'1\r\n')
                logV(cmd, '==>', r,v)
                if not r:
                    return False
        finally:
            self.io.disconnect()

        return True

    def wait_till_finish(self,argv):
        if not argv.has_key('timeout'):
            argv['timeout']='10'

        t0=time.time()
        r=''
        v=''
        try:
            self.io._connect()
            while time.time()-t0<=int(argv['timeout'].encode("ascii")):
                r,v = self.io.wr('SAF:STAT?\r\n','STOPPED\r\n')
                if r:
                    logV('SAF:STAT?','==>',r,v)
                    return True
            logV('SAF:STAT?', '==>', r,v)
        finally:
            self.io.disconnect()
        return False

    def get_result(self,argv):
        if not argv.has_key('channel'):
            argv['channel']='001'

        cmds=['SAF:RES:ALL:TIME?;*OPC?\r\n',
              'SAF:RES:ALL:MMET?;*OPC?\r\n',
              'SAF:RES:COMP?;*OPC?\r\n',
              'SAF:RES:ALL?;*OPC?\r\n',
              ]

        rts={'COMP':'',
             'ERROR':'',
             'MMET':'',
             'ERROR':''}

        tmp=[]

        try:
            self.io._connect()
            time.sleep(0.1)
            for cmd in cmds:
                r,v = self.io.wr(cmd,'1\r\n')
                logV(cmd,'==>',r,v)
                if r:
                    try:
                        tmp.append(v.split(';')[0])
                    except:
                        pass
            r, v = self.io.wr('SAF:STOP;*OPC?\r\n', '1\r\n')
        finally:
            self.io.disconnect()

        if len(tmp)==4:
            rts['TIME']=tmp[0]
            rts['MMET'] = tmp[1]
            rts['COMP'] = tmp[2]
            rts['ERROR'] = tmp[3]
        else:
            rts['TIME'] = '0'
            rts['MMET'] = '-9999'
            rts['COMP'] = '0'
            rts['ERROR'] = '35'

        return rts



