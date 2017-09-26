from IO.rs232 import RS232
from data import *
##cmds##
# <Lmodulename> -> <RD>
# <D1,QRC><D2,xxx>..<Etest> -> <RD>
#
# <X> -> <RD>   -><XE>

class laservall:
    def __init__(self,argv):
        self.io = RS232(argv)
        self.io._connect()

    def loadmodule(self,argv):
        modulename=argv['modulename']
        cmd='<L%s>\n'%modulename
        r,v=self.io.wr(cmd,'<RD>')
        logV(r,repr(v))
        return r, v

    def loadparameters(self,argv):
        cmd=argv['cmd']
        r, v = self.io.wr(cmd, '<RD>')
        logV(r, repr(v))
        return r, v

    def etch(self,argv):
        r, v = self.io.wr('<X>\n', '<XE>','<RD>')
        logV(r, repr(v))
        return r,v

    def rotatein(self,argv):
        pass

    def rotateout(self,argv):
        pass