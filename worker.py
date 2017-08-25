import multiprocessing
from data import *
import time
import os
import sys
from script import script
from reflex import *

sys.path.append("modules")
VERSION = '1.0.0.0'


class worker(multiprocessing.Process):
    def __init__(self,_id, isn,result_queue,share_dic,locks,barriers):
        print ('work init:', os.getpid(),id(DATA))
        multiprocessing.Process.__init__(self)
        self.id = _id
        self.isn  =isn

        self.result_queue = result_queue
        self.share_dic=share_dic
        self.locks=locks
        self.barriers=barriers

    def run(self):
        try:
            print ('work run:', os.getpid(),id(DATA))
            proc_name = self.name

            DATA.start_time = t0 = time.time()

            DATA.id = self.id
            DATA.isn=self.isn
            if len(DATA.isn) == 0:
                DATA.isn = '1234567890123456'
            DATA.logfilepath = 'logforid' + str(self.id)
            with open(DATA.logfilepath, 'w') as fw:
                fw.write('START TEST:\n')
            DATA.result_queue = self.result_queue
            DATA.locks = self.locks
            DATA.barriers = self.barriers

            DATA.script_name = self.share_dic['script_name']
            self.script = script(DATA.script_name)
            DATA.setting_name = self.setting_name = self.share_dic['setting_name']
            DATA.read_setting()
            logV( 'load cost:', time.time() - t0)
            t0 = time.time()
            DATA.version = VERSION
            objs={}
            for obj in self.script.get_initial():
                objs[obj["obj"]] = getObject(obj["class"], obj)
            logV( 'initial cost:',time.time()-t0)

            process=self.script.get_process()
            steps=len(process)
            logV('process len=',steps)
            skip_flag = False
            for step in process:
                logV('\n#####', step['name'], '#####')
                if skip_flag:
                    canskip = True
                    try:
                        if step['noskip'] == 'YES':
                            canskip = False
                    except:
                        pass
                    if canskip:
                        print ('skip')
                        self.result_queue.put(str(self.id) + '>step<')
                        continue
                t00 = time.time()
                DATA.settime()
                obj = objs[step['obj']]
                rst = applyFuc(obj, step['action'], step)
                logV('\n-----', time.time() - t00, 's -----\n\n-')
                try:
                    if step['failstop'] == 'YES' and not DATA.currentpass:
                        skip_flag = True
                except:
                    pass
                try:
                    if step['anyfailstop'] == 'YES' and DATA.totalfails > 0:
                        skip_flag = True
                except:
                    pass

                self.result_queue.put(str(self.id)+ '>step<')



            # while True:
            #     time.sleep(1)
            #     self.result_queue.put(self.id)
            #     logV(time.time())

            return

        except Exception as e:
            logE(Exception, e)
            import traceback
            logE(traceback.print_exc())
            DATA.op('TEST_FAILURES,1,Exception,N/A,N/A')
        finally:
            DATA.end_content()
            logV( '\nTotal cost:', time.time() - t0)
            DATA.end_process()
            self.result_queue.put(str(self.id) + '>finish<')