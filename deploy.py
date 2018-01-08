
script='scripts/BM_FATP_PAD_SS_V2.script'
setting = 'setting/Setting_BM_FATP_PAD_SS.ini'

import re,json
import os,shutil
import py_compile

target='../release/'+script.split('/')[1].split('.')[0]

try:
    os.mkdir(target)
except:
    pass
try:
    os.makedirs(target+'/'+'scripts')
    os.makedirs(target+'/'+'setting')
except:
    pass

shutil.copy(script,target+'/'+script)
shutil.copy(setting,target+'/'+setting)

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




