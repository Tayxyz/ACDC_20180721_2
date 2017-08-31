import multiprocessing
from multiprocessing import Manager
from worker import worker
from reflex import *
from script import script
from singletoneBarrier import BARRIER
from data import DATA

sys.path.append("modules")

hold_stderr=sys.stderr
sys.stderr=open('error','w')


class controller():
    def __init__(self,script_name,setting_name,n):
        DATA.logfilepath ='controllerlog'
        with open(DATA.logfilepath,'w') as fw:
            fw.write('start\n')
        self.script_name=script_name
        self.setting_name = setting_name
        self.script=script(script_name)
        self.workers_number=0

        self.createSharedict()
        self.createLocks()
        self.createBarriers(n)
        self.createMonopoly()

        self.results = multiprocessing.Queue()

        self.s2c_io=multiprocessing.Queue()
        self.c2s_io=multiprocessing.Queue()

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

    def createMonopoly(self):
        self.monopolyobjs = {}
        for obj in self.script.get_monopoly():
            #print obj
            self.monopolyobjs[obj["obj"]] = getObject(obj["class"], obj)



    def create_one(self,id,isn):
        one=worker(id,isn,self.results,self.share_dic,self.locks,self.barriers,self.s2c_io,self.c2s_io)
        one.daemon=True
        one.start()
        self.workers.append(one)
        self.workers_number+=1

    def loops(self):
        while not self.stop:
            result = self.results.get()
            #print(result)
            print >> hold_stderr, result
            if str(result).find('&h')>=0:
                self.workers_number-=1
                if self.workers_number==0:
                    break
        #print ('-1&END')
        #print >> hold_stderr, '-1&END'

    def monopoly(self):
        while not self.stop:
            mission=self.c2s_io.get()
            if mission==None:
                break
            obj = self.monopolyobjs[mission['obj']]
            #print type(mission),mission
            rst = applyFuc(obj, mission['do'], mission)
            self.s2c_io.put(rst)


    def end(self):
        for w in self.workers:
            w.join()
        self.c2s_io.put(None)

if __name__=='__main__':
    #script,setting,x,isn_1,...,isn_x
    try:
        #print sys.argv
        script_name=sys.argv[1]
        setting_name=sys.argv[2]
        x=int(sys.argv[3])

        n=0
        for i in range(x):
            if not len(sys.argv[4+i])==0:
                n+=1


        Controller=controller(script_name,setting_name,n)
        for i in range(x):
            if not len(sys.argv[4+i])==0:
                Controller.create_one(i+1,sys.argv[4+i])

        import threading
        t=threading.Thread(target=Controller.loops)
        t.start()

        m = threading.Thread(target=Controller.monopoly)
        m.start()

        Controller.end()
        t.join()
        m.join()
    except Exception,e:
        print Exception,e

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
