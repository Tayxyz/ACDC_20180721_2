from data import *
from IO.rs232 import RS232
import time
from PROJECTS.BM.PAD.ssh2linux import ssh2linux
import COMMON.dialog as dialog
import subprocess

class ss():
    def __init__(self,argv):
        self.io=RS232({'COM':argv['COM'][str(DATA.id)]})
        self.hub_port = argv['hub_port'][str(DATA.id)]

    def GetMiddleStr(self,content, startStr, endStr):
        startIndex = content.find(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
            endIndex = content.find(endStr, startIndex)
            if endIndex >= 0:
                return content[startIndex:endIndex]
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

    def waitForBoot(self,argv):
        s2l = ssh2linux({})
        try:
            rt=s2l.waitForBoot(argv)
            if not rt:
                DATA.op('BOOT,1,FAIL,N/A,N/A')
            else:
                DATA.op('BOOT,0,PASS,N/A,N/A')
        except Exception, e:
            logE(Exception, e)

    def swdl_waitForReBoot(self,argv):
        t0=time.time()
        self.io._connect()
        rt=''
        while time.time()-t0<120:
            try:
                tmp=self.io.com.readall()
                if len(tmp)>0:
                    logV(tmp)
                    rt +=tmp
                if tmp.find('moonstone login:')>=0:
                    self.io.com.write('root\r')
                    self.io.disconnect()
                    return True
            except:
                pass
            #time.sleep(0.3)
        logE(rt,'timeout..')
        self.io.disconnect()
        return False

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
        #1P:18$R:1$S:21AA01AC3817004K$L:64166600000F57D8$W:6416660F4525$C:FFR02F$
        self.qrc='1P:18$R:1$S:'+self.env_kv['ISN_FATP']+'$L:'+self.env_kv['6LOWPAN_MAC']+'$W:'+self.env_kv['WIFI_MAC']+'$C:'+self.env_kv['NLWEAVEPAIRINGCODE']+'$'
        if len(self.qrc) == 72:
            DATA.save_more = '#SAVE:SND:A,0,%s,N/A,N/A\n' % value
            DATA.op('QRCODE,0,%s,N/A,N/A' % value)
            return
        DATA.op('QRCODE,1,FAIL,N/A,N/A')


    def set_read_nlwirelessregdom(self,argv):
        #cmds=['nlcli env set nlwirelessregdom A2\r','nlcli env get nlwirelessregdom\r']
        self.io._connect()
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
        self.io.disconnect()

    def set_read_nldestcountry(self,argv):
        #cmds=['nlcli env set nldestcountry US\r','nlcli env set nldestcountry\r']
        self.io._connect()
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
        self.io.disconnect()

    def optest(self,argv):
        'nlcli pad -c version =1.5'
        cmd = 'nlcli pad -c version\r'
        r, v = self.io.wr(cmd, '# ')
        logV(r, v)
        'nlcli pad -c "p w g 12 1"'
        cmd = 'nlcli pad -c "p w g 12 1"\r'
        r, v = self.io.wr(cmd, '# ')
        logV(r, v)

        closeLedCmd=['nlcli pad -c "led_white 0 0 ff 0"\r',
                     'nlcli pad -c "led_rgb 0 0 0 0 0 0"\r']
        for cmd in closeLedCmd:
            r, v = self.io.wr(cmd, '# ')
            logV(r, v)
        redLedCmd=['nlcli pad -c "led_rgb 1 0 ff 0 0 1ff"\r',
                   'nlcli pad -c "led_rgb 1 0 0 0 0 1ff"\r',
                   'nlcli pad -c "led_rgb 2 0 ff 0 0 1ff"\r',
                   'nlcli pad -c "led_rgb 2 0 0 0 0 1ff"\r'
        ]
        greenLedCmd=[
            'nlcli pad -c "led_rgb 1 0 0 ff 0 1ff"\r',
            'nlcli pad -c "led_rgb 1 0 0 0 0 1ff"\r',
            'nlcli pad -c "led_rgb 2 0 0 ff 0 1ff"\r',
            'nlcli pad -c "led_rgb 2 0 0 0 0 1ff"\r'
        ]
        blueLedCmd=[
            'nlcli pad -c "led_rgb 1 0 0 0 ff 1ff"\r',
            'nlcli pad -c "led_rgb 1 0 0 0 0 1ff"\r',
            'nlcli pad -c "led_rgb 2 0 0 0 ff 1ff"\r',
            'nlcli pad -c "led_rgb 2 0 0 0 0 1ff"\r'
        ]
        whiteLedCmd=[
            'nlcli pad -c "led_white 1 0 ff 1ff"\r',
            'nlcli pad -c "led_white 1 0 ff 0"\r',
            'nlcli pad -c "led_white 2 0 ff 1ff"\r',
            'nlcli pad -c "led_white 2 0 ff 0"\r'
        ]
        ledCmds={
            'close':closeLedCmd,
            'red':redLedCmd,
            'green':greenLedCmd,
            'blue':blueLedCmd,
            'white':whiteLedCmd
        }
        ledColors=['red','green','blue','white']
        for color in ledColors:
            cmds=ledCmds[color]
            r, v = self.io.wr(cmds[0], '# ')
            logV(r, v)
            d = dialog.dialog({})
            r=d.yesorno({'msg':'left %s led?'%color})
            if r==0:
                DATA.op('LEFT_%s,0,PASS,N/A,N/A'%color)
            else:
                DATA.op('LEFT_%s,1,FAIL,N/A,N/A'%color)
            r, v = self.io.wr(cmds[1], '# ')
            logV(r, v)
            r, v = self.io.wr(cmds[2], '# ')
            logV(r, v)
            d = dialog.dialog({})
            r = d.yesorno({'msg': 'right %s led?' % color})
            if r == 0:
                DATA.op('RIGHT_%s,0,PASS,N/A,N/A' % color)
            else:
                DATA.op('RIGHT_%s,1,FAIL,N/A,N/A' % color)
            r, v = self.io.wr(cmds[3], '# ')
            logV(r, v)

        senseAll='nlcli pad -c senseAll\r'
        for i in range(5):
            r, v = self.io.wr(senseAll, '# ')
            logV(r, v)

        itg='nlcli pad -c itg\r'
        r, v = self.io.wr(itg, '# ')
        logV(r, v)
        ia='nlcli pad -c ia\r'
        r, v = self.io.wr(ia, '# ')
        logV(r, v)
        it0='nlcli pad -c it0\r'
        r, v = self.io.wr(it0, '# ')
        logV(r, v)
        ip='nlcli pad -c ip\r'
        r, v = self.io.wr(ip, '# ')
        logV(r, v)
        iif='nlcli pad -c if\r'
        r, v = self.io.wr(iif, '# ')
        logV(r, v)
        its='nlcli pad -c its 1\r'
        r, v = self.io.wr(its, '# ')
        logV(r, v)
        itall='nlcli pad -c itall\r'
        r, v = self.io.wr(itall, '# ')
        logV(r, v)
        ia1='nlcli pad -c ia\r'
        r, v = self.io.wr(ia1, '# ')
        logV(r, v)
        urt='nlcli uart /dev/ttysensormcu0 -p\r'
        r, v = self.io.wr(urt, '# ')
        logV(r, v)
        its0='its 0\r'
        for i in range(20):
            r, v = self.io.wr(its0, '>')
            logV(r, v)

    def system_halt(self,argv):
        'nlcli pad -c version =1.5'
        cmd = 'nlcli pad -c version\r'
        r, v = self.io.wr(cmd, '# ')
        logV(r, v)
        if r and v.find('1.5')>=0:
            DATA.op('MCU_VERSION,0,PASS,N/A,N/A')
        else:
            DATA.op('MCU_VERSION,1,FAIL,N/A,N/A')
        cmd='/sbin/halt\r'
        r, v = self.io.wr(cmd, '# ')
        self.io.disconnect()
        if r:
            DATA.op('SYSTEM_HALT,0,PASS,N/A,N/A')
        else:
            DATA.op('SYSTEM_HALT,1,FAIL,N/A,N/A')

    def printQRC(self,argv):
        subprocess.call('taskkill /F /IM MfgTool2.exe', shell=True)
        if DATA.totalfails > 0:
            DATA.op('PRINT_QRC,1,SKIP,N/A,N/A')
            return
        cmd='''^XA
                    ^LH166,30^FS
                    ^FO6,8
                    ^A0N,14,14^FDFATP_ISN^FS
                    ^FO10,22
                    ^BQN,2,3
                    ^FDQA,QRCODE^FS
                    ^FO43,160
                    ^A0N,16,16^FDPAIRINGCODE^FS
                    ^XZ'''
        cmd=cmd.replace('FATP_ISN',self.env_kv['ISN_FATP']).replace('QRCODE',self.qrc).replace('PAIRINGCODE',self.env_kv['NLWEAVEPAIRINGCODE'])
        with open('qrc.txt','w') as f:
            f.write(cmd)
        rc = subprocess.call('copy qrc.txt LPT1', shell=True)
        if rc==0:
            DATA.op('PRINT_QRC,0,OK,N/A,N/A')
        else:
            DATA.op('PRINT_QRC,1,FAIL,N/A,N/A')


    ####  EVT  ++
    def openDLTool(self,argv):
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        try:
            boottool=argv['boottool']
        except:
            boottool='D:\\preEVT\\win-virgin-dfu-1.0d1-msevt-17-moonstone-diagnostics-0NUG\\MfgTool2.exe -autostart'
        try:
            import subprocess
            if barrier:
                if barrier.acquire():
                        sp = subprocess.Popen(boottool, shell=True, stdout=subprocess.PIPE)
                        logV('I do it')
                else:
                    logV('bypass')
                barrier.release()
            else:
                sp = subprocess.Popen(boottool, shell=True, stdout=subprocess.PIPE)

        except Exception,e:
            print Exception,e

    def anyfail(self,fname):
        rt = True
        with open(fname) as fr:
            for line in fr:
                items = line.split(',')
                if len(items)<6:
                    return False
                if items[1]=='1':
                    return False
        return True


    def showinfo(self,argv):
        try:
            barrier = DATA.barriers[argv['barrier']]
        except:
            barrier = None
        if barrier:
            try:
                if barrier.acquire():
                    logs = ['csvforid1','csvforid2','csvforid3','csvforid4']
                    msg = ''
                    for idx in range(4):
                        try:
                            if self.anyfail(logs[idx]):
                                msg+= str(idx+1)+' '
                        except:
                            pass
                    msg = msg+'\n\n'+argv['msg']

                    dlg = dialog.dialog(argv)
                    dlg.info({'msg':msg})
                    logV('I do it')
                else:
                    logV('bypass')
            except Exception,e:
                logE(Exception,e)
            finally:
                barrier.release()
        else:
            dlg = dialog.dialog(argv)
            dlg.info(argv)
            logV('No barrier')


    def killDLTool(self,argv):
        try:
            barrier = DATA.barriers[argv['barrier']]
        except:
            barrier = None
        if barrier:
            if barrier.acquire():
                try:
                    subprocess.Popen("taskkill /F /IM MfgTool2.exe")
                    logV('I do it')
                except Exception, e:
                    pass
            else:
                logV('bypass')
            barrier.release()
        else:
            subprocess.Popen("taskkill /F /IM MfgTool2.exe")
            logV('No barrier')

    def waitDLDone(self,argv):
        time.sleep(10)
        timeout = int(argv['timeout'])
        newfindstr=findstr = '[WndIndex:%s], Body is $ (echo Update Complete!) || (. dfu-utils.sh dfu_end_fail)'
        hit1 = '-Port:'
        hit2 = '[WndIndex:'
        logfile = argv['log']
        logV(findstr)
        t0 = time.time()
        while time.time()-t0 <=timeout:
            with open(logfile) as fr:
                flag = 0
                findflag=0
                for line in fr:
                    if line.find(hit1) >= 0:
                        if line.find(self.hub_port) >= 0:
                            flag = 1
                        else:
                            flag = 0
                    if flag and findflag==0 and line.find(hit2) >= 0:
                        logV(line)
                        index = self.GetMiddleStr(line, hit2, ']')
                        logV(index)
                        newfindstr= findstr % index
                        logV(newfindstr)
                        findflag=1

                    if line.find(newfindstr)>0:
                        logV(line)
                        DATA.op(argv['name']+',0,PASS,N/A,N/A')
                        return
            time.sleep(1)
        DATA.op(argv['name'] + ',1,TimeOut,N/A,N/A')

    def waitForRebootAndSeeCOMPort(self,argv):
        time.sleep(3)
        #self.io = RS232(argv)
        timeout = int(argv['timeout'])
        t0 = time.time()
        while time.time() - t0 <= timeout:
            try:
                self.io.connect()
                time.sleep(1)
                self.io.disconnect()
                break
            except:
                time.sleep(1)
        else:
            DATA.op(argv['name'] + ',1,TimeOut,N/A,N/A')
            return
        DATA.op(argv['name'] + ',0,PASS,N/A,N/A')


    def readALLEnv(self,argv):
        #self.io = RS232(argv)
        item_names={
            'ISN_MLB':'TEST_READ_ISN_PAD_MLB', 'ISN_FATP':'TEST_READ_ISN_PAD_FATP',
            'MLBCONFIG':'TEST_READ_CONFIG_PAD_MLB', 'CONFIG_FATP':'TEST_READ_CONFIG_PAD_FATP',
            'BUILD_PHASE':'TEST_READ_BUILD_PHASE', 'NLMODEL':'TEST_READ_NLMODEL', 'BUILD_EVENT':'TEST_READ_BUILD_EVENT', 'BUILD_DATE':'TEST_READ_BUILD_DATE', 'GANG_NUM':'TEST_READ_GANG_NUM',
            'REL_STATUS':'TEST_READ_REL_STATUS',
            'ISN_IF':'TEST_READ_ISN_IF', 'ISN_BATTERY':'TEST_READ_ISN_BATTERY', 'ISN_PIR':'TEST_READ_ISN_PIR', 'ISN_PROXTALS':'TEST_READ_ISN_PROXTALS',
            'RF_CALL_11': 'TEST_READ_RF_CALL_11', 'RF_NP_US':'TEST_READ_RF_NP_US', 'RF_CAL_17':'TEST_READ_RF_CAL_17', 'RF_IBO':'TEST_READ_RF_IBO', 'RF_CAL_25':'TEST_READ_RF_CAL_25',
            'NLWEAVEPROVISIONINGHASH':'TEST_READ_NLWEAVEPROVISIONINGHASH',
            'NLWEAVEPRIVATEKEY':'TEST_READ_NLWEAVEPRIVATEKEY',
            'NLWEAVECERTIFICATE':'TEST_READ_NLWEAVECERTIFICATE',
            'NLWEAVEPAIRINGCODE':'TEST_READ_NLWEAVEPAIRINGCODE',
            'WIFI_MAC':'TEST_READ_WIFI_MAC',
            '6LOWPAN_MAC':'TEST_READ_6LOWPAN_MAC'
        }
        self.env_names = ['ISN_MLB','ISN_FATP',
                         'MLBCONFIG','CONFIG_FATP',
                          'BUILD_PHASE','NLMODEL','BUILD_EVENT','BUILD_DATE','GANG_NUM',
                          'REL_STATUS',
                          'ISN_IF', 'ISN_BATTERY','ISN_PIR','ISN_PROXTALS',
                          'RF_CALL_11','RF_NP_US','RF_CAL_17','RF_IBO','RF_CAL_25',
                          'NLWEAVEPROVISIONINGHASH',
                         'NLWEAVEPRIVATEKEY',
                         'NLWEAVECERTIFICATE',
                         'NLWEAVEPAIRINGCODE',
                         'WIFI_MAC',
                         '6LOWPAN_MAC']
        self.env_nvs = {}
        for name in self.env_names:
            self.env_nvs[name]='N/A'
        self.gen_hash='N/A'
        self.env_kvs = {}
        try:
            self.io.connect()
        except Exception,e:
            logE(Exception,e)
            DATA.op('TEST_OPEN_COM_PORT,1,FAIL,N/A,N/A')
            return
        DATA.op('TEST_OPEN_COM_PORT,0,PASS,N/A,N/A')
        r, v = self.io.wr('root\r', '# ', has='root@')
        logV(r, v)
        cmd = 'nlcli env\r'
        r,v = self.io.wr(cmd,'# ',has = 'root@')
        logV(r, v)
        #nlcli provisioning_hash
        rt,genhash = self.io.wr('nlcli provisioning_hash\r','# ',has = 'root@')
        logV(rt,genhash)
        self.gen_hash = genhash.split('\n')[-2].strip()
        DATA.op('TEST_GENERATE_NLWEAVEPROVISIONINGHASH,0,%s,N/A,N/A'%self.gen_hash)
        self.io.disconnect()

        
        

        self.env_name_keys={
            'ISN_MLB':'mlb#',
            'ISN_FATP':'serial#',
            'CONFIG_FATP':'config',
            'BUILD_PHASE':'build_phase',
            'REL_STATUS':'rel',
            'NLWEAVEPRIVATEKEY':'nlWeavePrivateKey',
            'NLWEAVECERTIFICATE':'nlWeaveCertificate',
            'NLWEAVEPAIRINGCODE':'nlWeavePairingCode',
            'NLWEAVEPROVISIONINGHASH':'nlWeaveProvisioningHash',
            'WIFI_MAC':'ethaddr',
            '6LOWPAN_MAC':'hwaddr1',
            'NLMODEL':'nlmodel',
            'MLBCONFIG':'mlbconfig',
            'BUILD_EVENT':'build_event',
            'BUILD_DATE':'build_date',
            'GANG_NUM':'gang_num',
            'ISN_IF':'if_brd#',
            'ISN_BATTERY':'battery#',
            'ISN_PIR':'pir_brd#',
            'ISN_PROXTALS':'prox_als_brd#',
            'RF_CALL_11':'nlwpandiags.nRF.calTable.11',
            'RF_NP_US':'nlwpandiags.nRF.nominalPower.US',
            'RF_CAL_17':'nlwpandiags.nRF.calTable.17',
            'RF_IBO':'nlwpandiags.nRF.installBackoff',
            'RF_CAL_25':'nlwpandiags.nRF.calTable.25'
        }

        try:
            lines = v.split('\n')
        except:
            lines = []
        for line in lines:
            if line.find('=')>0:
                item,value = line.strip().split('=',1)
                self.env_kvs[item]=value

        for name in self.env_names:
            if self.env_name_keys[name] in self.env_kvs.keys():
                v = self.env_kvs[self.env_name_keys[name]]
                if v.find(',')>=0:
                    v='\"[['+v+']]\"'
                DATA.op(item_names[name]+',0,'+v+',N/A,N/A')
                self.env_nvs[name]=v
            else:
                DATA.op(item_names[name] + ',0,N/A,N/A,N/A')
                self.env_nvs[name] = 'N/A'


    def check_env(self,argv):
        self.env_names = ['ISN_MLB', 'ISN_FATP',
                          'MLBCONFIG', 'CONFIG_FATP',
                          'BUILD_PHASE', 'NLMODEL', 'BUILD_EVENT', 'BUILD_DATE', 'GANG_NUM',
                          'REL_STATUS',
                          'ISN_IF', 'ISN_BATTERY', 'ISN_PIR', 'ISN_PROXTALS',
                          'RF_CALL_11', 'RF_NP_US', 'RF_CAL_17', 'RF_IBO', 'RF_CAL_25',
                          'NLWEAVEPROVISIONINGHASH',
                          'NLWEAVEPRIVATEKEY',
                          'NLWEAVECERTIFICATE',
                          'NLWEAVEPAIRINGCODE',
                          'WIFI_MAC',
                          '6LOWPAN_MAC']
        self.test_check_items = {'ISN_MLB': 'TEST_CHECK_ISN_PAD_MLB',  #80GET69
                           'ISN_FATP': 'TEST_CHECK_ISN_PAD_FATP',  #SCAN
                           'MLBCONFIG': 'TEST_CHECK_CONFIG_PAD_MLB',  # 69 GET CONFIG
                           'CONFIG_FATP': 'TEST_CHECK_CONFIG_PAD_FATP',  #80 GET CONFIG
                           'BUILD_PHASE': 'TEST_CHECK_BUILD_PHASE',#
                                 'NLMODEL': 'TEST_CHECK_NLMODEL',  # 69 SNE
                                 'BUILD_EVENT': 'TEST_CHECK_BUILD_EVENT',  # 69 SND
                                 'BUILD_DATE': 'TEST_CHECK_BUILD_DATE',  # 80 SNA
                                 'GANG_NUM': 'TEST_CHECK_GANG_NUM',  # 80 SNC
                                 'REL_STATUS': 'TEST_CHECK_REL_STATUS',
                                 'ISN_IF': 'TEST_CHECK_ISN_IF',#
                                 'ISN_BATTERY': 'TEST_CHECK_ISN_BATTERY',#
                                 'ISN_PIR': 'TEST_CHECK_ISN_PIR',#
                                 'ISN_PROXTALS': 'TEST_CHECK_ISN_PROXTALS',#
                                 'RF_CALL_11': 'TEST_CHECK_RF_CALL_11',#
                                 'RF_NP_US': 'TEST_CHECK_RF_NP_US',#
                                 'RF_CAL_17': 'TEST_CHECK_RF_CAL_17',#
                                 'RF_IBO': 'TEST_CHECK_RF_IBO',#
                                 'RF_CAL_25': 'TEST_CHECK_RF_CAL_25',
                                 'NLWEAVEPRIVATEKEY': 'TEST_CHECK_NLWEAVEPRIVATEKEY',  #69 SNA
                           'NLWEAVECERTIFICATE': 'TEST_CHECK_NLWEAVECERTIFICATE',  #69 SNB
                           'NLWEAVEPAIRINGCODE': 'TEST_CHECK_NLWEAVEPAIRINGCODE',  #69 SNC
                           'NLWEAVEPROVISIONINGHASH': 'TEST_CHECK_NLWEAVEPROVISIONINGHASH',  # 69 SNC
                           'WIFI_MAC': 'TEST_CHECK_WIFI_MAC',  #69 MAC1
                           '6LOWPAN_MAC': 'TEST_CHECK_6LOWPAN_MAC',  #69 A1394
                           }
        if len(self.env_nvs)==0:
            return
        self.isn80=DATA.isn
        logV('\n\n%s: %s =?= %s\n\n' % ('TEST_CHECK_ISN_PAD_FATP', DATA.isn,self.env_nvs['ISN_FATP']))
        if DATA.isn==self.env_nvs['ISN_FATP']:
            DATA.op('TEST_CHECK_ISN_PAD_FATP,0,%s,N/A,N/A'%DATA.isn)
        else:
            DATA.op('TEST_CHECK_ISN_PAD_FATP,1,%s,N/A,N/A'%DATA.isn)

        sfis=DATA.objs['sfis']
        logD(type(sfis))
        self.isn69=sfis.get69by80(self.isn80)
        logV('\n\n%s: %s =?= %s\n\n'%('TEST_CHECK_ISN_PAD_MLB',self.isn69,self.env_nvs['ISN_MLB']))
        if self.isn69==self.env_nvs['ISN_MLB']:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,0,%s,N/A,N/A'%self.isn69)
        else:
            DATA.op('TEST_CHECK_ISN_PAD_MLB,1,%s,N/A,N/A'%self.isn69)

        CONFIG_FATP=sfis.get_mlb_snx(self.isn80, 'SNB')
        logV('\n\n%s: %s =?= %s\n\n' % ('TEST_CHECK_CONFIG_PAD_FATP', CONFIG_FATP,self.env_nvs['CONFIG_FATP']))
        if CONFIG_FATP==self.env_nvs['CONFIG_FATP']:
            DATA.op('TEST_CHECK_CONFIG_PAD_FATP,0,%s,N/A,N/A'%CONFIG_FATP)
        else:
            DATA.op('TEST_CHECK_CONFIG_PAD_FATP,1,%s,N/A,N/A'%CONFIG_FATP)

        BUILD_PHASE = sfis.get_buildphase(self.isn80)
        logV('\n\n%s: %s =?= %s\n\n' % ('BUILD_PHASE', BUILD_PHASE , self.env_nvs['BUILD_PHASE']))
        if BUILD_PHASE == self.env_nvs['BUILD_PHASE']:
            DATA.op('TEST_CHECK_BUILD_PHASE,0,%s,N/A,N/A'%BUILD_PHASE)
        else:
            DATA.op('TEST_CHECK_BUILD_PHASE,1,%s,N/A,N/A'%BUILD_PHASE)

        MLBCONFIG = sfis.get_mlb_pre_config(self.isn69)
        logV('\n\n%s: %s =?= %s\n\n' % ('TEST_CHECK_CONFIG_PAD_MLB', MLBCONFIG , self.env_nvs['MLBCONFIG']))
        if MLBCONFIG == self.env_nvs['MLBCONFIG']:
            DATA.op('TEST_CHECK_CONFIG_PAD_MLB,0,%s,N/A,N/A'%MLBCONFIG)
        else:
            DATA.op('TEST_CHECK_CONFIG_PAD_MLB,1,%s,N/A,N/A'%MLBCONFIG)

        NLWEAVEPROVISIONINGHASH = sfis.get_mlb_snx(self.isn69, 'SNF')
        logV('\n\n%s: %s =?= %s ==?== %s\n\n' % ('TEST_CHECK_NLWEAVEPROVISIONINGHASH', NLWEAVEPROVISIONINGHASH , self.env_nvs['NLWEAVEPROVISIONINGHASH'],self.gen_hash))
        if NLWEAVEPROVISIONINGHASH == self.env_nvs['NLWEAVEPROVISIONINGHASH'] and NLWEAVEPROVISIONINGHASH==self.gen_hash:
            DATA.op('TEST_CHECK_NLWEAVEPROVISIONINGHASH,0,%s,N/A,N/A'%NLWEAVEPROVISIONINGHASH)
        else:
            DATA.op('TEST_CHECK_NLWEAVEPROVISIONINGHASH,1,%s,N/A,N/A'%NLWEAVEPROVISIONINGHASH)

        NLWEAVEPRIVATEKEY=sfis.get_mlb_snx(self.isn69,'SNG')
        logV('\n\n%s: %s =?= %s\n\n' % (
        'TEST_CHECK_NLWEAVEPRIVATEKEY', NLWEAVEPRIVATEKEY,self.env_nvs['NLWEAVEPRIVATEKEY']))
        if NLWEAVEPRIVATEKEY==self.env_nvs['NLWEAVEPRIVATEKEY']:
            DATA.op('TEST_CHECK_NLWEAVEPRIVATEKEY,0,%s,N/A,N/A'%NLWEAVEPRIVATEKEY)
        else:
            DATA.op('TEST_CHECK_NLWEAVEPRIVATEKEY,1,%s,N/A,N/A'%NLWEAVEPRIVATEKEY)

        NLWEAVECERTIFICATE = sfis.get_mlb_snx(self.isn69, 'SNB')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_NLWEAVECERTIFICATE', NLWEAVECERTIFICATE ,self.env_nvs['NLWEAVECERTIFICATE']))
        if NLWEAVECERTIFICATE == self.env_nvs['NLWEAVECERTIFICATE']:
            DATA.op('TEST_CHECK_NLWEAVECERTIFICATE,0,%s,N/A,N/A'%NLWEAVECERTIFICATE)
        else:
            DATA.op('TEST_CHECK_NLWEAVECERTIFICATE,1,%s,N/A,N/A'%NLWEAVECERTIFICATE)

        NLWEAVEPAIRINGCODE = sfis.get_mlb_snx(self.isn69, 'SNA')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_NLWEAVEPAIRINGCODE', NLWEAVEPAIRINGCODE ,self.env_nvs['NLWEAVEPAIRINGCODE']))
        if NLWEAVEPAIRINGCODE == self.env_nvs['NLWEAVEPAIRINGCODE']:
            DATA.op('TEST_CHECK_NLWEAVEPAIRINGCODE,0,%s,N/A,N/A'%NLWEAVEPAIRINGCODE)
        else:
            DATA.op('TEST_CHECK_NLWEAVEPAIRINGCODE,1,%s,N/A,N/A'%NLWEAVEPAIRINGCODE)

        BUILD_EVENT = 'EVT'#sfis.get_mlb_snx(self.isn69, 'SND')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_BUILD_EVENT', BUILD_EVENT , self.env_nvs['BUILD_EVENT']))
        if BUILD_EVENT == self.env_nvs['BUILD_EVENT']:
            DATA.op('TEST_CHECK_BUILD_EVENT,0,%s,N/A,N/A'%BUILD_EVENT)
        else:
            DATA.op('TEST_CHECK_BUILD_EVENT,1,%s,N/A,N/A'%BUILD_EVENT)

        NLMODEL = sfis.get_mlb_snx(self.isn69, 'SNE')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_NLMODEL', NLMODEL ,self.env_nvs['NLMODEL']))
        if NLMODEL == self.env_nvs['NLMODEL']:
            DATA.op('TEST_CHECK_NLMODEL,0,%s,N/A,N/A'%NLMODEL)
        else:
            DATA.op('TEST_CHECK_NLMODEL,1,%s,N/A,N/A'%NLMODEL)

        BUILD_DATE = sfis.get_mlb_snx(self.isn80, 'SNA')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_BUILD_DATE', BUILD_DATE ,self.env_nvs['BUILD_DATE']))
        if BUILD_DATE == self.env_nvs['BUILD_DATE']:
            DATA.op('TEST_CHECK_BUILD_DATE,0,%s,N/A,N/A'%BUILD_DATE)
        else:
            DATA.op('TEST_CHECK_BUILD_DATE,1,%s,N/A,N/A'%BUILD_DATE)

        GANG_NUM = sfis.get_mlb_snx(self.isn80, 'SNC')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_GANG_NUM', GANG_NUM ,self.env_nvs['GANG_NUM']))
        if GANG_NUM == self.env_nvs['GANG_NUM']:
            DATA.op('TEST_CHECK_GANG_NUM,0,%s,N/A,N/A'%GANG_NUM)
        else:
            DATA.op('TEST_CHECK_GANG_NUM,1,%s,N/A,N/A'%GANG_NUM)

        WIFI_MAC = sfis.get_mlb_snx(self.isn69, 'MAC1')
        WIFI_MAC=':'.join(WIFI_MAC[i:i+2] for i in range(0,12,2))
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_WIFI_MAC', WIFI_MAC ,self.env_nvs['WIFI_MAC']))
        if WIFI_MAC == self.env_nvs['WIFI_MAC']:
            DATA.op('TEST_CHECK_WIFI_MAC,0,%s,N/A,N/A'%WIFI_MAC)
        else:
            DATA.op('TEST_CHECK_WIFI_MAC,1,%s,N/A,N/A'%WIFI_MAC)

        SIXLOWPAN_MAC = sfis.get_mlb_snx(self.isn69, 'A13941')
        SIXLOWPAN_MAC = ':'.join(SIXLOWPAN_MAC[i:i + 2] for i in range(0, 16, 2))
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_6LOWPAN_MAC', SIXLOWPAN_MAC ,self.env_nvs['6LOWPAN_MAC']))
        if SIXLOWPAN_MAC == self.env_nvs['6LOWPAN_MAC']:
            DATA.op('TEST_CHECK_6LOWPAN_MAC,0,%s,N/A,N/A'%SIXLOWPAN_MAC)
        else:
            DATA.op('TEST_CHECK_6LOWPAN_MAC,1,%s,N/A,N/A'%SIXLOWPAN_MAC)

        ISN_IF = sfis.get_keypart(self.isn80, 'TP')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_ISN_INTERFACEBOARD', ISN_IF, self.env_nvs['ISN_IF']))
        if ISN_IF == self.env_nvs['ISN_IF']:
            DATA.op('TEST_CHECK_ISN_INTERFACEBOARD,0,%s,N/A,N/A'%ISN_IF)
        else:
            DATA.op('TEST_CHECK_ISN_INTERFACEBOARD,1,%s,N/A,N/A'%ISN_IF)

        ISN_BATTERY = sfis.get_keypart(self.isn80, 'BT')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_ISN_BATTERY', ISN_BATTERY, self.env_nvs['ISN_BATTERY']))
        if ISN_BATTERY == self.env_nvs['ISN_BATTERY']:
            DATA.op('TEST_CHECK_ISN_BATTERY,0,%s,N/A,N/A'%ISN_BATTERY)
        else:
            DATA.op('TEST_CHECK_ISN_BATTERY,1,%s,N/A,N/A'%ISN_BATTERY)

        ISN_PIR = sfis.get_keypart(self.isn80, 'SB2')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_ISN_PIR', ISN_PIR, self.env_nvs['ISN_PIR']))
        if ISN_PIR == self.env_nvs['ISN_PIR']:
            DATA.op('TEST_CHECK_ISN_PIR,0,%s,N/A,N/A'%ISN_PIR)
        else:
            DATA.op('TEST_CHECK_ISN_PIR,1,%s,N/A,N/A'%ISN_PIR)

        ISN_PROXTALS = sfis.get_keypart(self.isn80, 'SB1')
        logV('\n\n%s: %s =?= %s\n\n' % (
            'TEST_CHECK_ISN_PROX', ISN_PROXTALS, self.env_nvs['ISN_PROXTALS']))
        if ISN_PROXTALS == self.env_nvs['ISN_PROXTALS']:
            DATA.op('TEST_CHECK_ISN_PROX,0,%s,N/A,N/A'%ISN_PROXTALS)
        else:
            DATA.op('TEST_CHECK_ISN_PROX,1,%s,N/A,N/A'%ISN_PROXTALS)

        if self.env_nvs['REL_STATUS']=='0' or self.env_nvs['REL_STATUS']=='1':
            DATA.op('TEST_CHECK_REL_STATUS,0,%s,N/A,N/A'%self.env_nvs['REL_STATUS'])
        else:
            DATA.op('TEST_CHECK_REL_STATUS,1,%s,N/A,N/A'%self.env_nvs['REL_STATUS'])

        if self.env_nvs['RF_CALL_11']!='N/A':
            DATA.op('TEST_CHECK_RF_CALL_11,0,%s,N/A,N/A'%self.env_nvs['RF_CALL_11'])
        else:
            DATA.op('TEST_CHECK_RF_CALL_11,1,%s,N/A,N/A'%self.env_nvs['RF_CALL_11'])

        if self.env_nvs['RF_NP_US']!='N/A':
            DATA.op('TEST_CHECK_RF_NP_US,0,%s,N/A,N/A'%self.env_nvs['RF_NP_US'])
        else:
            DATA.op('TEST_CHECK_RF_NP_US,1,%s,N/A,N/A'%self.env_nvs['RF_NP_US'])

        if self.env_nvs['RF_CAL_17']!='N/A':
            DATA.op('TEST_CHECK_RF_CAL_17,0,%s,N/A,N/A'%self.env_nvs['RF_CAL_17'])
        else:
            DATA.op('TEST_CHECK_RF_CAL_17,1,%s,N/A,N/A'%self.env_nvs['RF_CAL_17'])

        if self.env_nvs['RF_IBO']!='N/A':
            DATA.op('TEST_CHECK_RF_IBO,0,%s,N/A,N/A'%self.env_nvs['RF_IBO'])
        else:
            DATA.op('TEST_CHECK_RF_IBO,1,%s,N/A,N/A'%self.env_nvs['RF_IBO'])

        if self.env_nvs['RF_CAL_25']!='N/A':
            DATA.op('TEST_CHECK_RF_CAL_25,0,%s,N/A,N/A'%self.env_nvs['RF_CAL_25'])
        else:
            DATA.op('TEST_CHECK_RF_CAL_25,1,%s,N/A,N/A'%self.env_nvs['RF_CAL_25'])

    def readsysenv(self,argv):
        self.sysenv_name_vale={}
        self.sysenv_readitems =['TEST_READ_SYSENV_GANG_NUM','TEST_READ_SYSENV_TOUCH_FW',
                           'TEST_READ_SYSENV_NLWEAVEPRIVATEKEY','TEST_READ_SYSENV_NLWEAVECERTIFICATE']
        
        for item in self.sysenv_readitems:
            self.sysenv_name_vale[item]='N/A'
        try:
            self.io.connect()
        except Exception,e:
            logE(Exception,e)
            DATA.op('%s,1,FAIL,N/A,N/A'%argv['name'])
            return
        r, v = self.io.wr('nlcli pad -p\r', '> ', has='exit')
        logV(r, v)
        r, v = self.io.wr('sysenv\r', '# ', has='root@')
        logV(r, v)
        self.io.disconnect()
        
        name_keys={'TEST_READ_SYSENV_GANG_NUM':'gang_num',
                   'TEST_READ_SYSENV_TOUCH_FW':'touch_fw',
                   'TEST_READ_SYSENV_NLWEAVEPRIVATEKEY':'nlWeavePrivateKey',
                   'TEST_READ_SYSENV_NLWEAVECERTIFICATE':'nlWeaveCertificate'}
        try:
            lines = v.split('\n')
        except:
            lines=[]
        k_v = {}
        for line in lines:
            if line.find('=')>0:
                k,v = line.split('=',1)
                k_v[k.strip()]=v.strip()

        for item in self.sysenv_readitems:
            if name_keys[item] in k_v.keys():
                self.sysenv_name_vale[item]=k_v[name_keys[item]]
                DATA.op('%s,0,%s,N/A,N/A'%(item,k_v[name_keys[item]]))
            else:
                DATA.op('%s,1,N/A,N/A,N/A' % (item))

    def checksysenv(self,argv):
        if self.sysenv_name_vale['TEST_READ_SYSENV_GANG_NUM']==self.env_nvs['GANG_NUM']:
            DATA.op('TEST_CHECK_SYSENV_GANG_NUM,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_SYSENV_GANG_NUM,1,FAIL,N/A,N/A')

        ### get touch ver from cmd
        try:
            self.io.connect()
        except Exception,e:
            logE(Exception,e)
            DATA.op('%s,1,FAIL,N/A,N/A'%argv['name'])
            return


        r, v = self.io.wr('its 0\r', '> ')
        logV(r, v)

        self.env_nvs['TOUCH_FW'] = 'N/A'
        if v.find(',')>0:
            vs=v.split(',')
            if len(vs)>2:
                self.env_nvs['TOUCH_FW'] = vs[1].split()[0].strip()
                logV('Touch FW = [%s]'%self.env_nvs['TOUCH_FW'])

        r, v = self.io.wr('%c\r'%3, '> ')
        logV(r, v)
        self.io.disconnect()
        if self.sysenv_name_vale['TEST_READ_SYSENV_TOUCH_FW'] == self.env_nvs['TOUCH_FW']:
            DATA.op('TEST_CHECK_SYSENV_TOUCH_FW,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_SYSENV_TOUCH_FW,1,FAIL,N/A,N/A')

        if self.sysenv_name_vale['TEST_READ_SYSENV_NLWEAVEPRIVATEKEY'] == self.env_nvs['NLWEAVEPRIVATEKEY']:
            DATA.op('TEST_CHECK_SYSENV_NLWEAVEPRIVATEKEY,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_SYSENV_NLWEAVEPRIVATEKEY,1,FAIL,N/A,N/A')

        if self.sysenv_name_vale['TEST_READ_SYSENV_NLWEAVECERTIFICATE'] == self.env_nvs['NLWEAVECERTIFICATE']:
            DATA.op('TEST_CHECK_SYSENV_NLWEAVECERTIFICATE,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_CHECK_SYSENV_NLWEAVECERTIFICATE,1,FAIL,N/A,N/A')



    def checkssversion(self,argv):
        check_ver = argv['version']
        #self.io = RS232(argv)
        self.io._connect()
        r, v =self.io.wr('\r', '# ')
        logV(r, v)
        r, v = self.io.wr('root\r', '# ', has='root@')
        logV(r, v)
        cmd = 'cat /proc/version\r'
        r, v = self.io.wr(cmd, '# ', has='root@')
        logV(r, v)
        items = v.split('\n')
        if len(items)>=2 and items[1].startswith('Linux version'):
            version = items[1].strip()
            if version.find(check_ver)>=0:
                DATA.op(argv['name']+',0,%s,N/A,N/A'%version)
            else:
                DATA.op(argv['name'] + ',1,%s,N/A,N/A' % version)
        else:
            DATA.op(argv['name'] + ',1,N/A,N/A,N/A')

        ###  power off at end
        power_off_cmds =[
            'echo 0 > /sys/bus/platform/devices/0.sensor-mcu-gpios/reset/value\r',
            'usleep 4000000\r',
            'echo 1 > /sys/bus/platform/devices/0.sensor-mcu-gpios/reset/value\r',
            'usleep 15000\r',
            'echo 0 > /sys/bus/platform/devices/0.sensor-mcu-gpios/reset/value\r',
            'usleep 3000000\r',
            'echo "\r" > /dev/ttymxc2\r',
            'echo "ship" > /dev/ttymxc2\r'
        ]
        for cmd in power_off_cmds:
            r, v = self.io.wr(cmd, '# ', has='root@')
            logV(r, v)
        # r, v = self.io.wr('echo "\r" > /dev/ttymxc2\r', '# ', has='root@')
        # logV(r, v)
        # r, v = self.io.wr('echo "ship" > /dev/ttymxc2\r', '# ', has='root@')
        # logV(r, v)
        self.io.disconnect()

    def check_qrc(self,argv):
        self.qrc = DATA.isn
        DATA.isn =self.qrc[28:44]
        #self.io = RS232(argv)
        self.io._connect()
        r, v = self.io.wr('root\r', '# ', has='root@')
        logV(r, v)
        rt, v = self.io.wr('devdesc\r', '# ', '', 1)
        self.io.disconnect()
        if rt:
            value = self.GetMiddleStr(v, 'devdesc\r', '\r').strip()
            logV('QRC:', rt, v, value)
            if value == self.qrc:
                DATA.op(argv['name']+',0,PASS,N/A,N/A')
                return
        DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')

    '''fix led bin code'''
    def fix_bincode(self,argv):
        sfis = DATA.objs['sfis']
        logD(type(sfis))
        ISN_IF = sfis.get_keypart(DATA.isn, 'TP')
        DATA.op('TEST_CHECK_ISN_INTERFACEBOARD,0,%s,N/A,N/A' % ISN_IF)
        BINCODE = sfis.get_mlb_snx(ISN_IF, 'SNC')
        DATA.op('BINCODE,0,%s,N/A,N/A' % BINCODE)
        if BINCODE.find(";")<0:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return
        BIN_RGB,BIN_WHITE = BINCODE.split(';')
        cmd1 = 'sysenv set WLED_bin %s\r'%BIN_WHITE
        cmd2 = 'sysenv set RGB_bin %s\r'%BIN_RGB

        try:
            self.io.connect()
        except Exception,e:
            logE(Exception,e)
            DATA.op('%s,1,FAIL,N/A,N/A'%argv['name'])
            return
        r, v = self.io.wr('root\r', '# ', has='root@')
        logV(r, v)
        r, v = self.io.wr('nlcli pad -p\r', '>', has='exit')
        logV(r, v)
        r, v = self.io.wr('sysenv\r', '>', has='>')
        logV(r, v)

        if v.find('WLED_bin')>=0 and v.find('RGB_bin')>=0:
            DATA.op('%s,0,NONEED,N/A,N/A' % argv['name'])
            r, v = self.io.wr('%c\r'%3, '# ', has='root@')
            logV(r, v)
            self.io.disconnect()
            return
        r, v = self.io.wr(cmd1, '>', has='>')
        logV(r, v)
        time.sleep(3)
        r, v = self.io.wr(cmd2, '>', has='>')
        logV(r, v)
        r, v = self.io.wr('%c\r' % 3, '# ', has='root@')
        logV(r, v)
        self.io.disconnect()

    # fill all bin code in csv
    def fillallbincode(self,argv):
        sfis = DATA.objs['sfis']
        logD(sfis)
        with open('allbincode.csv','w') as fw:
            with open('isns.txt') as fr:
                for isn in fr:
                    isn=isn.strip()
                    logV(isn)
                    ISN_IF = sfis.get_keypart(isn, 'TP')
                    DATA.op('TEST_CHECK_ISN_INTERFACEBOARD,0,%s,N/A,N/A' % ISN_IF)
                    BINCODE = sfis.get_mlb_snx(ISN_IF, 'SNC')
                    DATA.op('BINCODE,0,%s,N/A,N/A' % BINCODE)
                    if BINCODE.find(";") < 0:
                        DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
                        fw.write('')
                        fw.write(',')
                        fw.write('')
                        fw.write(',')
                        fw.write(isn)
                        fw.write('\n')
                        continue
                    BIN_RGB, BIN_WHITE = BINCODE.split(';')
                    fw.write(BIN_RGB)
                    fw.write(',')
                    fw.write(BIN_WHITE)
                    fw.write(',')
                    fw.write(isn)
                    fw.write('\n')



