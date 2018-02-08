import serial,time

sysenv_keys = [
    'nlWeavePrivateKey',
    'gang_num',
    'nlWeaveCertificate',
    'WLED_bin',
    'RGB_bin',
    'als_ratio',
    'led_white.gang1',
    'led_white.gang2',
    'led_blue.gang1',
    'led_blue.gang2',
    'led_green.gang1',
    'led_green.gang2',
    'led_yellow.gang1',
    'led_yellow.gang2',
    'touch_fw'
]


def wr(com, cmd, end, has='', timeout=3):
    try:
        com.write(cmd)
        buf = ''
        t0 = time.time()
        while time.time() - t0 < timeout:
            buf += com.readall()
            if buf.endswith(end) and buf.find(has) >= 0:
                return True, buf
        return False, buf
    except Exception, e:
        return False, e

com = serial.Serial('COM11', 115200,timeout=0)

r,v = wr(com,'root\r','# ',has='root@')
print r,v
r,v = wr(com,'nlcli env\r','# ',has='root@')
print r,v
env_kv={}
print '=====\n\n'
for line in v.split('\n'):
    if line.find('=')>0:
        key,value = line.strip().split('=',1)
        env_kv[key]=value

r,v = wr(com,'nlcli pad -p\r','>')
print r,v

for name in sysenv_keys:
    try:
        cmd = 'sysenv set %s %s\r'%(name,env_kv[name])
        r, v = wr(com, cmd, '>')
        print r, v
    except Exception,e:
        print Exception,e

r, v = wr(com, 'sysenv', '>')
print r, v

r, v = wr(com, '%c'%3, '>')
print r, v