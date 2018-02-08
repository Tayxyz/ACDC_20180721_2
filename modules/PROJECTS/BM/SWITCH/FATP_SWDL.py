from data import *
import subprocess
import time
from IO.rs232 import RS232

class dl:
    def __init__(self,argv):
        self.rs232={}

    def whichgang(self,argv):
        if DATA.isn.startswith('26'):
            self.gang = '1'
        elif DATA.isn.startswith('21'):
            self.gang = '2'
        else:
            self.gang = 'NUKNOW'
        DATA.op('GANG_NUMB,0,%s,N/A,N/A'%self.gang)

    def callexe(self,argv):
        try:
            gang=argv['gang']
        except:
            gang='1,2,3,4'
        if not self.gang in gang:
            #DATA.op(argv['name'] + ',0,SKIP,N/A,N/A')
            return
        cmd=argv['exe']
        try:
            has=argv['has']
        except:
            has=''
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
                DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            else:
                DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
            return rtbuf
        except Exception,e:
            logV(Exception,e)
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return ''

    def open_com_port(self,argv):
        try:
            gang=argv['gang']
        except:
            gang='1,2,3,4'
        if not self.gang in gang:
            #DATA.op(argv['name'] + ',0,SKIP,N/A,N/A')
            return
        name=argv['com_name']
        self.rs232[name]=RS232(argv)
        self.rs232[name]._connect()

    def close_com_port(self,argv):
        try:
            gang=argv['gang']
        except:
            gang='1,2,3,4'
        if not self.gang in gang:
            #DATA.op(argv['name'] + ',0,SKIP,N/A,N/A')
            return
        name = argv['com_name']
        self.rs232[name].disconnect()

    def send_cmd(self,argv):
        try:
            gang=argv['gang']
        except:
            gang='1,2,3,4'
        if not self.gang in gang:
            #DATA.op(argv['name'] + ',0,SKIP,N/A,N/A')
            return
        com_name = argv['com_name']
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
        r,v=self.rs232[com_name].wr(cmd,end,has,timeout)
        logV(r,repr(v))
        if r:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
