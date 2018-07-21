from data import *
import visa, time, os
import ADlink7320

class Chroma63102():
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
			cmds = ['*RST;*OPC?',
			'GO "0,0,0,0,0,0,0,0";*OPC?',
			'M "2,2,2,2,2,2,2,2";*OPC?',
			'VRB "1,1,1,1,1,1,1,1";*OPC?']
			for cmd in cmds:
				rt = self.inst.query(cmd)
				logV(cmd, '==>', repr(rt))
				if rt != '0\n':
					return False
			return True
		except Exception, e:
			logE(Exception, e)
			logE('get info fail: ', repr(rt))
			return False

	def setGO(self, argv): # {'GO': '1'}
		if not argv.has_key('GO'):
			argv['GO'] = '0'

		direct = 'GO "'+'%s%s;*OPC?' % ((argv['GO']+',')*6, '2,2"')
		try:
			rt = self.inst.query(direct)
			logV(direct, '==>', repr(rt))
			if rt != '0\n':
				logE('setGO fail:', repr(rt))
		except Exception, e:
			logE(Exception, e)


	def setCC(self, argv): # {'CC': '5.0000e-1'}
		if not argv.has_key('CC'):
			argv['CC'] = '1.0000e-1'

		direct = 'L "'+'%s%s' % ((argv['CC']+',')*6, '0.0000e+0,0.0000e+0"')
		logV(direct)
		try:
			self.inst.write(direct)
			time.sleep(0.1)
		except Exception, e:
			logE(Exception, e)
			logE('setCC fail:', direct)


	def setSRA(self, argv):
		try:
			rt = self.inst.query('SRA "1,1,1,1,1,1,0,0";*OPC?')
			logV('SRA "1,1,1,1,1,1,0,0";*OPC?', '==>', repr(rt))
			if rt != '0\n':
				logE('setSRA fail', repr(rt))
		except Exception, e:
			logE(Exception, e)


	def setM(self, argv): # {'M': '4'}
		if not argv.has_key('M'):
			argv['M'] = '2'

		direct = 'M "'+'%s%s;*OPC?' % ((argv['M']+',')*6, '0,0"')
		try:
			rt = self.inst.query(direct)
			logV(direct, '==>', repr(rt))
			if rt != '0\n':
				logE('setM fail:', repr(rt))
		except Exception, e:
			logE(Exception, e)


	def queryVolt(self, argv):
		try:
			rt = self.inst.query('MEAS:ALLV?')
			logV('MEAS:ALLV?', '==>', repr(rt))
		except Exception, e:
			logE(Exception, e)
		if rt:
			rt = rt.split(',')[DATA.id-1] # '11.9375'
			result = '{:.3f}'.format(float(rt))
			return str(result)
		else:
			logE('queryVolt fail:', repr(rt))
			return ''

	def queryCurr(self, argv):
		try:
			rt = self.inst.query('MEAS:ALLC?')
			logV('MEAS:ALLC?', '==>', repr(rt))
		except Exception, e:
			logE(Exception, e)
		if rt:
			return rt.split(',')[DATA.id-1]
		else:
			logE('queryCurr fail:', rt)
			return ''


	def set_load_dynamic(self, argv):
		cmds = ['CDL1 "1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,-1.0000e+0,-1.0000e+0"',
		'CDL2 "5.0000e-1,5.0000e-1,5.0000e-1,5.0000e-1,5.0000e-1,5.0000e-1,-1.0000e+0,-1.0000e+0"',
		'CDT1 "1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,-1.000000,-1.000000"',
		'CDT2 "1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,1.0000e-1,-1.000000,-1.000000"',
		'CCSR "1.0000e-2,1.0000e-2,1.0000e-2,1.0000e-2,1.0000e-2,1.0000e-2,-1.0000e+0,-1.0000e+0"']

		try:
			for cmd in cmds:
				self.inst.write(cmd)
				time.sleep(0.1)
				logV(cmd)
		except Exception, e:
			logE(Exception, e)
			logE('set_load_dynamic fail')



	def close(self):
		cmds = ['CHAN 1:CONF:TIM:STAT 0',
		'CHAN 2:CONF:TIM:STAT 0',
		'CHAN 3:CONF:TIM:STAT 0',
		'CHAN 4:CONF:TIM:STAT 0',
		'CHAN 5:CONF:TIM:STAT 0',
		'CHAN 6:CONF:TIM:STAT 0']
		try:
			for cmd in cmds:
				self.inst.write(cmd)
				time.sleep(0.1)
				logV(cmd)
		except Exception, e:
			logE(Exception, e)
			logE('close dcload fail')



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

	ins = Chroma63102({'address': 'GPIB0::7::0'})

