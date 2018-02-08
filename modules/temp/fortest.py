from data import *

class test:
    def __init__(self,argv):
        pass

    def passfail(self,argv):
        if DATA.id==1:
            DATA.op('TEST,1,FAIL,N/A,N/A')
        else:
            DATA.op('TEST,0,PASS,N/A,N/A')