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
        cmd='<L%s><D1,%s><D2,%s><D3,%s><X>'%(argv['m'],argv['isn'],argv['qrc'],argv['pairing'])
        cmd=cmd.encode("ascii")
        r, v = self.io.wr(cmd, '<XE>',timeout=30) #start to lase
        logV(r, repr(v))
        return r,v

    def etchisn(self,argv):
        cmd = '<L%s><D1,%s><X>' % (argv['m'], argv['isn'])
        cmd = cmd.encode("ascii")
        r, v = self.io.wr(cmd, '<XE>', timeout=30)
        logV(r, repr(v))
        return r, v

    def rotatein(self,argv):
        #send directions
        r, v = self.io.wr('<I>', '<W>', timeout=30)
        logV(r, repr(v))
        return r

    def rotateout(self,argv):
        r, v = self.io.wr('<I>', '<W>', timeout=30)
        logV(r, repr(v))
        return r