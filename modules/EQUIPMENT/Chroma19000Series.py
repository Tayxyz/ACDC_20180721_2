import visa
import time
from data import *

class NLChroma19000Series():
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

    def config(self,argv):
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

        cmds=['*CLS;*OPC?',
              'SAF:STEP1:AC %s;*OPC?'%argv['ac_voltage'],
              'SAF:STEP1:AC:LIM %s;*OPC?'%argv['ac_hightlimit'],
              'SAF:STEP1:AC:LIM:LOW %s;*OPC?'%argv['ac_lowlimit'],
              'SAF:STEP1:AC:TIME %s;*OPC?'%argv['ac_time'],
              'SAF:STEP1:AC:LIM:ARC %s;*OPC?'%argv['arc_limit'],
              'SAF:STEP1:AC:TIME:FALL %s;*OPC?'%argv['time_fall'],
              'SAF:STEP1:AC:TIME:RAMP %s;*OPC?'%argv['time_ramp'],
              'SAF:STEP1:AC:CHAN (@%s);*OPC?'%argv['channel'],
              'MEM:DEL:LOC %s;*OPC?'%argv['script_index'],
              '*SAV %s;*OPC?'%argv['script_index'],
              'MEM:STAT:DEF %s,%s;*OPC?'%(argv['script_name'],argv['script_index'])
              ]

        for cmd in cmds:
            rt=self.inst.query(cmd)
            logV(cmd,'==>',rt)
            if not '1\n' == rt:
                return False

        return True

    def start(self,argv):
        if not argv.has_key('script_index'):
            argv['script_index']='1'

        cmds=['*RCL %s;*OPC?'%argv['script_index'],
              'SAF:STAR;*OPC?']
        for cmd in cmds:
            rt = self.inst.query(cmd)
            logV(cmd, '==>', rt)
            if not '1\n' == rt:
                return False

        return True

    def wait_till_finish(self,argv):
        if not argv.has_key('timeout'):
            argv['timeout']='1'

        t0=time.time()
        rt=''
        while time.time()-t0<=int(argv['timeout']):
            rt = self.inst.query('SAF:STAT?')
            if rt.find('STOPPED')>=0:
                logV('SAF:STAT?','==>',rt)
                return True
        logV('SAF:STAT?', '==>', rt)
        return False

    def get_result(self,argv):
        if not argv.has_key('channel'):
            argv['channel']='001'

        cmds=['SAF:CHAN00%s:RES:ALL:TIME?;*OPC?'%argv['channel'],
              'SAF:CHAN00%s:RES:STEP1:MMET?;*OPC?'%argv['channel'],
              'SAF%s:RES:COMP?;*OPC?'%argv['channel'],
              'SAF:CHAN00%s:RES:STEP1?;*OPC?'%argv['channel'],
              ]

        rts={'COMP':'',
             'ERROR':'',
             'MMET':'',
             'ERROR':''}

        tmp=[]

        for cmd in cmds:
            rt = self.inst.query(cmd)
            logV(cmd,'==>',rt)
            if rt.endswith('1\n'):
                tmp.append(rt.split(';')[0])

        rts['TIME']=tmp[0]
        rts['MMET'] = tmp[1]
        rts['COMP'] = tmp[2]
        rts['ERROR'] = tmp[3]

        return rts



