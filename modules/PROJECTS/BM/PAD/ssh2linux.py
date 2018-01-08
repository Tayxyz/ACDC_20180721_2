import paramiko
import serial
import time
from data import *
import threading

class ssh2linux:
    def __init__(self,argv):
        pass

    def flash(self,argv):
        try:
            ip=argv['ip']
        except:
            ip='192.168.100.100'

        try:
            user=argv['user']
        except:
            user='bm'
        try:
            passwd=argv['passwd']
        except:
            passwd='pega#1234'
        try:
            cmd=argv['cmd']
        except:
            cmd='cd moonstone/dfu_noflash;./dfu.sh'
        try:
            com=argv['com']
        except:
            com='COM58'
        try:
            timeout=int(argv['timeout'])
        except:
            timeout=60
        try:
            expect=argv('expect')
        except:
            expect='moonstone login:'
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, 22,user ,passwd )
        client.exec_command(cmd)
        com = serial.Serial(com, 115200, timeout=1)
        t0 = time.time()
        buf = ''
        while time.time() - t0 < timeout:
            buftmp = com.read(1)
            print buftmp,
            buf += buftmp
            if buf.find(expect) >= 0:
                com.write('root\r')
                break
        com.close()
        client.close()
        logV(buf)

    def waitForBoot(self,argv):
        try:
            com=argv['com']
        except:
            com='COM58'
        try:
            boottool=argv['boottool']
        except:
            boottool='D:\\Testprogram\\POC\\win-noflash-dfu-20171118\\MfgTool2.exe -noui'
        try:
            import subprocess
            sp = subprocess.Popen(boottool, shell=True, stdout=subprocess.PIPE)

        except Exception,e:
            print Exception,e
        t0=time.time()
        com = serial.Serial(com, 115200, timeout=1)
        rt=''
        while time.time()-t0<30:
            try:
                rt+=com.read()
                if rt.find('login:')>=0:
                    com.write('root\r')
                    logV(rt)
                    com.close()
                    return True
            except:
                pass
            time.sleep(0.3)
        logE(rt,'timeout..')
        com.close()
        return False

    def update(self,argv):
        try:
            ip=argv['ip']
        except:
            ip='192.168.100.100'

        try:
            user=argv['user']
        except:
            user='bm'
        try:
            passwd=argv['passwd']
        except:
            passwd='pega#1234'
        try:
            cmd=argv['cmd']
        except:
            cmd='cd moonstone/dfu_update;./dfu.sh'
        try:
            timeout=int(argv['timeout'])
        except:
            timeout=220
        try:
            expect=argv('expect')
        except:
            expect='Done'
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, 22,user ,passwd )
        def backtime():
            time.sleep(timeout)
            try:
                stdout.close()
                client.close()
            except Exception,e:
                logD(Exception,e)
                pass
        thd=threading.Thread(target=backtime)
        thd.start()
        stdin, stdout, stderr =client.exec_command(cmd)
        for line in stdout:
            print line
            logV(line)
        try:
            client.close()
        except:
            pass


    def login(self):
        # thread1 = threading.Thread(target=self.dfu_bootload)
        # thread1.start()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect('192.168.100.100', 22, 'bm', 'pega#1234')
        stdin, stdout, stderr = self.client.exec_command('cd moonstone/linux;pwd;ls;./dfu.sh')
        self.dfu_bootload()
        # for line in stdout:
        #     print line
        # thread1.join()
        self.client.close()


    def dfu_bootload(self):
        com = serial.Serial('COM58',115200,timeout=1)

        t0 = time.time()
        buf=''
        while time.time() - t0 < 40:
            buf1=com.read(1)
            print buf1,
            buf+=buf1
            if buf.find('Hit any key to stop autoboot:')>=0:
                com.write('\r')
                com.write('setenv mmcpart 1\r')
                com.write('run bootcmd\r')
                print buf,
                break

        while time.time() - t0 < 60:
            buftmp= com.read(1)
            print buftmp,
            buf+=buftmp
            if buf.find('moonstone login:')>=0:
                com.write('root\r')
                break

        com.close()

        # print buf



if __name__=='__main__':
    s2l=ssh2linux({})
    s2l.login()


