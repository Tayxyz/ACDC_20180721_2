from data import *
from EQUIPMENT.laservall import laservall
class qrc:
    def __init__(self,argv):
        self.laser=laservall(argv)

    def get_qrc_from_sfis(self,argv):
        sfis = DATA.objs['sfis']
        self.qrc = sfis.get_mlb_snx(DATA.isn, 'SND')
        logV(self.qrc,len(self.qrc))
        if len(self.qrc)==72:
            DATA.op('TEST_GET_QRC,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_GET_QRC,1,FAIL,N/A,N/A')

    def rotatein(self,argv):
        rt=self.laser.rotatein(argv)
        if not rt:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')


    def rotateout(self,argv):
        rt=self.laser.rotateout(argv)
        if not rt:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')

    def etchqr(self,argv):
        if DATA.isn.startswith('26A'):
            gang='templet1'
        elif DATA.isn.startswith('21A'):
            gang = 'templet2'
        else:
            DATA.op(argv['name'] + ',1,UNKONW_GANG,N/A,N/A')
            return
        try:
            qrcmodule=argv[gang]
        except:
            qrcmodule='BM_PAD'
        if len(self.qrc)!=72:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return

        r,v=self.laser.etch({'m':qrcmodule,'isn':DATA.isn,'qrc':self.qrc,'pairing':self.qrc[-7:-1]})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')

    def fake_etchqr(self,argv):
        if DATA.isn.startswith('26A'):
            gang = 'templet1'
        elif DATA.isn.startswith('21A'):
            gang = 'templet2'
        else:
            DATA.op(argv['name'] + ',1,UNKONW_GANG,N/A,N/A')
            return
        try:
            qrcmodule = argv[gang]
        except:
            qrcmodule = 'BM_PAD'

        self.qrc='X'*72

        r, v = self.laser.etch({'m': qrcmodule, 'isn': DATA.isn, 'qrc': self.qrc, 'pairing': self.qrc[-7:-1]})
        if not r:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')

    def etchisn(self,argv):
        if DATA.isn.startswith('26C'):
            gang = 'templet1'
        elif DATA.isn.startswith('21C'):
            gang = 'templet2'
        else:
            DATA.op(argv['name'] + ',1,UNKONW_GANG,N/A,N/A')
            return
        try:
            qrcmodule=argv[gang]
        except:
            qrcmodule='BM_SWITCH'
        r, v = self.laser.etchisn({'m': qrcmodule, 'isn': DATA.isn})
        if not r:
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')