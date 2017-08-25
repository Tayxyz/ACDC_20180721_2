import multiprocessing
from multiprocessing import Manager
from worker import worker
from reflex import *
from script import script
from singletoneBarrier import BARRIER

sys.path.append("modules")


class controller():
    def __init__(self,script_name,setting_name,n):
        self.script_name=script_name
        self.setting_name = setting_name
        self.script=script(script_name)
        self.workers_number=0

        self.createSharedict()
        self.createLocks()
        self.createBarriers(n)

        self.results = multiprocessing.Queue()
        self.stop = False
        self.workers=[]
        #self.workers = [worker(i+1, self.results,self.share_dic,self.locks,self.events)
        #             for i in range(work_num)]

    def createSharedict(self):
        m = Manager()
        self.share_dic =m.dict()
        self.share_dic['script_name']=self.script_name
        self.share_dic['setting_name'] = self.setting_name


    def createLocks(self):
        self.locks={}
        for obj in self.script.get_locks():
            lock = multiprocessing.Lock()
            self.locks[obj["name"]]=lock

    def createBarriers(self,n):
        self.barriers={}
        for obj in self.script.get_barriers():
            barrier = BARRIER(n)
            self.barriers[obj["name"]]=barrier


    def create_one(self,id,isn):
        one=worker(id,isn,self.results,self.share_dic,self.locks,self.barriers)
        one.daemon=True
        one.start()
        self.workers.append(one)
        self.workers_number+=1

    def loops(self):
        while not self.stop:
            result = self.results.get()
            print(result)
            if str(result).find('>finish')>=0:
                self.workers_number-=1
                if self.workers_number==0:
                    break
        print ('loop end')


    def end(self):
        for w in self.workers:
            w.join()

if __name__=='__main__':
    n=1
    Controller=controller('scripts/test_barrier.script','setting/Setting.ini',n)
    import os
    print ('main:',os.getpid())
    for i in range(n):
        Controller.create_one(i+1,str(i)*12)

    import threading
    t=threading.Thread(target=Controller.loops)
    t.start()

    Controller.end()
    t.join()


    # histroy={}
    # while True:
    #     s=raw_input('>:')
    #     logname='logforid'+str(s)
    #     try:
    #         inx=histroy[logname]
    #     except:
    #         inx=0
    #     with open(logname) as fr:
    #         fr.seek(inx,0)
    #         print fr.read()
    #         histroy[logname]=fr.tell()
