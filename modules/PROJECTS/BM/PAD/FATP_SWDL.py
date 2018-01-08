import subprocess

class swdl:
    def dl(self):
        p = subprocess.Popen('', 0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             cwd='.', shell=False)
        while p.poll() == None:
            buf = p.stdout.readline()
            print buf
        print 'rtcode=',p.returncode