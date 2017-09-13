import subprocess
import time
from data import *

from Temperature import *

class DTS():
    def __init__(self,argv):
        if DATA.id==1:
            DATA.ble_mac='31:38:42:30:43:39'
        elif DATA.id==2:
            DATA.ble_mac='31:38:42:30:43:42'
        pass
        logV(DATA.ble_mac)

    def enable_disable_ble(self,argv):
        cmd=argv['exe']
        rtbuf=''
        logV(cmd)
        try:
            barrier=DATA.barriers[argv['barrier']]
        except:
            barrier=None
        try:
            if barrier.acquire():
                p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     cwd='.', shell=False)
                # p.stdin.write('25382564\n')
                while p.poll() == None:
                    buf=p.stdout.readline()
                    logV(buf)
                    rtbuf+=buf
                    time.sleep(0.005)
                buf=p.stdout.read()
                logV(buf)
                rtbuf += buf
                logV('return code:', p.returncode)

                return rtbuf
            else:
                logV('bypass')
        except Exception,e:
            logV(Exception,e)
            return ''
        finally:
            time.sleep(2)
            barrier.release()

    def callexe(self,argv):
        cmd=argv['exe']
        try:
            cmd=cmd.replace('31:38:42:30:43:39',DATA.ble_mac)
        except:
            pass
        rtbuf=''
        logV(cmd)
        try:
            lock = DATA.locks[argv['lock']]
            with lock:
                p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)
                time.sleep(3)
            # p.stdin.write('25382564\n')
            while p.poll() == None:
                buf=p.stdout.readline()
                logV(buf)
                rtbuf+=buf
                time.sleep(0.005)
            buf=p.stdout.read()
            logV(buf)
            rtbuf += buf
            logV('return code:', p.returncode)
            if p.returncode!=0:
                DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return rtbuf
        except Exception,e:
            logV(Exception,e)
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return ''

    def GetMiddleStr(self,content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
            endIndex = content.index(endStr,startIndex)
            return content[startIndex:endIndex]
        else:
            return ''

    def getdutversion(self,argv):
        cmd=argv['exe']
        try:
            cmd=cmd.replace('31:38:42:30:43:39',DATA.ble_mac)
        except:
            pass
        rtbuf=''
        logV(cmd)
        try:
            lock = DATA.locks[argv['lock']]
            with lock:
                p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)
                time.sleep(3)
            # p.stdin.write('25382564\n')
            while p.poll() == None:
                buf=p.stdout.readline()
                logV(buf)
                rtbuf+=buf
                time.sleep(0.005)
            buf=p.stdout.read()
            logV(buf)
            rtbuf += buf
            logV('return code:', p.returncode)
            if p.returncode!=0:
                DATA.op('TEST_READ_FW_VERSION_MLB,1,FAIL,N/A,N/A')
                DATA.op('TEST_READ_FW_VERSION_FATP,1,FAIL,N/A,N/A')
            else:
                try:
                    version=self.GetMiddleStr(rtbuf,'Write Command:','Send Command').strip()
                    version = self.GetMiddleStr(version, 'Version:', '\r').strip()
                    DATA.op('TEST_READ_FW_VERSION_MLB,0,'+version+',N/A,N/A')
                    DATA.op('TEST_READ_FW_VERSION_FATP,0,'+version+',N/A,N/A')
                except:
                    pass

        except Exception,e:
            logV(Exception,e)
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return ''

    def getdutinfo(self,argv):
        realinfo={'TEST_READ_ISN_MLB':'mlb#',
                  'TEST_READ_ISN_FATP':'S#',
                  'TEST_READ_FACTORY_CONFIG_MLB':'mlbconfig',
                  'TEST_READ_FACTORY_CONFIG_FATP': 'config',
                  'TEST_READ_MODEL_MLB':'nlmodel',
                  'TEST_READ_MODEL_FATP': 'nlmodel'}
        cmd=argv['exe']
        try:
            cmd=cmd.replace('31:38:42:30:43:39',DATA.ble_mac)
        except:
            pass
        logV(cmd)
        rtbuf=''
        info={}
        try:
            lock = DATA.locks[argv['lock']]
            with lock:
                p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)
                time.sleep(3)
            # p.stdin.write('25382564\n')
            while p.poll() == None:
                buf=p.stdout.readline()
                logV(buf)
                #rtbuf+=buf
                if buf.find('=')>=0:
                    try:
                        infos=buf.strip().split('=')
                        info[infos[0]]=infos[1]
                    except:
                        pass
                time.sleep(0.005)
            buf=p.stdout.read()
            logV(buf)
            rtbuf += buf
            logV('return code:', p.returncode)
            for key in realinfo:
                try:
                    DATA.op(key+','+'0'+','+info[realinfo[key]]+',N/A,N/A')
                except:
                    DATA.op(key + ',1,FAIL,N/A,N/A')
            return rtbuf
        except Exception,e:
            logV(Exception,e)
            DATA.op(argv['name']+','+'1,FAIL,N/A,N/A')
            return ''

    def grabtemp(self,argv):
        cmd = argv['exe']
        try:
            cmd=cmd.replace('31:38:42:30:43:39',DATA.ble_mac)
        except Exception,e:
            logD(Exception,e)
            pass
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        logV(cmd)
        rtbuf = ''
        the_buf=''
        h_buf=''
        s_buf=''
        t_buf=''
        try:
            lock = DATA.locks[argv['lock']]
            with lock:
                p = subprocess.Popen(cmd, 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd='.', shell=False)

            # p.stdin.write('25382564\n')
            ix=0
            if DATA.id==1:
                tempfn='Temperature1.csv'
            elif DATA.id==2:
                tempfn = 'Temperature2.csv'
            with open(tempfn,'w') as fw:
                fw.write('Time,Heater_Temp,Ambient_Temp,MainTempSensor,Thermistor_1\n')
                while p.poll() == None:
                    buf = p.stdout.readline()
                    logV(buf)

                    try:

                        ix+=1
                        if(ix<=11):
                            continue
                        try:
                            ts_dut = buf.strip().split(':')
                            if len(ts_dut)!=3:
                                continue
                        except:
                            continue
                        logV(ts_dut)
                        rtbuf += str(float(ts_dut[1].strip())/10) + ';'
                        the_buf += ts_dut[2].strip() + ';'
                        t_buf+=ts_dut[0].strip() + ';'
                        temp=DATA.objs['temp']

                        t_h=temp.readtemp({"name":"TEMPERATURE_READ","obj" : "temp","action": "readtemp",
                                        "cmd":"01 03 00 00 00 02 C4 0B","end":"","has":"01 03","timeout":"1"})
                        h_buf+=str(t_h)+';'
                        fixture=DATA.objs['fixture']
                        if lock:
                            with lock:
                                if DATA.id==1:
                                    fixture._connect()
                                    rt,v=fixture.wr(cmd='READ T1\r',end="@^@")
                                    fixture.disconnect()
                                elif DATA.id==2:
                                    fixture._connect()
                                    rt, v = fixture.wr(cmd='READ T2\r', end="@^@")
                                    fixture.disconnect()
                        else:
                            rt, v = fixture.wr(cmd='READ T1\r', end="@^@")
                        logV(rt,v)
                        if rt:
                            ts_s=v.split('\r')[1].strip()
                        else:
                            ts_s='-999'
                        logV(ts_s)
                        s_buf+=ts_s+';'
                        fw.write(ts_dut[0]+','+str(t_h)+','+ts_s+','+str(float(ts_dut[1].strip())/10)+','+ts_dut[2]+'\n')
                    except Exception,e:
                        logV(Exception,e,'Skip.')

                    #rtbuf += buf
                    time.sleep(0.005)
            buf = p.stdout.read()
            logV(buf)
            ##TEST_TEMP112_RAW
            ##TEST_THERMISTOR_RAW
            ##TEST_THERMISTOR_CONVERTED
            ##TEST_AMBIENT_TEMP_RAW
            ##TEST_HEATER_RAW

            DATA.op('TEST_TIME_RAW,0,' + t_buf + ',N/A,N/A')
            DATA.op('TEST_TEMP112_RAW,0,'+rtbuf+',N/A,N/A')
            DATA.op('TEST_THERMISTOR_RAW,0,' + the_buf + ',N/A,N/A')
            DATA.op('TEST_HEATER_RAW,0,' + h_buf + ',N/A,N/A')
            DATA.op('TEST_AMBIENT_TEMP_RAW,0,' + s_buf + ',N/A,N/A')
            #rtbuf += buf
            logV('return code:', p.returncode)
            try:
                df = pd.read_csv(tempfn, dtype=str)
                result = dtsAlgo(df)
            except Exception,e:
                logE('dtsAlgo error:',Exception,e)
                result={}
                result["TEST_TEMPERATURE_TMP112_IDLE_TIME"] = 99999
                result["TEST_TEMPERATURE_TMP112_IDLE_TIME_TEMP_RISE"] = 99999
                result["TEST_TEMPERATURE_TMP112_EXP_CURVE_CONSTANT_A"] = 99999
                result["TEST_TEMPERATURE_TMP112_EXP_CURVE_CONSTANT_B"] = 99999
                result["TEST_TEMPERATURE_TMP112_EXP_CURVE_CONSTANT_C"] = 99999
                result["TEST_TEMPERATURE_TMP112_RAW_STEADY_STATE_VALUE"] = 99999
                result["TEST_TEMPERATURE_TMP112_RAW_TIME_CONSTANT"] = 99999
                result["TEST_TEMPERATURE_TMP112_RAW_SETTLE_TIME"] = 99999
                result["TEST_TEMPERATURE_TMP112_COMP_STEADY_STATE_VALUE"] = 99999
                result["TEST_TEMPERATURE_TMP112_COMP_TIME_CONSTANT"] = 99999
                result["TEST_TEMPERATURE_TMP112_COMP_SETTLE_TIME"] = 99999
                result["TEST_TEMPERATURE_HEATER_PLATE_STD_DEV"] = 99999
                result["TEST_TEMPERATURE_HEATER_PLATE_MAX"] = 99999
                result["TEST_TEMPERATURE_HEATER_PLATE_MIN"] = 99999
                result["TEST_TEMPERATURE_AMBIENT_STD_DEV"] = 99999
                result["TEST_TEMPERATURE_AMBIENT_MAX"] = 99999
                result["TEST_TEMPERATURE_AMBIENT_MIN"] = 99999
                result["TEST_TEMPERATURE_APPLIED_STEP"] = 99999
                result["TEST_TEMPERATURE_DUT_PERCEIVED_STEP"] = 99999
                result["TEST_THERMISTOR_CONVERTED"] = 99999
                result["TEST_TEMPERATURE_TMP112_LAST_VALUE"] = 99999
                result["TEST_TEMPERATURE_TMP112_MAX"] = 99999
                result["TEST_TEMPERATURE_TMP112_MIN"] = 99999
                result["TEST_TEMPERATURE_TMP112_FIRST_VALUE"] = 99999
                result["THERMISTOR_STD_DEV"] = 99999
                result["TEST_TEMPERATURE_THERMISTOR_MAX"] = 99999
                result["TEST_TEMPERATURE_THERMISTOR_MIN"] = 99999

            logV( result)
            if len(result)==0:
                DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            for key in result.keys():
                DATA.op(key+','+'0'+',\"'+str(result[key])+'\",N/A,N/A')
            return rtbuf
        except Exception, e:
            logV(Exception, e)
            DATA.op(argv['name'] + ',' + '1,FAIL,N/A,N/A')
            return ''