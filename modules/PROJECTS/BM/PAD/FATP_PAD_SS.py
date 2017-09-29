from data import *
from IO.rs232 import RS232
import time
from PROJECTS.BM.PAD.ssh2linux import ssh2linux

class ss():
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

    def dfu(self,argv):
        s2l = ssh2linux({})
        s2l.login()
        time.sleep(2)

    def flash(self,argv):
        s2l = ssh2linux({})
        try:
            s2l.flash({})
        except Exception,e:
            logE(Exception,e)

    def update(self,argv):
        s2l = ssh2linux({})
        try:
            s2l.update({})
        except Exception,e:
            logE(Exception,e)

    def read_env(self,argv):
        self.env_keys=['ISN_MLB',
                       'ISN_FATP',
                       'CONFIG_FATP',
                       'NLWEAVEPRIVATEKEY',
                       'NLWEAVECERTIFICATE',
                       'NLWEAVEPAIRINGCODE',
                       'WIFI_MAC',
                       '6LOWPAN_MAC',
                       'NLMODEL',
                       'MLBCONFIG',
                       'BUILD_EVENT',
                       'BUILD_DATE',
                       'GANG_NUM']
        self.test_items = {'ISN_MLB': 'TEST_READ_ISN_PAD_MLB',
                         'ISN_FATP': 'TEST_READ_ISN_PAD_FATP',
                         'CONFIG_FATP': 'TEST_READ_CONFIG_PAD_FATP',
                         'NLWEAVEPRIVATEKEY': 'TEST_READ_NLWEAVEPRIVATEKEY',
                         'NLWEAVECERTIFICATE': 'TEST_READ_NLWEAVECERTIFICATE',
                         'NLWEAVEPAIRINGCODE': 'TEST_READ_NLWEAVEPAIRINGCODE',
                         'WIFI_MAC': 'TEST_READ_WIFI_MAC',
                         '6LOWPAN_MAC': 'TEST_READ_6LOWPAN_MAC',
                         'NLMODEL':'TEST_READ_NLMODEL',
                         'MLBCONFIG':'TEST_READ_MLBCONFIG',
                         'BUILD_EVENT':'TEST_READ_BUILD_EVENT',
                         'BUILD_DATE':'TEST_READ_BUILD_DATE',
                         'GANG_NUM':'TEST_READ_GANG_NUM' }
        self.env_cmds={'ISN_MLB':'nlcli env get mlb#\r',
                       'ISN_FATP': 'nlcli env get serial#\r',
                       'CONFIG_FATP': 'nlcli env get config\r',
                       'NLWEAVEPRIVATEKEY': 'nlcli env get nlWeavePrivateKey\r',
                       'NLWEAVECERTIFICATE': 'nlcli env get nlWeaveCertificate\r',
                       'NLWEAVEPAIRINGCODE': 'nlcli env get nlWeavePairingCode\r',
                       'WIFI_MAC': 'nlcli env get ethaddr\r',
                       '6LOWPAN_MAC': 'nlcli env get hwaddr1\r',
                       'NLMODEL': 'nlcli env get nlmodel\r',

                       'BUILD_EVENT': 'nlcli env get build_event\r',
                       'BUILD_DATE': 'nlcli env get build_date\r',
                       'GANG_NUM': 'nlcli env get gang_num\r',
                       'MLBCONFIG': 'nlcli env get mlbconfig\r'}
        self.env_kv={'ISN_MLB': 'NA',
                         'ISN_FATP': 'NA',
                         'CONFIG_FATP': 'NA',
                         'NLWEAVEPRIVATEKEY': 'NA',
                         'NLWEAVECERTIFICATE': 'NA',
                         'NLWEAVEPAIRINGCODE': 'NA',
                         'WIFI_MAC': 'NA',
                         '6LOWPAN_MAC': 'NA',
                         'NLMODEL':'NA',
                         'MLBCONFIG':'NA',
                         'BUILD_EVENT':'NA',
                         'BUILD_DATE':'NA',
                         'GANG_NUM':'NA' }
        self.io._connect()
        logV(self.io.wr('root\r', '# '))
        for key in self.env_keys:
            cmd=self.env_cmds[key]
            for i in range(5):
                rt,v=self.io.wr(cmd,'# ','=',1)
                if rt:
                    break
            logV('\n--- ::', self.test_items[key],' : ',cmd)
            logV(rt,v)
            if not rt:
                DATA.op(self.test_items[key]+',1,FAIL,N/A,N/A')
            else:
                value=self.GetMiddleStr(v,'=','\r').strip()
                if len(value)==0:
                    DATA.op(self.test_items[key] + ',1,NA,N/A,N/A')
                else:
                    DATA.op(self.test_items[key] +',0,'+value +',N/A,N/A')
                    self.env_kv[key]=value
            time.sleep(0.1)

        rt, v = self.io.wr('devdesc\r', '# ', '', 1)
        if rt:
            value = self.GetMiddleStr(v, 'devdesc\r', '\r').strip()
            logV('QRC:',rt,v,value)
            if len(value)==72:
                self.qrc=value
                DATA.save_more='#SAVE:SND:A,0,%s,N/A,N/A\n'%value
                DATA.op('QRCODE,0,%s,N/A,N/A'%value)
                return
        DATA.op('QRCODE,1,FAIL,N/A,N/A')


    def set_read_nlwirelessregdom(self,argv):
        #cmds=['nlcli env set nlwirelessregdom A2\r','nlcli env get nlwirelessregdom\r']
        r,v=self.io.wr('nlcli env set nlwirelessregdom A2\r','# ')
        logV(r, v)
        if r:
            DATA.op('TEST_WRITE_NLWIRELESSREGDOM,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_WRITE_NLWIRELESSREGDOM,1,FAIL,N/A,N/A')
        r, v = self.io.wr('nlcli env get nlwirelessregdom\r', '# ','nlwirelessregdom=A2')
        logV(r, v)
        if r:
            DATA.op('TEST_READ_NLWIRELESSREGDOM,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_READ_NLWIRELESSREGDOM,1,FAIL,N/A,N/A')

    def set_read_nldestcountry(self,argv):
        #cmds=['nlcli env set nldestcountry US\r','nlcli env set nldestcountry\r']
        r, v = self.io.wr('nlcli env set nldestcountry US\r', '# ')
        logV(r, v)
        if r:
            DATA.op('TEST_WRITE_NLDESTCOUNTRY,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_WRITE_NLDESTCOUNTRY,1,FAIL,N/A,N/A')
        r, v = self.io.wr('nlcli env get nldestcountry\r', '# ', 'nldestcountry=US')
        logV(r, v)
        if r:
            DATA.op('TEST_READ_NLDESTCOUNTRY,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_READ_NLDESTCOUNTRY,1,FAIL,N/A,N/A')

    def check_env(self,argv):
        self.test_check_items = {'ISN_MLB': 'TEST_CHECK_ISN_PAD_MLB',#80GET69
                           'ISN_FATP': 'TEST_CHECK_ISN_PAD_FATP',#SCAN
                           'CONFIG_FATP': 'TEST_CHECK_CONFIG_PAD_FATP',#80 GET CONFIG
                           'NLWEAVEPRIVATEKEY': 'TEST_CHECK_NLWEAVEPRIVATEKEY',#69 SNA
                           'NLWEAVECERTIFICATE': 'TEST_CHECK_NLWEAVECERTIFICATE',#69 SNB
                           'NLWEAVEPAIRINGCODE': 'TEST_CHECK_NLWEAVEPAIRINGCODE',#69 SNC
                           'WIFI_MAC': 'TEST_CHECK_WIFI_MAC',#69 MAC1
                           '6LOWPAN_MAC': 'TEST_CHECK_6LOWPAN_MAC',#69 A1394
                           'NLMODEL': 'TEST_CHECK_NLMODEL', #69 SNE
                           'MLBCONFIG': 'TEST_CHECK_MLBCONFIG',#69 GET CONFIG
                           'BUILD_EVENT': 'TEST_CHECK_BUILD_EVENT',#69 SND
                           'BUILD_DATE': 'TEST_CHECK_BUILD_DATE',#80 SNA
                           'GANG_NUM': 'TEST_CHECK_GANG_NUM' #80 SNC
                                 }
        self.isn80=DATA.isn
        if DATA.isn==self.env_kv['ISN_FATP']:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,1,FAIL,N/A,N/A')

        sfis=DATA.objs['sfis']
        logD(type(sfis))
        self.isn69=sfis.get69by80(self.isn80)
        if self.isn69==self.env_kv['ISN_MLB']:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,1,FAIL,N/A,N/A')

        CONFIG_FATP=sfis.get_config(self.isn80)
        if CONFIG_FATP==self.env_kv['CONFIG_FATP']:
            DATA.op('TEST_CHECK_CONFIG_PAD_FATP,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_CONFIG_PAD_FATP,1,FAIL,N/A,N/A')

        MLBCONFIG = sfis.get_mlb_pre_config(self.isn69)
        if MLBCONFIG == self.env_kv['MLBCONFIG']:
            DATA.op('TEST_CHECK_CONFIG_PAD_MLB,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_CONFIG_PAD_MLB,1,FAIL,N/A,N/A')

        NLWEAVEPRIVATEKEY=sfis.get_mlb_snx(self.isn69,'SNC')
        if NLWEAVEPRIVATEKEY==self.env_kv['NLWEAVEPRIVATEKEY']:
            DATA.op('TEST_CHECK_NLWEAVEPRIVATEKEY,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_NLWEAVEPRIVATEKEY,1,FAIL,N/A,N/A')

        NLWEAVECERTIFICATE = sfis.get_mlb_snx(self.isn69, 'SNB')
        if NLWEAVECERTIFICATE == self.env_kv['NLWEAVECERTIFICATE']:
            DATA.op('TEST_CHECK_NLWEAVECERTIFICATE,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_NLWEAVECERTIFICATE,1,FAIL,N/A,N/A')

        NLWEAVEPAIRINGCODE = sfis.get_mlb_snx(self.isn69, 'SNA')
        if NLWEAVEPAIRINGCODE == self.env_kv['NLWEAVEPAIRINGCODE']:
            DATA.op('TEST_CHECK_NLWEAVEPAIRINGCODE,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_NLWEAVEPAIRINGCODE,1,FAIL,N/A,N/A')

        BUILD_EVENT = sfis.get_mlb_snx(self.isn69, 'SND')
        if BUILD_EVENT == self.env_kv['BUILD_EVENT']:
            DATA.op('TEST_CHECK_BUILD_EVENT,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_BUILD_EVENT,1,FAIL,N/A,N/A')

        NLMODEL = sfis.get_mlb_snx(self.isn69, 'SNE')
        if NLMODEL == self.env_kv['NLMODEL']:
            DATA.op('TEST_CHECK_NLMODEL,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_NLMODEL,1,FAIL,N/A,N/A')

        # BUILD_DATE = sfis.get_mlb_snx(self.isn80, 'SNA')
        # if BUILD_DATE == self.env_kv['BUILD_DATE']:
        #     DATA.op('TEST_CHECK_BUILD_DATE,0,PASS,N/A,N/A')
        # else:
        #     DATA.op('TEST_CHECK_BUILD_DATE,1,FAIL,N/A,N/A')
        DATA.op('TEST_CHECK_BUILD_DATE,0,SKIP,N/A,N/A')

        GANG_NUM = '2'
        #sfis.get_mlb_snx(self.isn80, 'SNC')
        if GANG_NUM == self.env_kv['GANG_NUM']:
            DATA.op('TEST_CHECK_GANG_NUM,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_GANG_NUM,1,FAIL,N/A,N/A')

        WIFI_MAC = sfis.get_mlb_snx(self.isn69, 'MAC1')
        WIFI_MAC=':'.join(WIFI_MAC[i:i+2] for i in range(0,12,2))
        if WIFI_MAC == self.env_kv['WIFI_MAC']:
            DATA.op('TEST_CHECK_WIFI_MAC,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_WIFI_MAC,1,FAIL,N/A,N/A')

        SIXLOWPAN_MAC = sfis.get_mlb_snx(self.isn69, 'A13941')
        SIXLOWPAN_MAC = ':'.join(SIXLOWPAN_MAC[i:i + 2] for i in range(0, 16, 2))
        if SIXLOWPAN_MAC == self.env_kv['6LOWPAN_MAC']:
            DATA.op('TEST_CHECK_6LOWPAN_MAC,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_6LOWPAN_MAC,1,FAIL,N/A,N/A')



    def system_halt(self,argv):
        cmd='/sbin/halt\r'
        r, v = self.io.wr(cmd, '# ')
        self.io.disconnect()
        if r:
            DATA.op('SYSTEM_HALT,0,PASS,N/A,N/A')
        else:
            DATA.op('SYSTEM_HALT,1,FAIL,N/A,N/A')
