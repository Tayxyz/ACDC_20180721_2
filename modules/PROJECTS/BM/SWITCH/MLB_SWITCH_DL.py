from data import *
from IO.rs232 import RS232

class dl():
    def __init__(self,argv):
        self.io=RS232(argv)


    def GetMiddleStr(self,content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
            endIndex = content.index(endStr,startIndex)
            return content[startIndex:endIndex]
        else:
            return ''

    def write_sysenv(self,argv):
        self.env_cmds = {
                         'TEST_WRITE_IMAGE_SWITCH_MLB': 'sysenv set image 1\r',
                         'TEST_WRITE_NLMODEL_SWITCH_MLB': 'sysenv set nlmodel Tiros-1.1\r',

                         'TEST_WRITE_CONFIG_SWITCH_MLB': 'sysenv set  mlbconfig %s\r'%DATA.mlbconfig.encode('ascii'),
                         'TEST_WRITE_BUILDEVENT_SWITCH_MLB': 'sysenv set build_event EVT\r',
                         'TEST_WRITE_ISN_SWITCH_MLB': 'sysenv set mlb# %s\r'%DATA.isn,
                         'TEST_WRITE_NLWEAVEDEVICEID_SWITCH_MLB': 'sysenv set nlWeaveDeviceId %s\r'%DATA.MAC_6LOWPAN.encode('ascii'),
                         'TEST_WRITE_NLWEAVECERTIFICATE_SWITCH_MLB': 'sysenv set nlWeaveCertificate %s\r'%DATA.nlWeaveCertificate.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPRIVATEKEY_SWITCH_MLB': 'sysenv set nlWeavePrivateKey %s\r' % DATA.nlWeavePrivateKey.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPAIRINGCODE_SWITCH_MLB': 'sysenv set nlWeavePairingCode %s\r' % DATA.nlWeavePairingCode.encode('ascii'),
                         'TEST_WRITE_NLWEAVEPROVISIONINGHASH_SWITCH_MLB': 'sysenv set nlWeaveProvisioningHash %s\r' % DATA.nlWeaveProvisioningHash.encode('ascii')
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

    def read_env(self,argv):
        self.env_cmds = {'TEST_READ_NLMODEL_SWITCH_MLB': 'sysenv get nlmodel\r',
                         'TEST_READ_CONFIG_SWITCH_MLB': 'sysenv get mlbconfig\r',
                         'TEST_READ_BUILDEVENT_SWITCH_MLB': 'sysenv get build_event\r',
                         'TEST_READ_ISN_SWITCH_MLB': 'sysenv get mlb#\r',
                         'TEST_READ_NLWEAVEDEVICEID_SWITCH_MLB': 'sysenv get nlWeaveDeviceId\r',
                         'TEST_READ_NLWEAVECERTIFICATE_SWITCH_MLB': 'sysenv get nlWeaveCertificate\r',
                         'TEST_READ_NLWEAVEPRIVATEKEY_SWITCH_MLB': 'sysenv get nlWeavePrivateKey\r',
                         'TEST_READ_NLWEAVEPAIRINGCODE_SWITCH_MLB': 'sysenv get nlWeavePairingCode\r',
                         'TEST_READ_NLWEAVEPROVISIONINGHASH_SWITCH_MLB': 'sysenv get nlWeaveProvisioningHash\r'
                         }
        self.env_kv = {'TEST_READ_NLMODEL_SWITCH_MLB': 'Tiros-1.1',
                         'TEST_READ_CONFIG_SWITCH_MLB': DATA.mlbconfig.encode('ascii'),
                         'TEST_READ_BUILDEVENT_SWITCH_MLB': 'EVT',
                         'TEST_READ_ISN_SWITCH_MLB': DATA.isn,
                         'TEST_READ_NLWEAVEDEVICEID_SWITCH_MLB': DATA.MAC_6LOWPAN.encode('ascii'),
                         'TEST_READ_NLWEAVECERTIFICATE_SWITCH_MLB': DATA.nlWeaveCertificate.encode('ascii'),
                         'TEST_READ_NLWEAVEPRIVATEKEY_SWITCH_MLB': DATA.nlWeavePrivateKey.encode('ascii'),
                         'TEST_READ_NLWEAVEPAIRINGCODE_SWITCH_MLB': DATA.nlWeavePairingCode.encode('ascii'),
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


