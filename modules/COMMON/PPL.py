import ConfigParser
import datetime

class PPL:
    def __init__(self,isn,setting_name,fixture_id,build_phase):
        self.isn=isn
        _data={}
        _data['TEST_DATE_TIME']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _data['FIXTURE_INDEX']=fixture_id
        _data['BUILD_PHASE']=build_phase

        self.loadFromSeeting(setting_name)
        self.getStationMAC()
        self.snParsing()
        #STATION_SW_VERSION
        #SCRIPT_VERSION
        #LIMITS_VERSION

        #SFIS_STATION_INPUT_CHECK
        #SFIS_UPLOAD_TEST_RESULT

        patten={
            'STATION_NAME':'^[A-Z0-9_]+$',
        }

        head=['TEST_DATE_TIME',
              'TEST_READ_ISN_MLB',
              'TEST_READ_ISN_FATP',
               'STATION_NAME',
               'BUILD_EVENT',
               'FIXTURE_ID',
               'FIXTURE_INDEX',
               'LINE_NUMBER',
               'STATION_MAC',
               'USER_ID',
               'REL_STATUS',
               'SFIS_LOGIN_DB',
               'SFIS_CHECK_ROUTE',
               'STATION_MODE',
               'BUILD_PHASE',
               'PRODUCT_CODE',
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
               'TEST_READ_MODEL',
               'TEST_READ_FACTORY_CONFIG_MLB',
               'TEST_READ_FACTORY_CONFIG_FATP',
               'STATION_SW_VERSION',
               'SCRIPT_VERSION',
               'LIMITS_VERSION',
               'TEST_READ_FW_VERSION']

        tail=['TEST_FAIL_ITEM_QTY',
                'TEST_FAILURES',
                'TEST_END_TIME',
                'SFIS_WRITE_RESULT',
                'SFIS_LOGOUT_DB',
                'OVERALL_TEST_RESULT',
                'TOTAL_TEST_TIME']

    def loadFromSeeting(self,setting_name):
        #
        cf = ConfigParser.ConfigParser()
        cf.read(setting_name)
        self._data['STATION_NAME'] = cf.get('basic_info', 'STATION_NAME')
        self._data['USER_ID'] = cf.get('basic_info', 'OPID')
        self._data['LINE_NUMBER'] = cf.get('basic_info', 'LINE_NUMBER')
        self._data['BUILD_EVENT'] = cf.get('basic_info', 'BUILD_EVENT')
        self._data['STATION_MODE'] = cf.get('basic_info', 'STATION_MODE')
        self._data['LINE_NUMBER'] = cf.get('basic_info', 'LINE_NUMBER')

    def getStationMAC(self):
        #STATION_MAC
        import uuid
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        self._data['STATION_MAC']=':'.join([mac[i:i+2] for i in range(0,11,2)])

    def snParsing(self):
        PRODUCT_VERSION_DESC={'A':'WHITE','B':'BLACK'}
        PRODUCT_CODE_DESC={}
        PRODUCT_NAME_DESC={}
        PRODUCT_TYPE_DESC={}

        self._data['PRODUCT_REVISION']=self.isn[4:6]
        self._data['MFG_LOCATION'] = self.isn[6:8]
        self._data['MFG_LOCATION_DESC'] = 'PEGATRON_MAINTEK_SUZHOU'
        self._data['PRODUCT_CODE'] = self.isn[0:3]

        self._data['MFG_WW'] = self.isn[8:10]
        self._data['MFG_YEAR'] = self.isn[10:12]
        self._data['PRODUCT_NAME'] = self.isn[0:2]
        self._data['PRODUCT_TYPE'] = self.isn[2:3]
        self._data['PRODUCT_VERSION'] = self.isn[3:4]
        try:
            self._data['PRODUCT_TYPE_DESC'] = PRODUCT_TYPE_DESC[self._data['PRODUCT_TYPE']]
        except:
            self._data['PRODUCT_TYPE_DESC'] = 'NOT_DEFINED'
        try:
            self._data['PRODUCT_NAME_DESC'] = PRODUCT_NAME_DESC[self._data['PRODUCT_NAME']]
        except:
            self._data['PRODUCT_NAME_DESC'] = 'NOT_DEFINED'
        try:
            self._data['PRODUCT_CODE_DESC'] = PRODUCT_CODE_DESC[self._data['PRODUCT_CODE']]
        except:
            self._data['PRODUCT_CODE_DESC'] = 'NOT_DEFINED'
        try:
            self._data['PRODUCT_VERSION_DESC'] = PRODUCT_VERSION_DESC[self._data['PRODUCT_VERSION']]
        except:
            self._data['PRODUCT_VERSION_DESC'] = 'NOT_DEFINED'

    def settail(self):
        #TEST_END_TIME,TOTAL_TEST_TIME,OVERALL_TEST_RESULT,TEST_FAILURES,TEST_FAIL_ITEM_QTY,SPC_RUN_ID,SPC_ITERATION,REL_STATUS
        pass

    def get(self,key):
        try:
            return self._data[key]
        except:
            return None