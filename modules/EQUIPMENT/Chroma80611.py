#Noise Time
from data import *
import visa, time, os

class Chroma80611():
	def __init__(self, argv):
		try:
			self.rm = visa.ResourceManager()
			if not self._connect(argv['address']):
				return
		except Exception, e:
			logE(Exception, e)


	def _connect(self, address = None):
		if address is None:
			address = self.address
		try:
			self.inst = self.rm.open_resource(address)
			return True
		except Exception, e:
			logE(Exception, e)
			logE(address, 'not find')
			return False

	def get_info(self, argv):
		try:
			logV(self.inst.query('*IDN?'))
			rt = self.inst.query('*RST;*OPC?')
			if rt != '0\n':
				return False
			return True
			# 'NRMSR "2,2,2,2,2,2,2,2,2,2";*OPC?',
			# 'NMT "2,2,2,2,2,2,2,2,2,2";*OPC?',
			# 'NB "1,1,1,1,1,1,1,1,1,1";*OPC?',
			# 'VR "3,3,3,3,3,3,2,2,2,2";*OPC?'
			# 'TO "60.0,60.0,60.0,60.0,60.0,60.0,60.0,60.0,60.0,60.0";*OPC?',
			# 'NR "1,1,1,1,1,1,1,1,1,1";*OPC?',
			# 'DO1:SETALL 0,0,0,0;*OPC?',

		except Exception, e:
			logE(Exception, e)
			logE('get info fail: ', rt)
			return False

	def setVR(self, argv):
		cmd = 'VR "2,2,2,2,2,2,2,2,2,2";*OPC?'
		try:
			rt = self.inst.query(cmd)
			logV(cmd, '==>', rt)
			if rt != '0\n':
				logE('setVR fail:', rt)
				return False
		except Exception, e:
			logE(Exception, e)
			return False
		return True

	def setVPK(self, argv): # {'VPK': '1'}
		if not argv.has_key('VPK'):
			argv['VPK'] = '1'

		direct = 'VPK "'+'%s%s;*OPC?' % ((argv['VPK']+',')*6, '0,0,0,0"')
		try:
			rt = self.inst.query(direct)
			logV(direct, '==>', rt)
			if rt != '0\n':
				logE(r'setVPK fail. \'VPK\': ', argv['VPK'])
				return False
		except Exception, e:
			logE(Exception, e)
			return False
		return True

	def ReadVMPKValue(self, argv):
		cmds_items = ['VMPKH?', 'VMPKL?']
		reValues = {'VMPKH': '', 'VMPKL': ''}
		temp = []

		try:
			for cmd in cmds_items:
				rt_items = self.inst.query(cmd)
				logV(cmd, '==>', rt_items)
				if rt_items:
					temp.append(rt_items.split(',')[DATA.id-1])
				else:
					logE('read items VMPKH/VMPKL', 'fail')
					return ''
		except Exception, e:
			logE(Exception, e)
			return ''

		reValues['VMPKH'] = '{:.2f}'.format(float(temp[0]))
		reValues['VMPKL'] = '{:.2f}'.format(float(temp[1]))

		return reValues

	def setNosie(self, argv):
		if not argv.has_key('NRMSR'):
			argv['NRMSR'] = '3'
		if not argv.has_key('NMT'):
			argv['NMT'] = '2'
		if not argv.has_key('NR'):
			argv['NR'] = '2'

		cmds = ['NRMSR "'+'%s%s;*OPC?' % ((argv['NRMSR']+',')*6, '3,3,3,3"'),
		'NMT "'+'%s%s;*OPC?' % ((argv['NMT']+',')*6, '2,2,2,2"'),
		'NR "'+'%s%s;*OPC?' % ((argv['NR']+',')*6, '2,2,2,2"')]
		try:
			for cmd in cmds:
				rt = self.inst.query(cmd)
				logV(cmd, '==>', rt)
				if rt != '0\n':
					logE('setNosie', 'fail')
					return False
		except Exception, e:
			logE(Exception, e)
			return False
		return True

	def setNoiseVolt(self, argv):
		try:
			rt = self.inst.query('NOIS:CHAN 0;CONV;*OPC?')
			logV('NOIS:CHAN 0;CONV;*OPC?', '==>', rt)
			if rt != '0\n':
				logE('setNosieVolt fail:', rt)
				return False
		except Exception, e:
			logE(Exception, e)
			return False
		return True

	def ReadNoiseVolt(self, argv):
		try:
			rt = self.inst.query('NM?')
			logV('NM?', '==>', rt)
			if rt:
				return rt.split(',')[DATA.id-1] # '0.03830000'
		except Exception, e:
			logE(Exception, e)
			logE('send NM fail:', rt)
			return ''

	def close(self):
		cmds = [
		'SET:REL 0;*OPC?',
		'SET:TTLB 0;*OPC?',
		'DVM1:INP 0;*OPC?',
		'HF1:OUT1 0;*OPC?',
		'HF1:OUT2 0;*OPC?',
		'HF2:OUT1 0;*OPC?',
		'HF2:OUT2 0;*OPC?']

		try:
			for cmd in cmds:
				rt = self.inst.query(cmd)
				logV(cmd, '==>', rt)
				if rt != '0\n':
					logE('close80611 fail', rt)
		except Exception, e:
			logE(Exception, e)




if __name__ == '__main__':
	if os.path.exists('ee.txt'):
		os.remove('ee.txt')
	def logE(*args):
		v=' '.join([str(s) for s in args])
		with open('ee.txt','a') as fa:
			fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
			fa.write('[error] ')
			fa.write(v)

	def logV(*args):
		v=' '.join([str(s) for s in args])
		with open('ee.txt', 'a') as fa:
			fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
			fa.write('[verbose] ')
			fa.write(v)


	ins = Chroma80611({'address': 'GPIB0::8::0'})

	print ins.setNosie({'NRMSR': '3', 'NMT': '1', 'NR': '2'})

