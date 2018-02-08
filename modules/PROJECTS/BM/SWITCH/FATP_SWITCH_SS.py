from data import *
from IO.rs232 import RS232
import time
import COMMON.dialog as dialog
import subprocess

class ss():
    def __init__(self,argv):
        if DATA.isn.startswith('26'):
            self.gang = 1
        elif DATA.isn.startswith('21'):
            self.gang = 2
        else:
            self.gang = 'NUKNOW'
        DATA.op('GANG_NUMBER,0,%d,N/A,N/A'%self.gang)
        self.comid = argv['COM']['1']
        self.dut=RS232({"COM":self.comid})
        if self.gang>1:
            self.comid2=argv['COM']['2']
            self.dut2=RS232({"COM":self.comid2})
        if self.gang>2:
            self.comid3=argv['COM']['3']
            self.dut3=RS232({"COM":self.comid3})


    def GetMiddleStr(self,content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
            endIndex = content.index(endStr,startIndex)
            return content[startIndex:endIndex]
        else:
            return ''

    def testReadValueByOne(self,dut):
        versionname = 'TEST_READ_FW_VERSION'
        sysenvnames=[
                    'TEST_READ_MODEL_SWITCH',
                    'TEST_READ_CONFIG_SWTICH_MLB',
                    'TEST_READ_CONFIG_SWTICH_FATP',
                    'TEST_READ_BUILD_EVENT',
                    'TEST_READ_ISN_SWTICH_MLB',
                    'TEST_READ_ISN_SWTICH_FATP',
                    'TEST_READ_NLWEAVEDEVICEID',
                    'TEST_READ_CERTIFICATE_KEY',
                    'TEST_READ_NLWEAVEPRIVATEKEY',
                    'TEST_READ_NLHASHKEY',
                    'TEST_READ_NLWEAVEPROVISIONINGHASH']
        genhashname='TEST_GENERATE_NLWEAVEPROVISIONINGHASH'
        item_value={}
        for name in sysenvnames:
            item_value[name]='N/A'
        item_value[versionname]='N/A'
        item_value[genhashname] = 'N/A'
        sys_kname = {
                     'TEST_READ_MODEL_SWITCH':'nlmodel',
                     'TEST_READ_CONFIG_SWTICH_MLB':'mlbconfig',
                     'TEST_READ_CONFIG_SWTICH_FATP':'config',
                     'TEST_READ_BUILD_EVENT':'build_event',
                     'TEST_READ_ISN_SWTICH_FATP':'serial#',
                     'TEST_READ_ISN_SWTICH_MLB':'mlb#',
                     'TEST_READ_NLWEAVEDEVICEID':'nlWeaveDeviceId',
                     'TEST_READ_CERTIFICATE_KEY':'nlWeaveCertificate',
                     'TEST_READ_NLWEAVEPRIVATEKEY':'nlWeavePrivateKey',
                     'TEST_READ_NLHASHKEY':'nlHashKey',
                     'TEST_READ_NLWEAVEPROVISIONINGHASH':'nlWeaveProvisioningHash',
                     'TEST_READ_NLDESTCOUNTRY':'nldestcountry',
                     'TEST_READ_BUILD_DATE':'build_date'}
        env_kv={}
        dut._connect()
        r,v = dut.wr('\r','# ')
        logV(r,v)
        r,v = dut.wr('sysenv\r','# ','=',1)
        logV(r,v)
        if r:
            try:
                vs=v.split('\n')
            except:
                vs=[]
            for value in vs:
                try:
                    syskey,sysv=value.strip().split('=',1)
                    env_kv[syskey]=sysv
                except:
                    pass
        for name in sysenvnames:
            if sys_kname[name] in env_kv.keys():
                item_value[name] = env_kv[sys_kname[name]]

        r,v = dut.wr('version\r','# ')
        logV(r,v)
        if r:
            try:
                vs=v.split('\n')
                if len(vs)>=3:
                    item_value[versionname]=vs[-2].strip()
            except:
                pass
        r, v = dut.wr('weavehash\r', '# ')
        logV(r,v)
        if r:
            try:
                vs = v.split('\n')
                if len(vs) >= 3:
                    item_value[genhashname] = vs[-2].strip().split(':')[1].strip()
            except:
                pass
        dut.disconnect()
        return item_value

    def testReadValue(self,argv):
        sysenvnames = ['TEST_READ_FW_VERSION',
            'TEST_READ_MODEL_SWITCH',
            'TEST_READ_CONFIG_SWTICH_MLB',
            'TEST_READ_CONFIG_SWTICH_FATP',
            'TEST_READ_BUILD_EVENT',
            'TEST_READ_ISN_SWTICH_MLB',
            'TEST_READ_ISN_SWTICH_FATP',
            'TEST_READ_NLWEAVEDEVICEID',
            'TEST_READ_CERTIFICATE_KEY',
            'TEST_READ_NLWEAVEPRIVATEKEY',
            'TEST_READ_NLHASHKEY',
            'TEST_READ_NLWEAVEPROVISIONINGHASH',
            'TEST_GENERATE_NLWEAVEPROVISIONINGHASH']

        self.kv =kv= self.testReadValueByOne(self.dut)
        logV(kv)
        for name in sysenvnames:
            if kv[name]=='N/A':
                DATA.op('%s_P1,1,%s,N/A,N/A' % (name, kv[name]))
            else:
                DATA.op('%s_P1,0,%s,N/A,N/A' % (name, kv[name]))

        if self.gang==2:
            self.kv2=kv = self.testReadValueByOne(self.dut2)
            for name in sysenvnames:
                if kv[name] == 'N/A':
                    DATA.op('%s_P2,1,%s,N/A,N/A' % (name, kv[name]))
                else:
                    DATA.op('%s_P2,0,%s,N/A,N/A' % (name, kv[name]))

    def testCheckValueByOne(self,kv):
        sysenvnames = ['TEST_READ_FW_VERSION',
                       'TEST_READ_MODEL_SWITCH',
                       'TEST_READ_CONFIG_SWTICH_MLB',
                       'TEST_READ_CONFIG_SWTICH_FATP',
                       'TEST_READ_BUILD_EVENT',
                       'TEST_READ_ISN_SWTICH_MLB',
                       'TEST_READ_ISN_SWTICH_FATP',
                       'TEST_READ_NLWEAVEDEVICEID',
                       'TEST_READ_CERTIFICATE_KEY',
                       'TEST_READ_NLWEAVEPRIVATEKEY',
                       'TEST_READ_NLHASHKEY',
                       'TEST_READ_NLWEAVEPROVISIONINGHASH',
                       'TEST_GENERATE_NLWEAVEPROVISIONINGHASH']
        testitems = ['TEST_CHECK_MODEL_SWITCH',
                     'TEST_CHECK_CONFIG_SWTICH_MLB',
                     'TEST_CHECK_CONFIG_SWTICH_FATP',
                     'TEST_CHECK_BUILD_EVENT',
                     'TEST_CHECK_ISN_SWTICH_MLB',
                     'TEST_CHECK_ISN_SWTICH_FATP',
                     'TEST_CHECK_NLWEAVEDEVICEID',
                     'TEST_CHECK_NLHASHKEY',
                     'TEST_CHECK_CERTIFICATE_KEY',
                     'TEST_CHECK_NLWEAVEPRIVATEKEY',
                     'TEST_CHECK_NLWEAVEPROVISIONINGHASH']
        result={}
        for item in testitems:
            result[item] = False

        isn80 = DATA.isn
        logV('%s , %s'%(kv['TEST_READ_ISN_SWTICH_FATP'] ,DATA.isn))
        if kv['TEST_READ_ISN_SWTICH_FATP'] == DATA.isn:
            result['TEST_CHECK_ISN_SWTICH_FATP'] = True

        isn60 = kv['TEST_READ_ISN_SWTICH_MLB']
        logV('mlb# = %s'%isn60)
        result['TEST_CHECK_ISN_SWTICH_MLB'] = True

        sfis = DATA.objs['sfis']
        logD(sfis)
        CONFIG_FATP = sfis.get_config(isn80)
        logV('%s , %s' % (CONFIG_FATP, kv['TEST_READ_CONFIG_SWTICH_FATP']))
        if CONFIG_FATP == kv['TEST_READ_CONFIG_SWTICH_FATP']:
            result['TEST_CHECK_CONFIG_SWTICH_FATP'] = True

        MLBCONFIG = sfis.get_mlb_pre_config(isn60)
        logV('%s , %s' % (MLBCONFIG,kv['TEST_READ_CONFIG_SWTICH_MLB']))
        if MLBCONFIG==kv['TEST_READ_CONFIG_SWTICH_MLB']:
            result['TEST_CHECK_CONFIG_SWTICH_MLB']=True

        TEST_CHECK_NLWEAVEPRIVATEKEY = sfis.get_mlb_snx(isn60, 'SNA')
        logV('%s , %s' % (TEST_CHECK_NLWEAVEPRIVATEKEY , kv['TEST_READ_NLWEAVEPRIVATEKEY']))
        if TEST_CHECK_NLWEAVEPRIVATEKEY == kv['TEST_READ_NLWEAVEPRIVATEKEY']:
            result['TEST_CHECK_NLWEAVEPRIVATEKEY'] = True

        TEST_CHECK_CERTIFICATE_KEY = sfis.get_mlb_snx(isn60, 'SNB')
        logV('%s , %s' % (TEST_CHECK_CERTIFICATE_KEY , kv['TEST_READ_CERTIFICATE_KEY']))
        if TEST_CHECK_CERTIFICATE_KEY == kv['TEST_READ_CERTIFICATE_KEY']:
            result['TEST_CHECK_CERTIFICATE_KEY'] = True

        TEST_CHECK_NLWEAVEPROVISIONINGHASH = sfis.get_mlb_snx(isn60, 'SND')
        logV('TEST_CHECK_NLWEAVEPROVISIONINGHASH: [%s] , [%s] ,[%s]' % (TEST_CHECK_NLWEAVEPROVISIONINGHASH , kv['TEST_GENERATE_NLWEAVEPROVISIONINGHASH'],kv['TEST_READ_NLWEAVEPROVISIONINGHASH']))
        if TEST_CHECK_NLWEAVEPROVISIONINGHASH == kv['TEST_GENERATE_NLWEAVEPROVISIONINGHASH'] and TEST_CHECK_NLWEAVEPROVISIONINGHASH == kv['TEST_READ_NLWEAVEPROVISIONINGHASH']:
            result['TEST_CHECK_NLWEAVEPROVISIONINGHASH'] = True
            logD(result)

        TEST_CHECK_NLHASHKEY = sfis.get_mlb_snx(isn60, 'SNE')
        logV('TEST_CHECK_NLHASHKEY :%s , %s' % (TEST_CHECK_NLHASHKEY , kv['TEST_READ_NLHASHKEY']))
        if TEST_CHECK_NLHASHKEY == kv['TEST_READ_NLHASHKEY']:
            result['TEST_CHECK_NLHASHKEY'] = True

        TEST_CHECK_NLWEAVEDEVICEID = sfis.get_mlb_snx(isn60, 'A13941')
        TEST_CHECK_NLWEAVEDEVICEID = ':'.join(TEST_CHECK_NLWEAVEDEVICEID[i:i+2] for i in range(0,16,2))
        logV('TEST_CHECK_NLWEAVEDEVICEID :%s , %s' % (TEST_CHECK_NLWEAVEDEVICEID , kv['TEST_READ_NLWEAVEDEVICEID']))
        if TEST_CHECK_NLWEAVEDEVICEID == kv['TEST_READ_NLWEAVEDEVICEID']:
            result['TEST_CHECK_NLWEAVEDEVICEID'] = True
        

        TEST_CHECK_MODEL_SWITCH = sfis.get_mlb_snx(isn60, 'SNF')
        logV('%s , %s' % (TEST_CHECK_MODEL_SWITCH , kv['TEST_READ_MODEL_SWITCH']))
        if TEST_CHECK_MODEL_SWITCH == kv['TEST_READ_MODEL_SWITCH']:
            result['TEST_CHECK_MODEL_SWITCH'] = True

        TEST_CHECK_BUILD_EVENT = sfis.get_mlb_snx(isn60, 'SNG')
        logV('%s , %s' % (TEST_CHECK_BUILD_EVENT , kv['TEST_READ_BUILD_EVENT']))
        if TEST_CHECK_BUILD_EVENT == kv['TEST_READ_BUILD_EVENT']:
            result['TEST_CHECK_BUILD_EVENT'] = True

        return result





    def checkSysEnv(self,argv):
        testitems=['TEST_CHECK_MODEL_SWITCH',
                    'TEST_CHECK_CONFIG_SWTICH_MLB',
                   'TEST_CHECK_CONFIG_SWTICH_FATP',
                    'TEST_CHECK_BUILD_EVENT',
                    'TEST_CHECK_ISN_SWTICH_MLB',
                   'TEST_CHECK_ISN_SWTICH_FATP',
                    'TEST_CHECK_NLWEAVEDEVICEID',
                   'TEST_CHECK_NLHASHKEY',
                    'TEST_CHECK_CERTIFICATE_KEY',
                    'TEST_CHECK_NLWEAVEPRIVATEKEY',
                    'TEST_CHECK_NLWEAVEPROVISIONINGHASH']
        
        result = self.testCheckValueByOne(self.kv)
        logV(result)
        for item in testitems:
            if result[item]:
                DATA.op('%s_P1,0,PASS,N/A,N/A' % (item))
            else:
                DATA.op('%s_P1,1,FAIL,N/A,N/A' % (item))
        if self.gang==2:
            result2 = self.testCheckValueByOne(self.kv2)
            for item in testitems:
                if result[item]:
                    DATA.op('%s_P2,0,PASS,N/A,N/A' % (item))
                else:
                    DATA.op('%s_P2,1,FAIL,N/A,N/A' % (item))

    def callexe(self,argv):
        cmd = argv['exe']
        has = argv['has']
        realcmd = cmd.replace('COM?',self.comid)
        rt  = self.callexebyone(realcmd,has)
        if rt:
            DATA.op('%s_P1,0,PASS,N/A,N/A' % argv['name'])
        else:
            DATA.op('%s_P1,1,FAIL,N/A,N/A' % argv['name'])

        if self.gang==2:
            realcmd = cmd.replace('COM?', self.comid2)
            rt = self.callexebyone(realcmd, has)
            if rt:
                DATA.op('%s_P2,0,PASS,N/A,N/A' % argv['name'])
            else:
                DATA.op('%s_P2,1,FAIL,N/A,N/A' % argv['name'])

    def callexebyone(self,cmd,has):
        rtbuf=''
        logV(cmd)
        try:
            p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)

            while True:
                buf = p.stdout.readline()
                if not buf:
                    break
                logV(buf)
                rtbuf+=buf
                time.sleep(0.005)
            logV('return code:', p.returncode)
            if not rtbuf.find(has)>=0:
                return False
            else:
                return True
        except Exception,e:
            logV(Exception,e)
            return False
            return ''

    def open_com_port(self,argv):
        try:
            self.dut._connect()
            DATA.op('%s_P1,0,PASS,N/A,N/A' % (argv['name']))
        except:
            DATA.op('%s_P1,1,FAIL,N/A,N/A'%(argv['name']))
        if self.gang==2:
            try:
                self.dut2._connect()
                DATA.op('%s_P2,0,PASS,N/A,N/A' % (argv['name']))
            except:
                DATA.op('%s_P2,1,FAIL,N/A,N/A' % (argv['name']))

    def close_com_port(self,argv):
        self.dut.disconnect()
        DATA.op('%s_P1,0,PASS,N/A,N/A' % (argv['name']))
        if self.gang==2:
            self.dut2.disconnect()
            DATA.op('%s_P2,0,PASS,N/A,N/A' % (argv['name']))

    def send_cmd(self,argv):
        cmd=argv['cmd'].encode('ascii')
        try:
            end=argv['end']
        except:
            end=''
        try:
            has=argv['has']
        except:
            has=''
        try:
            timeout=argv['timeout']
        except:
            timeout=1
        r,v=self.dut.wr(cmd,end,has,timeout)
        logV(r,repr(v))
        if r:
            DATA.op(argv['name'] + '_P1,0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + '_P1,1,FAIL,N/A,N/A')
        if self.gang==2:
            r, v = self.dut2.wr(cmd, end, has, timeout)
            logV(r, repr(v))
            if r:
                DATA.op(argv['name'] + '_P2,0,PASS,N/A,N/A')
            else:
                DATA.op(argv['name'] + '_P2,1,FAIL,N/A,N/A')


