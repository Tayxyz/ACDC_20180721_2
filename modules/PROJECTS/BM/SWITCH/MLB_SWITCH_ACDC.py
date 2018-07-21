from data import *
from IO.rs232 import RS232
import ConfigParser, re

class ACDC():
	def __init__(self, argv):
		self.DUTCOM = argv['COM'][str(DATA.id)]
		self.DUT = RS232({'COM': self.DUTCOM})
		self.DUT._connect()


	def set_relay(self, argv):
		try:
			barrier = DATA.barriers[argv['barrier']]
		except:
			barrier = None

		relay1 = DATA.objs['RELAY1']
		relay2 = DATA.objs['RELAY2']
		if argv['mode'] == 'off':
			v1 = 0
			v2 = 0
		elif argv['mode'] == 'cn':
			v1 = 0b0001000100010001
			v2 = 0b0001000100111111
		elif argv['mode'] == 't1n':
			v1 = 0b0010001000100010
			v2 = 0b0010001000111111
		elif argv['mode'] == 't2n':
			v1 = 0b0100010001000100
			v2 = 0b0100010000111111
		elif argv['mode'] == 'ctn':
			v1 = 0b1001100110011001
			v2 = 0b1001100100000000

		try:
			if barrier:
				if barrier.acquire():
					logV('barrier do set relay')
					relay1.write_relay(v1)
					relay2.write_relay(v2)
					relay1.query_relay()
					relay2.query_relay()
				else:
					logV('barrier bypass')
		except Exception, e:
			logE(Exception, e)
		finally:
			if barrier:
				barrier.release()


	def test_pad_detect_state(self, argv):
		try:
			rt, buffer = self.DUT.wr('\r', '\r\n# ')
			logV(rt, repr(buffer))
			logV('---------------------------')
			time.sleep(2)
			if not rt:
				logE('test_pad_detect_state: send \'\r\' fail')

			rt, buffer = self.DUT.wr('pad detect\r', '# ', has='Detect:')
			logV(rt, repr(buffer))

			if rt:
				result = re.findall(r'\: +(\d+)\n\r#', buffer)
				DATA.op(argv['name']+',0,'+result[0]+',N/A,N/A')
			else:
				DATA.op(argv['name']+',1,FAIL,N/A,N/A')

		except Exception, e:
			logE(Exception, e)
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')


	def test_12v_read_dc(self, argv):
		time.sleep(2)
		#DUT
		try:
			rt, buffer = self.DUT.wr('voltread\r', '# ')
			logV(rt, repr(buffer))

			if rt:
				result = re.findall(r'\r\n+([0-9a-zA-Z]+[\S])', buffer)
				result = '{:.3f}'.format(int(result[0], 16)/226.0)
				DATA.op(argv['name'] + ',0,' + str(result) + ',N/A,N/A')
			else:
				DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')

		except Exception, e:
			logE(Exception, e)
			DATA.op(argv['name'] + ',1,FAIL,N/A,N/A')


	def test_load_regulation_120v_0ma_cn(self, argv):
		if not self.switch_hpmode():
			logE('test_load_regulation_120v_0ma_cn', 'switch_hpmode fail')


		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]
		dcload = DATA.objs['DCLOAD']

		try:
			if barrier.acquire():
				logV('barrier get, do set DCLOAD')
				dcload.setCC({'CC':'1.0000e-1'})
				dcload.setSRA({})
				dcload.setGO({'GO':'1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('set DCLOAD Fail')
			return
		finally:
			barrier.release()

		#wait...
		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		logV(repr(rt))
		if rt:
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')


	def test_load_regulation_120v_500ma_cn(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]
		dcload = DATA.objs['DCLOAD']

		try:
			if barrier.acquire():
				logV('barrier get, set CC')
				dcload.setCC({'CC':'5.0000e-1'})
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_cn setCC: 5.0000e-1 fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		logV(repr(rt))
		if rt:
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')

		try:
			if barrier.acquire():
				logV('barrier get, set GO')
				dcload.setGO({'GO': '0'})
				time.sleep(1)
				dcload.set_load_dynamic({})
				dcload.setM({'M': '4'})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_cn  set DCLOAD fail')
			return
		finally:
			barrier.release()


	def test_dynamic_load_120v_cn(self, argv):
		barrier	= DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		emu = DATA.objs['EMU8']
		try:
			if barrier.acquire():
				logV('barrier get, set VPK')
				emu.setVR({})#
				emu.setVPK({'VPK': '1'})
			else:
				logV('barrier bypass')
		except:
			logE('test_dynamic_load_120v_cn set EMU Fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt = emu.ReadVMPKValue({})
		logV(repr(rt))
		if rt:
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_C_N,0,' + rt['VMPKH'] + ',N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_C_N,0,' + rt['VMPKL'] + ',N/A,N/A')
		else:
			logE('test_dynamic_120v_cn ReadVMPKValue fail')
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_C_N,1,FAIL,N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_C_N,1,FAIL,N/A,N/A')

		try:
			if barrier.acquire():
				logV('barrier get, set VPK')
				emu.setVPK({'VPK': '0'})
			else:
				logV('barrier bypass')
		except:
			logE('test_dynamic_load_120v_cn', 'setVPK fail')
			return
		finally:
			barrier.release()


	def test_noload_power_120v_0ma_cn(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]
		dcload = DATA.objs['DCLOAD']

		try:
			if barrier.acquire():
				logV('barrier get, set DCLOAD')
				dcload.setM({'M': '2'})
				dcload.setCC({'CC': '1.0000e-1'})
				dcload.setSRA({})
				dcload.setGO({'GO': '0'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('test_noload_power_120v_0ma_cn', 'set DCLOAD fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		pm = DATA.objs['PM']
		with lock:
			pm.setRange({'SOUR:CURR:RANG': 'A01'})

		#waiting...
		time.sleep(2)
		with lock:
			rt = pm.ReadREALValue({})
		logV(repr(rt))
		if rt:
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')


	def test_efficiency_120v_500ma_cn(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		pm = DATA.objs['PM']
		with lock:
			pm.setRange({'SOUR:CURR:RANG': 'A04'})

		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, set GO')
				dcload.setCC({'CC': '5.0000e-1'})
				dcload.setSRA({})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('set DCLOAD Fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt_V = float(dcload.queryVolt({}))
		if not rt_V:
			logE('test_efficiency_120v_500ma_cn queryVolt fail')
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			return

		time.sleep(1)
		with lock:
			rt_C = float(dcload.queryCurr({}))
		if not rt_C:
			logE('test_efficiency_120v_500ma_cn', 'queryCurr fail')
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			return

		time.sleep(1)
		with lock:
			rt_P = float(pm.ReadREALValue({}))
		if not rt_P:
			logE('test_efficiency_120v_500ma_cn', 'ReadREALValue fail')
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			return

		result = rt_V*rt_C/rt_P
		form = format(result*100, '.2f')
		DATA.op(argv['name']+',0,'+ str(form) +',N/A,N/A')


	def test_ripple_120v_0ma_cn(self, argv):
		barrierload = DATA.barriers[argv['barrierload']]
		barrieremu = DATA.barriers[argv['barrieremu']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']

		try:
			if barrierload.acquire():
				logV('barrierload get, set CC')
				dcload.setCC({'CC': '1.0000e-1'})
				dcload.setSRA({})
			else:
				logV('barrierload bypass')
		except:
			logE('test_ripple_120v_0ma_cn  setCC fail')
			return
		finally:
			barrierload.release()

		time.sleep(1)
		emu = DATA.objs['EMU8']
		try:
			if barrieremu.acquire():
				logV('barrieremu get, set Nosie')
				emu.setNosie({'NRMSR': '3', 'NMT': '1', 'NR': '2'})
				emu.setNoiseVolt({})
			else:
				logV('barrieremu bypass')
		except:
			logE('test_ripple_120v_0ma_cn setNosie fail')
			return
		finally:
			barrieremu.release()


		time.sleep(1)
		flag = 0
		for i in range(10):
			with lock:
				rt = emu.ReadNoiseVolt({})
			if float(rt) > 0:
				flag = 1
				result = float(rt)*1000
				break
			time.sleep(1)

		if flag:
			DATA.op(argv['name']+',0,'+ str(result) +',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')


	def test_ripple_120v_500ma_cn(self, argv):
		barrierload = DATA.barriers[argv['barrierload']]
		barrieremu = DATA.barriers[argv['barrieremu']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']

		try:
			if barrierload.acquire():
				logV('barrierload get, set CC')
				dcload.setCC({'CC': '5.0000e-1'})
				dcload.setSRA({})
			else:
				logV('barrierload bypass')
		except:
			logE('test_ripple_120v_500ma_cn setCC fail')
			return
		finally:
			barrierload.release()

		time.sleep(1)
		emu = DATA.objs['EMU8']

		try:
			if barrieremu.acquire():
				logV('barrieremu get, set NosieVolt')
				emu.setNoiseVolt({})
			else:
				logV('barrieremu bypass')
		except:
			logE('test_ripple_120v_500ma_cn setNosieVolt fail')
			return
		finally:
			barrieremu.release()

		flag = 0
		for i in range(10):
			time.sleep(1)
			with lock:
				rt = emu.ReadNoiseVolt({})
			if float(rt) > 0:
				flag = 1
				result = float(rt)*1000
				break
		if flag:
			DATA.op(argv['name']+',0,'+ str(result) +',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')


	def test_ocp_120v_cn(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, set SRA')
				dcload.setSRA({})
			else:
				logV('barrier bypass')
		except:
			logE('test_ocp_120v_cn setSRA fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		if not rt:
			logE('test_ocp_120v_cn queryVolt fail')
		elif float(rt) < 11.0:
			logE('Voltage is already below the set value .')
			# return


		ini_curr = 4.0000e-1
		set_volt = 11.0
		bcatch = False
		catch_cur = 0

		for i in range(25):
			try:
				if barrier.acquire():
					logV('barrier get, set CC')
					dcload.setCC({'CC': str(ini_curr)})
				else:
					logV('barrier bypass')
			except:
				logE('test_ocp_120v_cn setCC fail')
				#return
			finally:
				barrier.release()


			with lock:
				time.sleep(0.1)
				rt = dcload.queryVolt({})
			if rt:
				if (float(rt) < set_volt) and (not bcatch):
					bcatch = True
					catch_cur = ini_curr
			ini_curr += 0.2000e-1

		if not bcatch:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			logE('test_ocp_120v_cn queryVolt fail')
		else:
			logV('max current: ', str(catch_cur))
			DATA.op(argv['name']+',0,'+ str(catch_cur) +',N/A,N/A')


		try:
			if barrier.acquire():
				logV('barrier get, set CC')
				dcload.setCC({'CC': '2.0000e-1'})
				dcload.setSRA({})
			else:
				logV('barrier bypass')
		except:
			logE('test_ocp_120v_cn setCC: 2.0000e-1 fail')
			#return
		finally:
			barrier.release()

		class VOLT_ending(Exception): pass
		j = 0
		try:
			for i in range(30):
				with lock:
					rt = dcload.queryVolt({})
				if rt:
					if float(rt) > 12.0:
						j += 1
						if j >= 10:
							raise VOLT_ending
				time.sleep(1)
		except VOLT_ending:
			logV('Voltage has already bigger than 12.0V')
		else:
			logE('Voltage isn\'t bigger than 12.0V')


	def test_load_regulation_120v_0ma_t1n(self, argv):
		rt, buffer = self.DUT.wr('\r', '\r\n# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'\r\' fail')

		if not self.switch_hpmode():
			logE('test_load_regulation_120v_0ma_t1n', 'switch_hpmode fail')

		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, do set DCLOAD')
				dcload.setCC({'CC': '1.0000e-1'})
				dcload.setSRA({})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('set DCLOAD Fail')
			return
		finally:
			barrier.release()

		#3. wait
		time.sleep(2)

		with lock:
			rt = dcload.queryVolt({})
		logV(repr(rt))
		if rt:
			logV('test_load_regulation_120v_0ma_t1n: VOLT: ', rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			logE('test_load_regulation_120v_0ma_t1n', 'queryVolt fail')


	def test_load_regulation_120v_500ma_t1n(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]
		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, set CC')
				dcload.setCC({'CC': '5.0000e-1'})
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_t1n setCC: 5.0000e-1 fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		logV(repr(rt))
		if rt:
			logV('test_load_regulation_120v_500ma_t1n: VOLT: ', rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			logE('test_load_regulation_120v_500ma_t1n', 'queryVolt fail')
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')

		try:
			if barrier.acquire():
				logV('barrier get, set GO')
				dcload.setGO({'GO': '0'})
				time.sleep(1)
				dcload.set_load_dynamic({})
				dcload.setM({'M': '4'})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_t1n  set DCLOAD fail')
		finally:
			barrier.release()


	def test_dynamic_load_120v_t1n(self, argv):
		barrieremu = DATA.barriers[argv['barrieremu']]
		barrierload = DATA.barriers[argv['barrierload']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		emu = DATA.objs['EMU8']
		try:
			if barrieremu.acquire():
				logV('barrier get, setVPK')
				emu.setVPK({'VPK': '1'})
			else:
				logV('barrier bypass')
		except:
			logE('test_dynamic_load_120v_t1n', 'setVPK Fail')
			return
		finally:
			barrieremu.release()

		time.sleep(2)
		with lock:
			rt = emu.ReadVMPKValue({})
		logV(repr(rt))
		if rt:
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_T1_N,0,' + rt['VMPKH'] + ',N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_T1_N,0,' + rt['VMPKL'] + ',N/A,N/A')
		else:
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_T1_N,1,FAIL,N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_T1_N,1,FAIL,N/A,N/A')

		try:
			if barrieremu.acquire():
				logV('barrier get, set VPK')
				emu.setVPK({'VPK': '0'})
			else:
				logV('barrier bypass')
		except:
			logE('test_dynamic_load_120v_t1n', 'setVPK fail')
			return
		finally:
			barrieremu.release()

		try:
			if barrierload.acquire():
				logV('barrier get, setM')
				dcload.setM({'M': '2'})
			else:
				logV('barrier bypass')
		except:
			logE('test_dynamic_load_120v_t1n', 'setM fail')
			return
		finally:
			barrierload.release()


	def test_load_regulation_120v_0ma_t2n(self, argv):
		rt, buffer = self.DUT.wr('\r', '\r\n# ')
		logV(rt, repr(buffer))
		if not rt:
			logE(r'send \'\r\' fail')

		if not self.switch_hpmode():
			logE('test_load_regulation_120v_0ma_t2n', 'switch_hpmode fail')


		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, do set DCLOAD')
				dcload.setCC({'CC': '1.0000e-1'})
				dcload.setSRA({})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('set DCLOAD Fail')
			return
		finally:
			barrier.release()

		#3. wait
		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		if rt:
			logV('test_load_regulation_120v_0ma_t2n: VOLT: ',rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			logE('test_load_regulation_120v_0ma_t2n', 'queryVolt fail')


	def test_load_regulation_120v_500ma_t2n(self, argv):
		barrier = DATA.barriers[argv['barrier']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		try:
			if barrier.acquire():
				logV('barrier get, set CC')
				dcload.setCC({'CC': '5.0000e-1'})
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_t2n setCC: 5.0000e-1 fail')
			return
		finally:
			barrier.release()

		time.sleep(2)
		with lock:
			rt = dcload.queryVolt({})
		if rt:
			logV('test_load_regulation_120v_500ma_t2n: VOLT: ', rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			logE('test_load_regulation_120v_500ma_t2n', 'queryVolt fail')
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')

		try:
			if barrier.acquire():
				logV('barrier get, set GO')
				dcload.setGO({'GO': '0'})
				time.sleep(1)
				dcload.set_load_dynamic({})
				dcload.setM({'M': '4'})
				dcload.setGO({'GO': '1'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('test_load_regulation_120v_500ma_t2n set DCLOAD fail')
		finally:
			barrier.release()


	def test_dynamic_load_120v_t2n(self, argv):
		barrieremu = DATA.barriers[argv['barrieremu']]
		barrierload = DATA.barriers[argv['barrierload']]
		lock = DATA.locks[argv['lock']]

		dcload = DATA.objs['DCLOAD']
		emu = DATA.objs['EMU8']
		try:
			if barrieremu.acquire():
				logV('barrier get, setVPK')
				emu.setVPK({'VPK': '1'})
			else:
				logV('barrieremu bypass')
		except:
			logE('test_dynamic_load_120v_t2n setVPK fail')
			return
		finally:
			barrieremu.release()


		time.sleep(2)
		with lock:
			rt = emu.ReadVMPKValue({})
		logV(repr(rt))
		if rt:
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_T2_N,0,' + rt['VMPKH'] + ',N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_T2_N,0,' + rt['VMPKL'] + ',N/A,N/A')
		else:
			logE('test_dynamicc_load_120v_t2n', 'ReadVMPKValue fail')
			DATA.op('TEST_DYNAMIC_LOAD_120V_0MA_VPH_T2_N,1,FAIL,N/A,N/A')
			DATA.op('TEST_DYNAMIC_LOAD_120V_500MA_VPL_T2_N,1,FAIL,N/A,N/A')

		try:
			if barrieremu.acquire():
				logV('barrier get, setVPK')
				emu.setVPK({'VPK': '0'})
			else:
				logV('barrieremu bypass')
		except:
			logE('test_dynamic_load_120v_t2n setVPK fail')
			return
		finally:
			barrieremu.release()

		try:
			if barrierload.acquire():
				logV('barrier get, setM')
				dcload.setM({'M': '2'})
			else:
				logV('barrierload bypass')
		except:
			logE('test_dynamic_load_120v_t2n setM fail')
			return
		finally:
			barrierload.release()


	def test_acpower_relay_setdimmer_50(self, argv):
		lock = DATA.locks[argv['lock']]

		time.sleep(1)
		rt, buffer = self.DUT.wr('\r', '\r\n# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'\r\' fail')

		logV('----------------------------')
		time.sleep(1)
		rt, buffer = self.DUT.wr('triac 50\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'triac 50\r\' fail')

		time.sleep(1)
		rt, buffer = self.DUT.wr('relay dir2\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'relay dir2\r\' fail')

		pm = DATA.objs['PM']
		with lock:
			pm.setRange({'SOUR:CURR:RANG': 'V300'})
			pm.setRange({'SOUR:CURR:RANG': 'A2L'})

		time.sleep(2)
		with lock:
			rt = pm.ReadREALValue({})
		if rt:
			logV('test_acpower_relay_setdimmer_50: REALValue : ', rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			logE('test_acpower_relay_setdimmer_50', 'ReadREALValue fail')


	def test_3way_state_relay_setdimmer_50(self, argv):
		time.sleep(1)
		try:
			rt, buffer = self.DUT.wr('ac 3way\r', '# ')
			logV(rt, repr(buffer))
			L = []
			if (not rt) or (not buffer):
				logE(r'send \'ac 3way\r\' fail')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_C,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_T1,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_T2,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_C,0,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_T1,0,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_T2,0,1,FAIL,N/A,N/A')
			else:
				t = re.findall(r'\: +(\d+ \d+)\n\r', buffer)
				for tt in t:
					L.append(re.findall(r'\S+', tt))
				logV('test_3way_state_relay_setdimmer_50: Result: ', L)
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_C,0,'+ L[0][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_T1,0,'+ L[1][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_FIRST_T2,0,'+ L[2][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_C,0,'+ L[0][1] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_T1,0,'+ L[1][1] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_SET_DIMMER_50_SECOND_T2,0,'+ L[2][1] +',N/A,N/A')
		except Exception, e:
			logE(Exception, e)
			logE('test_3way_state_relay_setdimmer_50 fail')


	def test_acpower_relay_resetdimmer_50(self, argv):
		lock = DATA.locks[argv['lock']]

		time.sleep(1)
		rt, buffer = self.DUT.wr('relay dir1\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE(r'send \'relay dir1\r\' fail')

		pm = DATA.objs['PM']
		with lock:
			pm.setRange({'SOUR:CURR:RANG': 'AUTO'})

		time.sleep(2)
		with lock:
			rt = pm.ReadREALValue({})
		if rt:
			logV('test_acpower_relay_resetdimmer_50: REALValue : ', rt)
			DATA.op(argv['name']+',0,'+rt+',N/A,N/A')
		else:
			DATA.op(argv['name']+',1,FAIL,N/A,N/A')
			logE('test_acpower_relay_resetdimmer_50', 'ReadREALValue fail')


	def test_3way_state_relay_resetdimmer_50(self, argv):
		time.sleep(1)
		try:
			rt, buffer = self.DUT.wr('ac 3way\r', '# ')
			logV(rt, repr(buffer))
			L = []
			if (not rt) or (not buffer):
				logE(r'send \'ac 3way\r\' fail')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_C,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_T1,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_T2,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_C,0,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_T1,0,1,FAIL,N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_T2,0,1,FAIL,N/A,N/A')

			else:
				t = re.findall(r'\: +(\d+ \d+)\n\r', buffer)
				for tt in t:
					L.append(re.findall(r'\S+', tt))
				logV('test_3way_state_relay_resetdimmer_50: Result: ', L)
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_C,0,'+ L[0][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_T1,0,'+ L[1][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_FIRST_T2,0,'+ L[2][0] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_C,0,'+ L[0][1] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_T1,0,'+ L[1][1] +',N/A,N/A')
				DATA.op('TEST_3WAY_STATE_RELAY_RESET_DIMMER_50_SECOND_T2,0,'+ L[2][1] +',N/A,N/A')
		except Exception, e:
			logE(Exception, e)
			logE('test_3way_state_relay_resetdimmer_50 fail')


	def test_dimmer0(self, argv):
		time.sleep(1)
		rt, buffer = self.DUT.wr('triac 0\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'triac 0\r\' fail')
			DATA.op(argv['name']+',1,0,N/A,N/A')
		else:
			DATA.op(argv['name']+',0,1,N/A,N/A')


	def test_neutral_det(self, argv):
		time.sleep(1)
		rt, buffer = self.DUT.wr('ac neutral\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'ac neutral\r\' fail')
			DATA.op(argv['name']+',1,0,N/A,N/A')
		else:
			DATA.op(argv['name']+',0,1,N/A,N/A')


	def test_acdc_disable(self, argv):
		time.sleep(1)
		rt, buffer = self.DUT.wr('acdc 1\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'acdc l\r\' fail')

		time.sleep(1)
		rt, buffer = self.DUT.wr('voltread\r', '# ')
		logV(rt, repr(buffer))
		if not rt:
			logE('send \'voltread\r\' fail')
			DATA.op(argv['name']+',1,0,N/A,N/A')
		else:
			DATA.op(argv['name']+',0,1,N/A,N/A')



	def closeDevice(self, argv):
		barrieremu = DATA.barriers[argv['barrieremu']]
		barrierload = DATA.barriers[argv['barrierload']]
		lock = DATA.locks[argv['lock']]

		emu = DATA.objs['EMU8']
		try:
			if barrieremu.acquire():
				logV('get barrier close emu')
				emu.close()
			else:
				logV('barrier bypass')
		finally:
			barrieremu.release()

		dcload = DATA.objs['DCLOAD']
		try:
			if barrierload.acquire():
				logV('get barrier close dcload')
				dcload.close()
			else:
				logV('barrier bypass')
		finally:
			barrierload.release()
                logV('-------------------------')
		pm = DATA.objs['PM']
		with lock:
			pm.close()



	def switch_hpmode(self):
		try:
			time.sleep(1)
			rt, buffer = self.DUT.wr('pad switch 1\r', '# ')
			logV(rt, repr(buffer))
			if not rt:
				logE('send \'pad switch 1\r\' fail')
				return False

			time.sleep(1)
			rt, buffer = self.DUT.wr('hpmode on\r', '# ')
			logV(rt, repr(buffer))
			if not rt:
				logE('send \'hpmode on\r\' fail')
				return False

		except Exception, e:
			logE(Exception, e)

		return True


	def acoff(self, argv):
		acsource = DATA.objs['ACSOURCE']

		barrier = DATA.barriers[argv['barrier']]
		try:
			if barrier.acquire():
				logV('barrier get, do set acsource')
				acsource.setAC({'VOLT:AC': '0.0'})
				acsource.setOUTP({'OUTP:STAT': 'OFF'})
			else:
				logV('barrier bypass')
		except:
			logE('acoff fail')
			return
		finally:
			barrier.release()


	def acon(self, argv):
		acsource = DATA.objs['ACSOURCE']
		try:
			config = argv['config']
		except:
			config = 'NO'

		barrier = DATA.barriers[argv['barrier']]
		try:
			if barrier.acquire():
				logV('barrier get, do set acsource')
				if config == 'YES':
					acsource.config({'VOLT:RANG': 'LOW', 'FREQ': '60.0', 'CURR:LIM': '2.0'})
				acsource.setAC({'VOLT:AC': '120.0'})
				acsource.setOUTP({'OUTP:STAT': 'ON'})
			else:
				logV('barrier bypass')
		except:
			logE('Set ACSource Fail')
			return
		finally:
			barrier.release()


	def closedcload(self, argv):
		dcload = DATA.objs['DCLOAD']
		barrier = DATA.barriers[argv['barrier']]
		try:
			if barrier.acquire():
				logV('get barrier, set DCLOAD')
				dcload.setCC({'CC': '2.0000e+0'})
				dcload.setSRA({})
				dcload.setGO({'GO':'0'})
				time.sleep(1)
			else:
				logV('barrier bypass')
		except:
			logE('close dcload fail')
			return
		finally:
			barrier.release()
