import subprocess
import serial
import time
def printQRC(sn,qrc,pc):

    cmd= '''^XA
                ^LH166,30^FS
                ^FO6,8
                ^A0N,14,14^FDFATP_ISN^FS
                ^FO10,22
                ^BQN,2,3
                ^FDQA,QRCODE^FS
                ^FO43,160
                ^A0N,16,16^FDPAIRINGCODE^FS
                ^XZ'''
    cmd=cmd . replace('FATP_ISN',sn).replace('QRCODE',qrc).replace('PAIRINGCODE',pc)
    with open('qrc.txt','w') as f:
        f.write(cmd)
    rc = subprocess.call('copy qrc.txt LPT1', shell=True)

def wr(com, cmd, end, has='', timeout=3):
    try:
        com.write(cmd)
        buf = ''
        t0 = time.time()
        while time.time() - t0 < timeout:
            buf += com.readall()
            if buf.endswith(end) and buf.find(has) >= 0:
                return True, buf
        return False, buf
    except Exception, e:
        print(Exception, e)
        return False, e

com = serial.Serial('COM7', 115200)
wr(com,'root\r','# ')
sn=raw_input('serial# = ')
wr(com,'nlcli env set serial# %s\r'%sn,'# ')
_,qrc_raw=wr(com,'devdesc\r','# ')
qrc=qrc_raw.split()[2]
pairingcode=qrc[-7:-1]

printQRC(sn,qrc,pairingcode)



