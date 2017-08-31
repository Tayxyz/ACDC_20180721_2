from multiprocessing import Lock,Condition,Process,Value

class BARRIER:
    def __init__(self,n):
        self.n=n
        self.i=Value('i',0)
        self.lock=Lock()
        self.condition=Condition()

    def acquire(self):
        with self.lock:
            self.i.value += 1
            if self.n==self.i.value:
                self.i.value=0
                return True

        #print self.i.value,self.n
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        return False

    def release(self):
        self.condition.acquire()
        self.condition.notify_all()
        self.condition.release()


if __name__=='__main__':
    def fun(i,b):
        import time
        time.sleep(i)
        if b.acquire():
            print i,'I catch you'
            b.release()
            print 'released'
        else:
            print i,'wait for you'

    b=BARRIER(5)
    ws=[Process(target=fun,args=(i,b)) for i in range(1,6)]
    for w in ws:
        w.start()