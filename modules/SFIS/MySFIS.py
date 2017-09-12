#!/usr/bin/env python
# coding:utf-8
import suds


class SFISWebService(object):
    """
	SFIS using suds
	member function return:[iStatus,szMessage]
	"""

    def __init__(self, urls, device, TSP, checkRouteType='1',
                 testResultType='1', autoRepairType='1'):
        super(SFISWebService, self).__init__()
        self.__programId = 'TSP_ATSHH'
        self.__programPassword = 'pap_ahga'
        self.__urls = urls + '?wsdl'
        self.__TSP = TSP
        self.__checkRouteType = checkRouteType
        self.__testResultType = testResultType
        self.__autoRepairType = autoRepairType
        self.__client = None
        self.__device = device

    def SFIS_Connect(self):
        try:
            self.__client = suds.client.Client(self.__urls)
            info = self.__client.service.GetDatabaseInformation()
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127))[1]
        # else:
        #	raise Exception(info.split(chr(127))[1])
        except Exception as e:
            print Exception,e
            return '0',str(e)

    def SFIS_Login(self, userId, loginMode, password=''):
        try:
            info = self.__client.service.WTSP_LOGINOUT(op=userId,
                                                       password=password, status=loginMode, programId=self.__programId,
                                                       programPassword=self.__programPassword, TSP=self.__TSP,
                                                       device=self.__device)
            if int(info.split(chr(127))[0]):
                self.__userId = userId
            return info.split(chr(127), 1)
		# return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_CheckRoute(self, isn, checkFlag='', checkData=''):
        try:
            info = self.__client.service.WTSP_CHKROUTE(programId=self.__programId,
                                                       programPassword=self.__programPassword, ISN=isn,
                                                       device=self.__device,
                                                       checkFlag=checkFlag, checkData=checkData,
                                                       type=self.__checkRouteType)
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_GetIMAC(self, isn, getVersionType=1):
        try:
            info = self.__client.service.WTSP_GETIMAC(programId=self.__programId,
                                                      programPassword=self.__programPassword, device=self.__device,
                                                      ISN=isn, status=1, imacnum=int(getVersionType))
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_GetVersion(self, isn, getVersionType='1', checkData='', checkData2=''):
        try:
            info = self.__client.service.WTSP_GETVERSION(programId=self.__programId,
                                                         programPassword=self.__programPassword, ISN=isn,
                                                         device=self.__device,
                                                         type=getVersionType, ChkData=checkData, ChkData2=checkData2)
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_TestResult(self, isn, errorcode='', logStreamData='', ):
        try:
            info = self.__client.service.WTSP_RESULT(programId=self.__programId,
                                                     programPassword=self.__programPassword, ISN=isn, error=errorcode,
                                                     device=self.__device, TSP=self.__TSP, data=logStreamData,
                                                     status=int(self.__testResultType), CPKFlag='')
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_Repair(self, isn):
        try:
            info = self.__client.service.WTSP_REPAIR(programId=self.__programId,
                                                     programPassword=self.__programPassword, TYPE=self.__autoRepairType,
                                                     ISN=isn, DEV=self.__device, REASON='ZR', DUTY='7C0', NGRP='AUTO2A',
                                                     TSP=self.__TSP)
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_GetI1394(self, isn, getVersionType=1):
        try:
            info = self.__client.service.WTSP_GETI1394(programId=self.__programId,
                                                       programPassword=self.__programPassword, ISN=isn,
                                                       device=self.__device,
                                                       status=int(getVersionType), I1394NUM=int(getVersionType))
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)

    def SFIS_LoadKey(self, loadKeyType='', logStreamData=''):
        try:
            info = self.__client.service.WTSP_LOADKEY(programId=self.__programId,
                                                      programPassword=self.__programPassword, SNTYPE=loadKeyType,
                                                      DATA=logStreamData, OP=self.__userId)
            return info.split(chr(127), 1)
        # if int(info.split(chr(127))[0]):
        #	return info.split(chr(127),1)[1]
        # else:
        #	raise Exception(info.split(chr(127),1)[1])
        except Exception as e:
            print Exception,e
            return '0', str(e)
