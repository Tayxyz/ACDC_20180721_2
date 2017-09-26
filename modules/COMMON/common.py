from data import *
import subprocess
class common:
    def __init__(self,argv):
        pass

    def callexe(self,argv):
        cmd=argv['exe']

        rtbuf=''
        logV(cmd)
        try:
            p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)

            while p.poll() == None:
                buf=p.stdout.readline()
                logV(buf)
                rtbuf+=buf
                time.sleep(0.005)
            buf=p.stdout.read()
            logV(buf)
            rtbuf += buf
            logV('return code:', p.returncode)
            if p.returncode!=0:
                DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            else:
                DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
            return rtbuf
        except Exception,e:
            logV(Exception,e)
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return ''