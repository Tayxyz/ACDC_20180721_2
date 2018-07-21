#Power meter


import visa, time, os, re
from data import *

class Chroma66200():
	def __init__(self, argv):
		try:
			self.rm = visa.ResourceManager()
			if not self._connect(argv['address'][str(DATA.id)]):
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
		except Exception, e:
			logE(Exception, e)
			logE('get info fail:', rt)
			return False


	def setRange(self, argv): # {'SOUR:CURR:RANG': 'A04'}
		if not argv.has_key('SOUR:CURR:RANG'):
			argv['SOUR:CURR:RANG'] = 'A01'

		cmd = 'SOUR:CURR:RANG %s;*OPC?' %argv['SOUR:CURR:RANG']

		try:
			rt = self.inst.query(cmd)
			logV(cmd, '==>', repr(rt))
			if rt != '0\r\n':
				logE('setRange fail:', repr(rt))
		except Exception, e:
			logE(Exception, e)


	def ReadREALValue(self, argv):
		#A01: 0.1234 -----item's value
		#A04: 7.0802 -----power
		try:
			rt = self.inst.query('FETC:SCAL:POW:REAL?\n')
			logV(r'FETC:SCAL:POW:REAL?\n', '==>', repr(rt))
		except Exception, e:
			logE(Exception, e)
		result = re.findall(r'\d.*\d+', rt)
		if not result:
			logE('ReadREALValue fail:', result)
			return ''
		else:
			rt_value = '{:.3f}'.format(float(result[0]))
			return str(rt_value)


	def close(self):
		try:
			rt = self.inst.query('SOUR:PROT:CLE;*OPC?')
			logV(r'SOUR:PROT:CLE;*OPC?', '==>', repr(rt))
		except Exception, e:
			logE(Exception, e)
		if rt != '0\r\n':
			logE('close66200 fail:', repr(rt))


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

	ins = Chroma66200({'address': 'GPIB0::13::0'})
	print ins.setRange({'SOUR:CURR:RANG': 'A01'})
	print ins.ReadREALValue({})
	print ins.setRange({'SOUR:CURR:RANG': 'A04'})
	print ins.setRange({'SOUR:CURR:RANG': 'V300'})
	print ins.setRange({'SOUR:CURR:RANG': 'A2L'})
	print ins.setRange({'SOUR:CURR:RANG': 'AUTO'})
	print ins.ReadREALValue({})
	print ins.close({})
