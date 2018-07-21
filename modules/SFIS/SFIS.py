from data import *
from MySFIS import SFISWebService
import COMMON.dialog as dialog

def GetMiddleStr( content, startStr, endStr):
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
        endIndex = content.index(endStr, startIndex)
        return content[startIndex:endIndex]
    else:
        return ''

class SFIS():
    def __init__(self, argv):
        self.sfis=SFISWebService(DATA.sfis_url,DATA.DEVICE_ID,DATA.sfis_tsp)


    def SFIS_LOGIN_DB(self,argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None


        try:
            if lock:
                lock.acquire()

            logV(self.sfis.SFIS_Connect())
            r,s= self.sfis.SFIS_Login(DATA.USER_ID,'1')
            logV( r,repr(s))
            if r=='1' or s.find('Login Twice')>=0:
                DATA.op(argv['name']+',0,PASS,N/A,N/A')
            else:
                DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE( Exception,e)
        finally:
            if lock:
                lock.release()



    def SFIS_CHECK_ROUTE(self, argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            r, s = self.sfis.SFIS_CheckRoute(DATA.isn)
            logV( r, repr(s))

            if r =='1': ## PASS return
                DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
                return
            if r=='0' and 'REPAIR OF' in s:
                #repair
                #if time ok
                t = GetMiddleStr(s,'LF#:',']')
                try:
                    int(t)
                except:
                    t='0'
                # over repair return
                if int(DATA.repair)>0 and int(DATA.repair)<=int(t):
                    dlg = dialog.dialog(argv)
                    dlg.info({'msg': 'OVER REPAIR COUNT = %s'%t})
                    DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
                    return

                ## AAB return
                if DATA.AAB == 'YES':
                    r, s = self.sfis.SFIS_GetVersion(DATA.isn, 'MO_D', 'DEVICE')
                    logV(r, repr(s))
                    if r !='1' or s.find('DATA GET OK')==-1:
                        dlg = dialog.dialog(argv)
                        dlg.info({'msg': 'get device fail'})
                        DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
                        return
                    items = s.split(chr(127))
                    try:
                        predeviceid = items[1]
                    except:
                        predeviceid = 'UNKNOW'
                    if predeviceid==DATA.DEVICE_ID and int(t)%2==1:
                        dlg = dialog.dialog(argv)
                        dlg.info({'msg': 'AAB:should not test on device:%s'%predeviceid})
                        DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
                        return
                    elif predeviceid!=DATA.DEVICE_ID and int(t)%2==0:
                        dlg = dialog.dialog(argv)
                        dlg.info({'msg': 'AAB:should test on device:%s' % predeviceid})
                        DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
                        return

                ## repaire PASS return
                r,s = self.sfis.SFIS_Repair(DATA.isn)
                logV( r,repr(s))
                if r=='1':
                    r, s = self.sfis.SFIS_CheckRoute(DATA.isn)
                    logV( r,repr(s))
                    if r=='1':
                        DATA.op(argv['name']+',0,PASS,N/A,N/A')
                        return

            ##  Fail return
            dlg = dialog.dialog(argv)
            dlg.info({'msg':s})
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            return
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')


    def TEST_READ_FACTORY_CONFIG(self,argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(DATA.isn,'GET_CONFIG','MO_MEMO')
                logV( r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>3 and len(items[1])>0:
                    DATA.op(argv['name']+',0,'+items[1]+',N/A,N/A')
                    DATA.mlbconfig=items[1]
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')


    def TEST_READ_FACTORY_CONFIG_MLB(self,argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(DATA.isn,'GET_CONFIG','MO_MEMO','MEMOCLS,RSDATE')
                logV( r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>3 and len(items[1])>0:
                    DATA.op(argv['name']+',0,'+items[1]+',N/A,N/A')
                    DATA.mlbconfig=items[1]
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')

    def BUILD_PHASE(self,argv):
        if not DATA.STATION_ONLINE=='YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(DATA.isn,'GET_CONFIG','MO_MEMO','MEMOCLS,RSDATE')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>3 and len(items[2])>0:
                    DATA.op(argv['name']+',0,'+items[2]+',N/A,N/A')
                    DATA.build_phase=items[2]
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')


    def TEST_GET_6LOWPAN_MAC(self,argv):
        if not DATA.STATION_ONLINE=='YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r,s = self.sfis.SFIS_GetI1394(DATA.isn)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>1 and len(items[1])==16:
                    DATA.MAC_6LOWPAN=':'.join([items[1][x:x+2] for x in range(0,16,2)])

                    DATA.op(argv['name']+',0,'+DATA.MAC_6LOWPAN+',N/A,N/A')
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')


    def TEST_GET_WIFI_MAC(self,argv):
        if not DATA.STATION_ONLINE=='YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r,s = self.sfis.SFIS_GetIMAC(DATA.isn)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            items= s.split(chr(127))
            if len(items)>1 and len(items[1])==12:
                DATA.MAC_WIFI=':'.join([items[1][x:x+2] for x in range(0,12,2)])

                DATA.op(argv['name']+',0,'+DATA.MAC_WIFI+',N/A,N/A')
                return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')

    def SFIS_WRITE_RESULT(self,argv):
        if not DATA.STATION_ONLINE=='YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')
            DATA.create_streamData()
            r, s = self.sfis.SFIS_TestResult(DATA.isn, DATA.error_code, DATA.logStreamData)
            logV(r, repr(s))
            if r=='0':
                DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
            else:
                DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')

    def SFIS_LOGOUT_DB(self,argv):
        DATA.op(argv['name'] + ',0,PASS,N/A,N/A')


    def GET69_BY_80(self,argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None


        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(DATA.isn,'MOKP_SN')
                logV( r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>3 and len(items[1])>0:
                    DATA.op(argv['name']+',0,'+items[1]+',N/A,N/A')
                    DATA.isn69=items[1]
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')

    def TEST_GETISNINFO(self,argv):
        if not DATA.STATION_ONLINE == 'YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:
            lock=DATA.locks[argv['lock']]
        except:
            lock=None

        try:
            type=argv['type']
        except:
            type='MAC2'

        try:
            if lock:
                lock.acquire()
                logV('lock.acquire')

            for i in range(3):
                if argv['name'].find('BLE_MAC')>0:
                    r, s = self.sfis.SFIS_GetVersion(DATA.isn69,'ISN_BASEINFO',type)
                    logV(DATA.isn69)
                else:
                    r, s = self.sfis.SFIS_GetVersion(DATA.isn, 'ISNINFO_INFO', type)
                logV( r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r=='1':
                items= s.split(chr(127))
                if len(items)>3 and len(items[1])>0:

                    if argv['name'].find('BLE_MAC')>0:
                        blemac=items[1]
                        DATA.ble_mac=':'.join(blemac[i:i+2] for i in range(0,12,2))
                        logV('ble_mac=',DATA.ble_mac)
                        DATA.op(argv['name'] + ',0,' + DATA.ble_mac + ',N/A,N/A')
                    return
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            logE(Exception,e)
        finally:
            if lock:
                lock.release()
                logV('lock.release')

    def get69by80(self, isn80):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn80, 'MOKP_SN')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def getnextisn(self,thisisn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(thisisn, 'ITEMINFO')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 4 and len(items[4]) > 0:
                    return items[4]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_config(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn, 'GET_CONFIG', 'MO_MEMO')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_mlb_config(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn,'GET_CONFIG','MO_MEMO','MEMOCLS,RSDATE')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_buildphase(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn,'GET_CONFIG','MO_MEMO','MEMOCLS,RSDATE')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[2]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_mlb_pre_config(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn,'GET_CONFIG','PREMO_MO_MEMO','MEMOCLS,RSDATE')
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_mlb_snx(self,isn,snx):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn, 'ISN_BASEINFO', snx)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_fatp_snx(self,isn,snx):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn, 'ISNINFO_INFO', snx)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_6lowpan_mac(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetI1394(isn)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 1 and len(items[1]) == 16:
                    return ':'.join([items[1][x:x + 2] for x in range(0, 16, 2)])
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_wifi_mac(self, isn):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetIMAC(isn)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            items = s.split(chr(127))
            if len(items) > 1 and len(items[1]) == 12:
                return ':'.join([items[1][x:x + 2] for x in range(0, 12, 2)])
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'

    def get_keypart(self,isn,kpbc):
        try:
            for i in range(3):
                r, s = self.sfis.SFIS_GetVersion(isn, 'MOKP_SN',kpbc)
                logV(r, repr(s))
                if r == '1':
                    break
                else:
                    logV('retry')
            if r == '1':
                items = s.split(chr(127))
                if len(items) > 3 and len(items[1]) > 0:
                    return items[1]
            return 'ERROR'
        except Exception, e:
            logE(Exception, e)
            return 'ERROR'


if __name__=='__main__':
    print GetMiddleStr('this is test[] for [lf#111] []','[x','1]')
