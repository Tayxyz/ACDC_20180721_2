from data import *
import  datetime
import  ConfigParser
import time
class BasicInfo():
    def __init__(self,argv):
        self.basicitems_fromsetting = [
            'STATION_NAME',  # from setting.ini
            'LINE_NUMBER',
            'STATION_ONLINE',
            'BUILD_EVENT',
            'FIXTURE_ID',
            'DEVICE_ID',
            'STATION_MODE',
            # 'SCRIPT_VERSION',
            # 'LIMITS_VERSION',
            # 'STATION_SW_VERSION'
            ]

        self.basicitems_bycallfunc = [
            'STATION_MAC',
        ]

        self.basicitems_byisn = [
            'PRODUCT_CODE',  # part of ISN
            'PRODUCT_NAME',
            'PRODUCT_NAME_DESC',
            'PRODUCT_TYPE',
            'PRODUCT_TYPE_DESC',
            'PRODUCT_VERSION',
            'PRODUCT_VERSION_DESC',
            'PRODUCT_REVISION',
            'MFG_LOCATION',
            'MFG_LOCATION_DESC',
            'MFG_WW',
            'MFG_YEAR',
        ]

        self.basicitems_bysfis = [

            # 'SFIS_LOGIN_DB', #SFIS
            # 'SFIS_CHECK_ROUTE',#SFIS
            # 'BUILD_PHASE',#SFIS
            # 'SFIS_WRITE_RESULT',  # SFIS
            # 'SFIS_LOGOUT_DB',  # SFIS
        ]
        self.basicitems_tail = [

            'TEST_FAIL_ITEM_QTY',
            'TEST_FAILURES',

            'TEST_END_TIME',
            'OVERALL_TEST_RESULT',
            'TOTAL_TEST_TIME',
        ]




    def isninfo(self):

        PRODUCT_NAME_DESC = {'21A':'M1','26A':'M1','21C':'TR1','26C':'TR1','22':'KR1'}
        PRODUCT_TYPE_DESC = {'A':'NA'}
        PRODUCT_CODE_DESC = {'22A':'KR1 FATP','21A': 'M1 FATP','26A': 'M1 FATP','21B': 'M1 MLB','21D': 'M1 Interface MLB','24A': 'TR1 FATP','21C': 'TR1 FATP','26C': 'TR1 FATP','24B': 'TR1 MLB','24D': 'TR1 Daughter MLB'}
        PRODUCT_VERSION_DESC = {'A':'WHITE'}
        MFG_LOCATION_DESC = {'AB':'Pegatron Protek Shanghai','AC':'PEGATRON_MAINTEK_SUZHOU','RA':'Pegatron Protek Shanghai','RC':'Pegatron Maintek Suzhou'}

        isn_info={}
        isn_info['PRODUCT_NAME'] = DATA.isn[0:2]
        isn_info['PRODUCT_TYPE'] = DATA.isn[2:3]
        isn_info['PRODUCT_CODE'] = DATA.isn[0:3]
        isn_info['PRODUCT_VERSION'] = DATA.isn[3:4]
        isn_info['PRODUCT_REVISION'] = DATA.isn[4:6]
        isn_info['MFG_LOCATION'] = DATA.isn[6:8]
        isn_info['MFG_WW'] = DATA.isn[8:10]
        isn_info['MFG_YEAR'] = DATA.isn[10:12]


        try:
            isn_info['PRODUCT_CODE_DESC'] = PRODUCT_CODE_DESC[isn_info['PRODUCT_CODE']]
        except:
            isn_info['PRODUCT_CODE_DESC'] = 'NA'
        # try:
        #     isn_info['PRODUCT_TYPE_DESC'] = PRODUCT_TYPE_DESC[isn_info['PRODUCT_TYPE']]
        # except:
        #     isn_info['PRODUCT_TYPE_DESC'] = 'NA'
        isn_info['PRODUCT_TYPE_DESC']=isn_info['PRODUCT_CODE_DESC'] #follow NAPA instruction
        try:
            isn_info['PRODUCT_NAME_DESC'] = PRODUCT_NAME_DESC[isn_info['PRODUCT_CODE']]
        except:
            isn_info['PRODUCT_NAME_DESC'] = 'NA'

        try:
            isn_info['PRODUCT_VERSION_DESC'] = PRODUCT_VERSION_DESC[isn_info['PRODUCT_VERSION']]
        except:
            isn_info['PRODUCT_VERSION_DESC'] = 'NA'
        try:
            isn_info['MFG_LOCATION_DESC'] = MFG_LOCATION_DESC[isn_info['MFG_LOCATION']]
        except:
            isn_info['MFG_LOCATION_DESC'] = 'NA'

        DATA.op('PRODUCT_CODE' + ',0,' + isn_info['PRODUCT_CODE'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_CODE_DESC' +  ',0,' + isn_info['PRODUCT_CODE_DESC'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_NAME' +  ',0,' + isn_info['PRODUCT_NAME'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_NAME_DESC' + ',0,' + isn_info['PRODUCT_NAME_DESC'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_TYPE' +  ',0,' + isn_info['PRODUCT_TYPE'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_TYPE_DESC' + ',0,' + isn_info['PRODUCT_TYPE_DESC'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_VERSION' +  ',0,' + isn_info['PRODUCT_VERSION'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_VERSION_DESC' +  ',0,' + isn_info['PRODUCT_VERSION_DESC'] + ',N/A,N/A',ui=False)
        DATA.op('PRODUCT_REVISION' +  ',0,' + isn_info['PRODUCT_REVISION'] + ',N/A,N/A',ui=False)
        DATA.op('MFG_LOCATION' +  ',0,' + isn_info['MFG_LOCATION'] + ',N/A,N/A',ui=False)
        DATA.op('MFG_LOCATION_DESC' +  ',0,' + isn_info['MFG_LOCATION_DESC'] + ',N/A,N/A',ui=False)
        DATA.op('MFG_WW' + ',0,'+ isn_info['MFG_WW'] + ',N/A,N/A',ui=False)
        DATA.op('MFG_YEAR' +  ',0,' + isn_info['MFG_YEAR'] + ',N/A,N/A',ui=False)


    def record_isn(self,argv):
        DATA.op(argv['name']+',0,'+DATA.isn+',N/A,N/A')


    def basic_info(self,argv):
        DATA.op('SCRIPT_VERSION' + ',0,' + DATA.script_name[DATA.script_name.index('/')+1:DATA.script_name.index('.')] + ',N/A,N/A')
        DATA.op('LIMITS_VERSION' + ',0,' + DATA.script_name[DATA.script_name.index('/')+1:DATA.script_name.index('.')] + ',N/A,N/A')
        DATA.op('STATION_SW_VERSION' + ',0,' + DATA.version + ',N/A,N/A')
        DATA.op('STATION_MAC' + ',0,' + self.get_pc_macaddress()+',N/A,N/A')
        DATA.op('REL_STATUS' + ',0,N/A,N/A,N/A', ui=False)
        self.isninfo()

    def fatp_isn_config_stuff(self,argv):
        self.isn80 = DATA.isn
        DATA.op('TEST_READ_ISN_FATP,0,%s,N/A,N/A'%DATA.isn)

        sfis = DATA.objs['sfis']
        logD(type(sfis))
        # self.isn69 = sfis.get69by80(self.isn80)
        # DATA.op('TEST_READ_ISN_MLB,0,%s,N/A,N/A'%self.isn69)

        CONFIG_FATP = sfis.get_config(self.isn80)
        DATA.op('TEST_READ_FACTORY_CONFIG_FATP,0,%s,N/A,N/A'%CONFIG_FATP)

        # MLBCONFIG = sfis.get_mlb_pre_config(self.isn69)
        # DATA.op('TEST_READ_FACTORY_CONFIG_MLB,0,%s,N/A,N/A'%MLBCONFIG)

    def wait(self, argv):
        time.sleep(float(argv['seconds']))

    def end_steps(self,argv):
        #TEST_FAIL_ITEM_QTY
        DATA.op('TEST_FAIL_ITEM_QTY' + ',0,' + str(DATA.totalfails) + ',N/A,N/A')
        #TEST_FAILURES
        if len(DATA.test_failures):
            DATA.op('TEST_FAILURES' + ',0,' + str(DATA.test_failures) + ',N/A,N/A')
        else:
            DATA.op('TEST_FAILURES' + ',0,NULL,N/A,N/A')
        #TEST_END_TIME
        DATA.op('TEST_END_TIME,0,' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ',N/A,N/A')
        # #OVERALL_TEST_RESULT
        # if DATA.totalfails==0:
        #     DATA.op('OVERALL_TEST_RESULT,0,PASS,N/A,N/A')
        # else:
        #     DATA.op('OVERALL_TEST_RESULT,1,FAIL,N/A,N/A')
        #TOTAL_TEST_TIME
        DATA.op('TOTAL_TEST_TIME,0,' + str(time.time()-DATA.start_time) + ',N/A,N/A')


    def get_pc_macaddress(self):
        import uuid
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


if __name__ == '__main__':
    bi=BasicInfo({})
    bi.wait({'seconds':'3.3'})
