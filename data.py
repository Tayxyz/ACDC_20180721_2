import threading
import time,datetime
import os
import sys
import ConfigParser

Lock = threading.Lock()

class data():
    __instance = None
    __time = time.time()

    def __init__(self):
        self.PROJECT = 'DEFAULT'
        self.BUILD_EVENT = 'DEFAULT'
        self.STATION_NAME = 'DEFAULT'
        self.DEVICE_ID = 'DEFAULT'
        self.STATION_MODE = 'DEFAULT'
        self.LOG_PATH = 'log'
        self.totalfails = 0
        self.repair = 0
        self.currentpass = True
        self.test_failures=''
        self.error=''
        self.full_info = []
        self.csv = []
        self.error_code=''
        self.logStreamData = ''

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                Lock.acquire()
                # double check
                if not cls.__instance:
                    cls.__instance = super(data, cls).__new__(cls, *args, **kwargs)
                    cls.__time = time.time()
            finally:
                Lock.release()
        return cls.__instance

    def find_errorcode(self,fail):
        try:
            with open('errorcode.txt') as f:
                for line in f:
                    if fail in line:
                        return line.strip().split()[1]
            return ''
        except:
            return ''

    def create_streamData(self):
        self.logStreamData = 'TEST,STATUS,VALUE,U_LIMIT,L_LIMIT\n'

        final = 0
        fails = ''
        for line in self.csv:
            items = line.split(',')
            if items[1] == '1':
                self.logStreamData += line
                final = final + 1
                if fails == '':
                    fails = items[0]
                break

        if final > 0:
            self.error_code = self.find_errorcode(fails)
            if not len(self.error_code) == 6:
                self.error_code = 'WIEOTR'
        else:
            self.error_code = ''

        logV(self.error_code)
        logV( self.logStreamData)

    def end_content(self):

        final = 0
        fails = ''
        for line in self.csv:
            items = line.split(',')
            if items[1] == '1':
                final = final + 1
                if fails == '':
                    fails = items[0]

        if final > 0:
            pf = 'FAIL'
            self.error_code=self.find_errorcode(fails)
            if not len(self.error_code)==6:
                self.error_code='WIEOTR'
        else:
            pf = 'PASS'

        if DATA.STATION_ONLINE=='YES':
            onoffline='ON_LINE'
        else:
            onoffline='OFF_LINE'
        logV( DATA.PROJECT, DATA.BUILD_EVENT, DATA.STATION_NAME, DATA.DEVICE_ID, onoffline)

        if self.LOG_PATH.endswith(os.sep):
            self.LOG_PATH = self.LOG_PATH[:self.LOG_PATH.rindex(os.sep)]

        dirpath=DATA.PROJECT + os.sep + DATA.BUILD_EVENT + os.sep + DATA.STATION_NAME + os.sep \
                 + DATA.DEVICE_ID + os.sep + onoffline + os.sep + pf + os.sep + datetime.datetime.now().strftime(
            '%Y%m%d')

        logdir = self.LOG_PATH + os.sep + dirpath
        logV(logdir)



        try:
            os.makedirs(logdir)
        except Exception as e:
            logD( Exception, e)

        if len(self.error_code)==6:
            erc=self.error_code+'_'
        else:
            erc=''

        filename=DATA.isn + '_'+erc + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        self.csvfilename = logdir + os.sep + filename + '.csv'
        self.cpkfilename = logdir + os.sep + filename + '.cpk'
        self.logfilename = logdir + os.sep + filename + '.debug'

        with open(self.csvfilename, 'w') as f:
            for line in self.csv:
                f.write(line)
                f.write('\n')

        spc_id='N/A'
        spc_iteration='N/A'
        if DATA.STATION_MODE=='SPC':
            flagfilename='CONSISTENCY_'+str(DATA.id)
            try:
                with open(flagfilename,'r') as  f:
                    content= f.read()
                    spc_id,spc_iteration=content.split(';')

                if not final>0:
                    xx=str(int(spc_iteration)+1)
                    with open(flagfilename,'w') as fw:
                        fw.write(spc_id)
                        fw.write(';')
                        fw.write(xx)

            except Exception as e:
                with open(flagfilename,'w') as fw:
                    spc_id='CONSISTENCY_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    fw.write(spc_id)
                    if final>0:
                        fw.write(';1')
                    else:
                        fw.write(';2')
                    spc_iteration='1'

        else:
            pass

        with open(self.csvfilename, 'a') as f:
            f.write('SPC_RUN_ID,0,'+spc_id+',N/A,N/A\n')
            self.op('SPC_RUN_ID,0,'+spc_id+',N/A,N/A')
            f.write('SPC_ITERATION,0,'+spc_iteration+',N/A,N/A\n')
            self.op('SPC_ITERATION,0,'+spc_iteration+',N/A,N/A')

        if final > 0:
            self.op('OVERALL_TEST_RESULT,1,FAIL,N/A,N/A')
            # self.final_result(fails, self.csvfilename)
            with open(self.csvfilename, 'a') as f:
                f.write('OVERALL_TEST_RESULT,1,FAIL,N/A,N/A')
        else:
            self.op('OVERALL_TEST_RESULT,0,PASS,N/A,N/A')
            # self.final_result('PASS', self.csvfilename)
            with open(self.csvfilename, 'a') as f:
                f.write('OVERALL_TEST_RESULT,0,PASS,N/A,N/A')

        with open(self.cpkfilename, 'w') as f:
            for line in self.full_info:
                f.write(line)
                f.write('\n')

        with open(DATA.logfilepath,'r') as fr:
            with open(self.logfilename,'w') as fw:
                fw.write(fr.read())

        try:#upload to server
            directory = "/vault/logserver"
            serverdir = directory + os.sep + dirpath
            logV( serverdir)

            try:
                os.makedirs(serverdir)
            except Exception as e:
                pass
            import shutil
            shutil.copy(self.csvfilename,serverdir+ os.sep + filename+ '.csv')
            shutil.copy(self.cpkfilename,serverdir + os.sep + filename+ '.cpk')

            pass
        except Exception as e:
            logE( Exception,e)
        finally:
            if final > 0:
                self.final_result(fails, logdir+';'+serverdir+';'+filename)
            else:
                self.final_result('PASS', logdir+';'+serverdir+';'+filename)

    def final_result(self,pf,log):
        logV(str(self.id),pf,log)
        DATA.result_queue.put(str(self.id) + ';'+pf)
        pass

    def end_process(self):
        pass

    def settime(self):
        data.__time = time.time()

    def op(self, format_content, ui=True, csv=True, ):
        logV( format_content)
        items = format_content.split(',')
        if len(items) != 5:
            logE( 'output error! Please check!')
            return
        if items[1].strip() == '1':
            self.totalfails += 1
            self.currentpass = False
            if len(self.test_failures)!=0:
                self.test_failures+=';'
            self.test_failures += items[0]

        else:
            self.currentpass = True

        cur = time.time()
        cost = cur - data.__time
        data.__time = cur
        self.full_info.append(format_content + ',' + '%.2f' % cost)
        if csv:
            self.csv.append(format_content)
        # if ui:
        #     sys.stderr.write(format_content + ',' + '%.2f' % cost)

    def getatparameter(self, key):
        try:
            cf = ConfigParser.ConfigParser()
            cf.read(DATA.setting_name)
            return cf.get(key, DATA.id)
        except Exception as e:
            logE( Exception, e)
            return ''

    def read_setting(self):
        DATA.op('TEST,STATUS,VALUE,U_LIMIT,L_LIMIT', ui=False)
        # 'TEST_DATE_TIME',  # start time
        DATA.op('TEST_DATE_TIME,0,' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ',N/A,N/A')
        cf = ConfigParser.ConfigParser()
        cf.read(DATA.setting_name)

        DATA.PROJECT = cf.get('basic_info', 'PROJECT')
        DATA.LOG_PATH = cf.get('basic_info', 'LOG_PATH')

        DATA.STATION_NAME = cf.get('basic_info', 'STATION_NAME')
        DATA.op('STATION_NAME' + ',0,' + DATA.STATION_NAME + ',N/A,N/A')
        DATA.LINE_NUMBER = cf.get('basic_info', 'LINE_NUMBER')
        DATA.op('LINE_NUMBER' + ',0,' + DATA.LINE_NUMBER + ',N/A,N/A')
        DATA.STATION_ONLINE = cf.get('basic_info', 'STATION_ONLINE')
        if DATA.STATION_ONLINE=='YES':
            DATA.op('STATION_ONLINE' + ',0,' + '1' + ',N/A,N/A')
        else:
            DATA.op('STATION_ONLINE' + ',0,' + '0' + ',N/A,N/A')
        DATA.BUILD_EVENT = cf.get('basic_info', 'BUILD_EVENT')
        DATA.op('BUILD_EVENT' + ',0,' + DATA.BUILD_EVENT + ',N/A,N/A')
        DATA.FIXTURE_ID = cf.get('basic_info', 'FIXTURE_ID')
        DATA.op('FIXTURE_ID' + ',0,' + DATA.FIXTURE_ID + ',N/A,N/A')
        DATA.op('FIXTURE_INDEX' + ',0,' + str(DATA.id) + ',N/A,N/A')
        DATA.DEVICE_ID = cf.get('basic_info', 'DEVICE_ID')
        DATA.op('DEVICE_ID' + ',0,' + DATA.DEVICE_ID + ',N/A,N/A')
        DATA.STATION_MODE = cf.get('basic_info', 'STATION_MODE')
        if DATA.STATION_ONLINE=='YES' and not DATA.STATION_MODE=='ONLINE':
            DATA.op('STATION_MODE' + ',1,' + DATA.STATION_MODE + ',N/A,N/A')
        elif not DATA.STATION_ONLINE=='YES' and DATA.STATION_MODE=='ONLINE':
            DATA.op('STATION_MODE' + ',1,' + DATA.STATION_MODE + ',N/A,N/A')
        else:
            DATA.op('STATION_MODE' + ',0,' + DATA.STATION_MODE + ',N/A,N/A')
        DATA.USER_ID = cf.get('basic_info', 'OPID')
        if len(DATA.USER_ID)!=9:
            DATA.USER_ID='S09654321'
        DATA.op('USER_ID' + ',0,' + DATA.USER_ID + ',N/A,N/A')
        ####
        DATA.sfis_url=cf.get('sfis', 'url')
        DATA.sfis_tsp=cf.get('sfis', 'tsp')
        DATA.repair = cf.get('sfis', 'repair')
        DATA.provision_ip=cf.get('provision','ip')
        DATA.dl_py = cf.get('dl', 'py')
        DATA.logserver = cf.get('logserver', 'url')
        # print DATA.PROJECT, DATA.BUILD_EVENT, DATA.STATION_NAME, DATA.DEVICE_ID, DATA.STATION_MODE




DATA=data()
DATA.logfilepath=''

########## LOG #############
def logV(*args):
    v=' '.join([str(s) for s in args])
    with open(DATA.logfilepath,'a') as fa:
        fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        fa.write('[verbose] ')
        fa.write(v)

def logE(*args):
    v=' '.join([str(s) for s in args])
    with open(DATA.logfilepath,'a') as fa:
        fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        fa.write('[error] ')
        fa.write(v)

def logD(*args):
    v=' '.join([str(s) for s in args])
    with open(DATA.logfilepath,'a') as fa:
        fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        fa.write('[debug] ')
        fa.write(v)