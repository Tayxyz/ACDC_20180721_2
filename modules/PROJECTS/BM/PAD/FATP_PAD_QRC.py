from data import *
from EQUIPMENT.laservall import laservall
class qrc:
    def __init__(self,argv):
        self.laser=laservall(argv)

    def get_qrc_from_sfis(self,argv):
        sfis = DATA.objs['sfis']
        self.qrc = sfis.get_mlb_snx(DATA.isn, 'SND')
        logV(self.qrc)
        if len(self.qrc)==71:
            DATA.op('TEST_GET_QRC,0,PASS,N/A,N/A')
        else:
            DATA.op('TEST_GET_QRC,1,FAIL,N/A,N/A')

    def etchqr(self,argv):
        try:
            qrcmodule=argv['templet']
        except:
            qrcmodule='BM_PAD'
        r,v=self.laser.loadmodule({'modulename':qrcmodule})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
            return
        cmds='<D1,%s><Etest>'%self.qrc
        r,v=self.laser.loadparameters({'cmd':cmds})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
            return
        r,v=self.laser.etch({})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')

    def etchisn(self,argv):
        try:
            qrcmodule=argv['templet']
        except:
            qrcmodule='BM_SWITCH'
        r,v=self.laser.loadmodule({'modulename':qrcmodule})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
            return
        cmds='<D1,%s><Etest>'%DATA.isn
        r,v=self.laser.loadparameters({'cmd':cmds})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
            return
        r,v=self.laser.etch({})
        if not r:
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        else:
            DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
