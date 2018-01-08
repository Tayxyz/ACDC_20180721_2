import requests
import time
from data import *
class provision():
    def __init__(self, argv):
        pass

    def GetMiddleStr(self,content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
            endIndex = content.index(endStr,startIndex)
            return content[startIndex:endIndex]
        else:
            return ''

    def GetWeaveProvisioningInfo(self,argv):
        if not DATA.STATION_ONLINE=='YES':
            DATA.op(argv['name'] + ',0,OFFLINE-SKIP,N/A,N/A')
            return
        try:

            DATA.lock_common('LOCK_SFIS')
            get_str = 'https://%s:8000/%s?macAddr=%s' % (DATA.provision_ip,'GetWeaveProvisioningInfo', DATA.MAC_6LOWPAN)
            requests.packages.urllib3.disable_warnings()
            r=requests.get(get_str,verify=False)
            info=r.text
            print info
            if "</dict>" in info:
                aaa = info.replace("\n", "")
                DATA.nlWeaveCertificate = self.GetMiddleStr(aaa, 'nlWeaveCertificate</key><string>', '</string><key>nlWeavePrivateKey')
                print "nlWeaveCertificate: %s" % DATA.nlWeaveCertificate

                DATA.nlWeavePrivateKey = self.GetMiddleStr(aaa, 'nlWeavePrivateKey</key><string>', '</string><key>nlWeavePairingCode')
                print "nlWeavePrivateKey: %s" % DATA.nlWeavePrivateKey

                DATA.nlWeavePairingCode = self.GetMiddleStr(aaa, 'nlWeavePairingCode</key><string>', '</string><key>nlWeaveProvisioningHash')
                print "nlWeavePairingCode: %s" % DATA.nlWeavePairingCode

                DATA.nlWeaveProvisioningHash = self.GetMiddleStr(aaa, 'nlWeaveProvisioningHash</key><string>', '</string></dict>')
                print "nlWeaveProvisioningHash: %s" % DATA.nlWeaveProvisioningHash

                if len(DATA.nlWeaveCertificate)>0 and len(DATA.nlWeavePrivateKey)>0 and len(DATA.nlWeavePairingCode)>0:
                    DATA.op(argv['name'] + ',0,PASS,N/A,N/A')
                    return

            print "get provision info fail"
            DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')
        except Exception,e:
            print Exception,e
            DATA.op(argv['name']+',1,FAIL,N/A,N/A')
        finally:
            DATA.unlock_common('LOCK_SFIS')

