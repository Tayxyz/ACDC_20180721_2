from data import *
from IO.rs232 import RS232
import time
import subprocess
import serial
import COMMON.dialog as dialog

class MLB_SWDL:
    def __init__(self,argv):
        try:
            com=argv['com']
        except:
            com='COM23'
        try:
            self.dut= RS232(argv)
            self.dut._connect()
        except Exception as e:
            d = dialog({})
            d.info({Exception: e})

    def openDLTool(self,argv):
        try:
            boottool=argv['boottool']
        except:
            boottool='D:\\preEVT\\win-virgin-dfu-1.0d1-msevt-17-moonstone-diagnostics-0NUG\\MfgTool2.exe -autostart'
        try:
            import subprocess
            sp = subprocess.Popen(boottool, shell=True, stdout=subprocess.PIPE)

        except Exception,e:
            print Exception,e


    def waitDLDone(self,argv):
        try:
            timeout=argv['timeout']
        except:
            timeout=150
        try:
            has = argv['has']
        except:
            has ='Update Complete!'

        t0 = time.time()
        rt = ''
        while time.time() - t0 < timeout:
            try:
                tmp = self.dut.io.readall()
                if len(tmp) > 0:
                    logV(tmp)
                    rt += tmp
                if tmp.find(has) >= 0 or rt.find(has)>=0:
                    return True
            except:
                pass
        logE(rt, 'timeout..')
        return False

    def waitForReBoot(self,argv):
        try:
            timeout=argv['timeout']
        except:
            timeout=120
        try:
            has = argv['has']
        except:
            has ='moonstone login:'
        t0=time.time()
        rt=''
        while time.time()-t0<timeout:
            try:
                tmp=self.dut.io.readall()
                if len(tmp)>0:
                    logV(tmp)
                    rt +=tmp
                if tmp.find(has)>=0 or rt.find(has):
                    self.dut.wr('root\r','# ')
                    return True
            except:
                pass
        logE(rt,'timeout..')
        return False

    def killDLTool(self,argv):
        try:
            subprocess.Popen("taskkill /F /IM MfgTool2.exe")
        except Exception, e:
            pass

    def swdl_mcu(self,argv):
        self.io._connect()
        logV(self.io.wr('root\r', '# '))
        logV(self.io.wr('nlcli pad -b; sleep 1; stm32flash -o /dev/ttysensormcu0\r', '# ',timeout=20))
        logV(self.io.wr('nlcli pad -u /usr/share/msmcu/data/firmware/moonstone.bin /dev/ttysensormcu0\r', '# ',has='Done',timeout=200))
        self.io.disconnect()

    def swdl_write_sysenv(self,argv):
        self.env_cmds = {
                         'TEST_WRITE_BUILD_PHASE_PAD_MLB':'nlcli env set build_phase %s\r'%DATA.build_phase.encode('ascii'),
                         'TEST_WRITE_CONFIG_PAD_MLB': 'nlcli env set mlbconfig %s\r' % DATA.mlbconfig.encode('ascii'),
                         'TEST_WRITE_6LOWPAN_MAC_PAD_MLB': 'nlcli env set hwaddr1 %s\r' % DATA.MAC_6LOWPAN.encode('ascii'),
                         'TEST_WRITE_WIFI_MAC_PAD_MLB': 'nlcli env set ethaddr %s\r' % DATA.MAC_WIFI.encode('ascii'),
                         'TEST_WRITE_MODEL_PAD_MLB': 'nlcli env set nlmodel Moonstone-1.1\r',
                         'TEST_WRITE_BUILD_EVENT_PAD_MLB': 'nlcli env set build_event EVT\r',
                         'TEST_WRITE_ISN_PAD_MLB': 'nlcli env set mlb# %s\r'%DATA.isn,

                         'TEST_WRITE_NLWEAVECERTIFICATE_SWITCH_MLB': 'nlcli env set nlWeaveCertificate %s\r'%DATA.nlWeaveCertificate.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPRIVATEKEY_SWITCH_MLB': 'nlcli env set nlWeavePrivateKey %s\r' % DATA.nlWeavePrivateKey.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPAIRINGCODE_SWITCH_MLB': 'nlcli env set nlWeavePairingCode %s\r' % DATA.nlWeavePairingCode.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPROVISIONINGHASH_SWITCH_MLB': 'nlcli env set nlWeaveProvisioningHash %s\r' % DATA.nlWeaveProvisioningHash.encode('ascii')
                         }
        self.io._connect()
        logV(self.io.wr('root\r', '# '))
        for key in self.env_cmds.keys():
            cmd=self.env_cmds[key]
            for i in range(5):
                rt,v=self.io.wr(cmd,'# ','# ',1)
                if rt:
                    break
            logV('\n--- ::', key,' : ',cmd)
            logV(rt,v)
            if not rt:
                DATA.op(key+',1,FAIL,N/A,N/A')
            else:
                DATA.op(key + ',0,PASS,N/A,N/A')

    def swdl_read_env(self,argv):
        self.env_cmds = {
            'TEST_READ_BUILD_PHASE_PAD_MLB': 'nlcli env get build_phase\r',
            'TEST_READ_CONFIG_PAD_MLB': 'nlcli env get mlbconfig\r',
            'TEST_READ_6LOWPAN_MAC_PAD_MLB': 'nlcli env get hwaddr1\r',
            'TEST_READ_WIFI_MAC_PAD_MLB': 'nlcli env get ethaddr\r',
            'TEST_READ_MODEL_PAD_MLB': 'nlcli env get nlmodel\r',
            'TEST_READ_BUILD_EVENT_PAD_MLB': 'nlcli env get build_event\r',
            'TEST_READ_ISN_PAD_MLB': 'nlcli env get mlb#\r',

            'TEST_READ_NLWEAVECERTIFICATE_SWITCH_MLB': 'nlcli env get nlWeaveCertificate\r',
            'TEST_READ_NLWEAVEPRIVATEKEY_SWITCH_MLB': 'nlcli env get nlWeavePrivateKey\r',
            'TEST_READ_NLWEAVEPAIRINGCODE_SWITCH_MLB': 'nlcli env get nlWeavePairingCode\r',
            'TEST_READ_NLWEAVEPROVISIONINGHASH_SWITCH_MLB': 'nlcli env get nlWeaveProvisioningHash\r'
        }
        self.env_kv = {  'TEST_READ_BUILD_PHASE_PAD_MLB':DATA.build_phase.encode('ascii'),
                         'TEST_READ_CONFIG_PAD_MLB': DATA.mlbconfig.encode('ascii'),
                         'TEST_READ_6LOWPAN_MAC_PAD_MLB':  DATA.MAC_6LOWPAN.encode('ascii'),
                         'TEST_READ_WIFI_MAC_PAD_MLB': DATA.MAC_WIFI.encode('ascii'),
                         'TEST_READ_MODEL_PAD_MLB': 'Moonstone-1.1',
                         'TEST_READ_BUILD_EVENT_PAD_MLB': 'EVT',
                         'TEST_READ_ISN_PAD_MLB': DATA.isn,

                         'TEST_READ_NLWEAVECERTIFICATE_SWITCH_MLB': DATA.nlWeaveCertificate.encode('ascii'),
                         'TEST_READ_NLWEAVEPRIVATEKEY_SWITCH_MLB':  DATA.nlWeavePrivateKey.encode('ascii'),
                         'TEST_READ_NLWEAVEPAIRINGCODE_SWITCH_MLB':  DATA.nlWeavePairingCode.encode('ascii'),
                         'TEST_READ_NLWEAVEPROVISIONINGHASH_SWITCH_MLB': DATA.nlWeaveProvisioningHash.encode('ascii')
                         }

        for key in self.env_cmds.keys():
            cmd=self.env_cmds[key]
            for i in range(5):
                rt,v=self.io.wr(cmd,'# ','# ',1)
                if rt:
                    break
            logV('\n--- ::', key,' : ',cmd)
            logV(rt,v)
            if not rt:
                DATA.op(key+',1,FAIL,N/A,N/A')
            else:
                if v.find(self.env_kv[key])>=0:
                    DATA.op(key + ',0,%s,N/A,N/A'%self.env_kv[key])
                else:
                    DATA.op(key + ',1,%s,N/A,N/A'%self.env_kv[key])

        self.io.disconnect()
