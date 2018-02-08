from data import *
from IO.rs232 import RS232
class burning:
    def __init__(self,argv):
        logV(argv)
        self.isn = ''
        com = argv['COM'][str(DATA.id)]
        logV(com)
        self.dut = RS232({'COM':com})
        self.dut._connect()

    def compress(self,argv):
        timeout = argv['timeout']
        r, v = self.dut.wr('root\r', '# ', has='root@', timeout=timeout)
        logV(r, v)
        r, v = self.dut.wr('nlcli env get serial#\r', '# ', has='root@', timeout=timeout)
        logV(r, v)
        DATA.isn=self.isn =  GetMiddleStr(v,'serial#=','\r\n').strip()
        logV(self.isn)
        r, v = self.dut.wr('ls /media/log/burnin*\r', '# ', has='root@', timeout=timeout)
        logV(r, v)
        if v.find(self.isn)<0:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
            return

        cmd = argv['cmd'].encode('ascii')
        r,v = self.dut.wr(cmd,'# ',has='root@',timeout=timeout)
        logV(r,v)
        if r:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        r, v = self.dut.wr('rm -rf /media/log/burnin_*\r', '# ', has='root@', timeout=timeout)
        logV(r, v)


    def  test_append(self,argv):
        flag = argv['flag'].encode('ascii')
        r, v = self.dut.wr('cat /media/log/burnin/%s_*.csv\r'%self.isn, '# ', has='root@', timeout=2)
        logV(r, v)
        if v.find('No such file or directory')>0:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return
        DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
        lines = v.split('\n')
        bfind= False
        for line in lines:
            if line.find('FATP_GANG_NUMBER')>0:
                bfind = True
            if line.find(flag)>0:
                bfind = False
            if bfind:
                DATA.op(line.strip().replace('"',''))
            if line.find('TOTAL_TEST_TIME')>=0:
                items = line.split(',')
                if len(items)==5:
                    t = float(items[2].replace('"',''))
                    DATA.start_time-=t

    def send_log_to_pc(self,argv):
        tar = argv['tar'].encode('ascii')
        r, v = self.dut.wr('ls -l %s\r' % tar, '# ', has='root@', timeout=2)
        logV(r, v)
        items = v.split()
        if len(items)>7:
            try:
                filesize  =  int(items[7])
            except Exception,e:
                print Exception,e
                filesize = 0
        else:
            filesize  = 0
        logV('size: %d'%filesize)
        r, v = self.dut.wr('hexdump %s\r' % tar, '# ', has='root@', timeout=2)
        logV(r, v)
        if not r:
            logE('send cmd fail')
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return
        byte = 0
        with open(self.isn+'.tar.gz','wb') as fw:
            items = v.split('\n')
            for item in items:
                if item.find('hexdump')>=0:
                    continue
                if item.find('root@')>=0:
                    continue
                contents = item.split(' ')

                for i in range(1,len(contents)):
                    if len(contents[i])>=4:
                        fw.write('%c'%int(contents[i][2:4],16))
                        fw.write('%c' % int(contents[i][0:2],16))
                        byte +=2

        logV(filesize,byte)
        if filesize!=byte:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return

        DATA.morefiles.append(self.isn+'.tar.gz')
        DATA.op(argv['name'] + ',0,PASS,N/A,N/A')

    def batt_ship(self,argv):
        r, v = self.dut.wr('devdesc\r', '# ', has='root@', timeout=2)
        logV(r, v)
        qrc = GetMiddleStr(v,'devdesc','\r\n').strip()
        if len(qrc)==88:
            self.save_more=('#SAVE:SND:A,0,%s,N/A,N/A\n'%qrc)
        cmd = argv['cmd'].encode('ascii')
        r, v = self.dut.wr(cmd, '# ', has='root@', timeout=2)
        logV(r, v)
        self.dut.disconnect()
        if r:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
