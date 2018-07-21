'''
this module depends ADlink PCIS-DASK and only works under windows
call the functions in the PCI-Dask.dll/PCI-Dask64.dll

'''

from ctypes import *
from data import *

PCI_7230 = c_ushort(6)


class ADlink7320():

    def __init__(self,argv):
        try:
            self.dll = WinDLL('PCI-Dask.dll')
            logV(self.dll)
            self.opencard(argv)
        except Exception,e:
            self.dll =None
            logV(Exception,e)

    def __del__(self):
        if  self.dll and self.card>=0:
            self.dll.Release_Card(self.card)


    def opencard(self,argv):
        try:
            card_number=c_ushort(int(argv['card_number']))
        except:
            card_number = c_ushort(0)
        self.card = self.dll.Register_Card(PCI_7230,card_number)
        logV('card=',self.card)


    def write_relay(self,v):

        logV('relay off:',v,self.dll.DO_WritePort(self.card,0,v))

    def query_relay(self):

        state = c_ushort()
        logV(self.dll.DO_ReadPort(self.card,0,byref(state)))
        logV('state=',state)
        return state



if __name__ == '__main__':

    if os.path.exists('ee.txt'):
        os.remove('ee.txt')


    def logE(*args):
        v = ' '.join([str(s) for s in args])
        with open('ee.txt', 'a') as fa:
            fa.write('\n' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            fa.write('[error] ')
            fa.write(v)


    def logV(*args):
        v = ' '.join([str(s) for s in args])
        with open('ee.txt', 'a') as fa:
            fa.write('\n' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            fa.write('[verbose] ')
            fa.write(v)
    card1 = ADlink7320({})
    card1.opencard({'card_number':'0'})
    card2 = ADlink7320({})
    card2.opencard({'card_number':'1'})
    card1.relay_on({'channel':'0'})
    card1.relay_off({'channel': '1'})
    print card1.query_relay({'channel': '0'})
    print card1.query_relay({'channel': '1'})
    card1.relay_on({'channel': '2'})
    card1.relay_off({'channel': '3'})
    print card1.query_relay({'channel': '2'})
    print card1.query_relay({'channel': '3'})
