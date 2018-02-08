
script='scripts/BM_fix_led_bincode.script'
setting = 'setting/Setting.ini'

import re,json
import os,shutil
import py_compile
import datetime

timestr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
script_name = script.split('/')[1].split('.')[0]
setting_name = setting.split('/')[1].split('.')[0]
target='../release/'+script_name+'_'+timestr

try:
    os.mkdir(target)
except:
    pass
try:
    os.makedirs(target+'/'+'scripts')
    os.makedirs(target+'/'+'setting')
except:
    pass
targetscriptname = script_name+'_'+timestr+'.script'
targetsettingname = setting_name+'_'+timestr+'.ini'
shutil.copy(script,target+'/scripts/'+targetscriptname)
shutil.copy(setting,target+'/setting/'+targetsettingname)

necessary=['controller.py','data.py','reflex.py','script.py','singletoneBarrier.py','worker.py']
for f in necessary:
    py_compile.compile(f)
    shutil.copy(f+'c',target+'/'+f+'c')

allpy=[]
for root, dirs, files in os.walk('modules'):
    for f in files:
        if f.endswith('.py'):
            one=[root,root+'/'+f]
            allpy.append(one)
print allpy

for p in allpy:
    f=p[1]
    py_compile.compile(f)
    path=p[0]
    try:
        os.makedirs(target+'/'+path)
        print path
    except:
        pass
    shutil.copy(f+'c',target+'/'+f+'c')




