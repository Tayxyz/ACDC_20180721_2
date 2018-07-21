#   ACSource

from data import *
import visa, time, os

class Chroma61600():
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
			rt = self.inst.query('*CLS;*OPC?')
			if rt != '1\r\n':
				return False
			return True
		except Exception, e:
			logE(Exception, e)
			logE('get info fail: ', rt)
			return False



	def setAC(self, argv): # VOLT:AC 0.0
		cmd = 'VOLT:AC %s;*OPC?' %argv['VOLT:AC']
		try:
			rt = self.inst.query(cmd)
			logV(cmd, '==>', rt)
		except Exception, e:
			logE(Exception, e)

		if rt != '1\r\n':
			logE('setAC fail:', rt)
			return False
		return True


	def setOUTP(self, argv): # OUTP:STAT OFF
		cmd = 'OUTP:STAT %s;*OPC?' %argv['OUTP:STAT']

		try:
			rt = self.inst.query(cmd)
			logV(cmd, '==>', rt)
		except Exception, e:
			logE(Exception, e)
		if rt != '1\r\n':
			logE('setOUTP fail:', rt)
			return False
		return True


	def config(self, argv):
		if not argv.has_key('VOLT:RANG'):
			argv['VOLT:RANG'] = 'LOW'
		if not argv.has_key('FREQ'):
			argv['FREQ'] = '60.0'
		if not argv.has_key('CURR:LIM'):
			argv['CURR:LIM'] = '2.0'

		cmds = ['VOLT:RANG %s;*OPC?' %argv['VOLT:RANG'],
		'FREQ %s;*OPC?' %argv['FREQ'],
		'CURR:LIM %s;*OPC?' %argv['CURR:LIM']]

		try:
			for cmd in cmds:
				rt = self.inst.query(cmd)
				logV(cmd,'==>',rt)
				if rt != '1\r\n':
					logE('initial 61600 fail:', rt)
					return False
		except Exception, e:
			logE(Exception, e)

		return True




if __name__ == '__main__':
	def logE(*args):
		v=' '.join([str(s) for s in args])
		with open('ee.txt', 'a') as fa:
			fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
			fa.write('[error] ')
			fa.write(v)

	def logV(*args):
		v=' '.join([str(s) for s in args])
		with open('ee.txt', 'a') as fa:
			fa.write('\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
			fa.write('[verbose] ')
			fa.write(v)

	if os.path.exists('ee.txt'):
		os.remove('ee.txt')
	ins = Chroma61600({'address': 'GPIB0::30::0'})
	print ins.config({'VOLT:RANG': 'LOW', 'FREQ': '60.0','CURR:LIM': '2.0', 'VOLT:AC': '120.0', 'OUTP:STAT':'ON'})
	print ins.close({'VOLT:AC': '0.0', 'OUTP:STAT':'OFF'})
	print ins.restart({'VOLT:AC': '120.0', 'OUTP:STAT':'ON'})
	print ins.close({})
