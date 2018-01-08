# -*- coding:utf-8 -*-
import Tkinter as tk
import time,threading
class dialog():
    def __init__(self,argv):
        pass


    def info(self,argv):
        try:
            msg=argv['msg']
        except:
            msg='Example'
        rt = tk.Tk()
        rt.withdraw()
        rt.attributes("-alpha", 0.5)
        l = tk.Label(rt, text=msg,font=('Times', '35', 'bold italic'),foreground='#ff00dd',background='#ffff09')
        b = tk.Button(rt,text='OK',font=('Times', '30', 'bold italic'),foreground='#fff0dd',background='#999999',command=rt.quit)
        l.pack()
        b.pack()

        #rt.overrideredirect(True)
        rt.iconbitmap('c:/Python27/DLLs/py.ico')
        rt.resizable(False, False)
        rt.title("Info")
        rt.update()  # update window ,must do
        curWidth = rt.winfo_reqwidth()  # get current width
        curHeight = rt.winfo_height()  # get current height
        scnWidth, scnHeight = rt.maxsize()  # get screen width and height
        # now generate configuration information
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                                  (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        rt.geometry(tmpcnf)
        rt.deiconify()
        rt.mainloop()
        try:
            rt.destroy()
        except:
            pass

    def count(self,argv):
        try:
            n=int(argv['n'])
        except:
            n=3
        rt = tk.Tk()
        rt.overrideredirect(True)
        rt.withdraw()
        text = tk.StringVar()
        text.set(n)
        l = tk.Label(rt, textvariable=text,font=('Times', '200', 'bold italic'),foreground='#ff00dd',background='#ffff09')
        l.pack()

        rt.iconbitmap('c:/Python27/DLLs/py.ico')
        rt.resizable(False, False)
        rt.title("Info")
        rt.update()  # update window ,must do
        curWidth = rt.winfo_reqwidth()  # get current width
        curHeight = rt.winfo_height()  # get current height
        scnWidth, scnHeight = rt.maxsize()  # get screen width and height
        # now generate configuration information
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                                  (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        rt.geometry(tmpcnf)
        rt.deiconify()
        def backcount():
            for i in range(n,0,-1):
                text.set(i)
                time.sleep(1)
            rt.quit()
        bktd=threading.Thread(target=backcount)
        bktd.start()
        rt.mainloop()
        try:
            rt.destroy()
        except:
            pass

    def yesorno(self,argv):
        try:
            msg=argv['msg']
        except:
            msg='Example'
        rt = tk.Tk()
        rt.withdraw()
        global who
        who=-1

        def yesfun():
            print 'yes'
            global who
            who=0
            rt.quit()

        def nofun():
            print 'no'
            global who
            who=1
            rt.quit()

        l = tk.Label(rt, text=msg,font=('Times', '66', 'bold italic'),foreground='#ff00dd',background='#ffff09')
        byes = tk.Button(rt,text='YES',font=('Times', '30', 'bold italic'),foreground='#fff0dd',background='#999999',command=yesfun)
        bno = tk.Button(rt, text='NO', font=('Times', '30', 'bold italic'), foreground='#fff0dd',
                         background='#999999', command=nofun)
        l.grid(column=1, row=1,columnspan=2)
        byes.grid(column=1, row=2)
        bno.grid(column=2, row=2)

        #rt.overrideredirect(True)
        rt.iconbitmap('c:/Python27/DLLs/py.ico')
        rt.resizable(False, False)
        rt.title("Chose?")
        rt.update()  # update window ,must do
        curWidth = rt.winfo_reqwidth()  # get current width
        curHeight = rt.winfo_height()  # get current height
        scnWidth, scnHeight = rt.maxsize()  # get screen width and height
        # now generate configuration information
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                                  (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        rt.geometry(tmpcnf)
        rt.deiconify()
        rt.mainloop()
        rt.destroy()
        return who

    def ledForM1(self,argv):
        rt = tk.Tk()
        rt.withdraw()
        global who
        who = -1

        def redfun():
            global who
            who = 1
            rt.quit()

        def greenfun():
            global who
            who = 2
            rt.quit()

        def bluefun():
            global who
            who = 3
            rt.quit()

        def whitefun():
            global who
            who = 4
            rt.quit()

        def offfun():
            global who
            who = 5
            rt.quit()

        def breakfun():
            global who
            who = 6
            rt.quit()

        l = tk.Label(rt, text=u'请选择看见的颜色', font=('Times', '66', 'bold italic'), foreground='#ff00dd',
                     background='#ffffff')
        bred = tk.Button(rt, text=u'红色', font=('Times', '30', 'bold italic'), foreground='#fff0dd',
                         background='#ff0000', command=redfun,width=20)
        bgreen = tk.Button(rt, text=u'绿色', font=('Times', '30', 'bold italic'), foreground='#000000',
                        background='#00ff00', command=greenfun,width=20)
        bblue = tk.Button(rt, text=u'蓝色', font=('Times', '30', 'bold italic'), foreground='#fff0dd',
                           background='#0000ff', command=bluefun,width=20)
        bwhite = tk.Button(rt, text=u'白色', font=('Times', '30', 'bold italic'), foreground='#000000',
                           background='#ffffff', command=whitefun,width=20)
        boff = tk.Button(rt, text=u'都没亮', font=('Times', '30', 'bold italic'), foreground='#fff0dd',
                            background='#888888', command=offfun,width=20)
        bbreak = tk.Button(rt, text=u'有的没亮', font=('Times', '30', 'bold italic'), foreground='#fff0dd',
                         background='#000000', command=breakfun,width=20)
        l.grid(column=1, row=1, columnspan=2)
        bred.grid(column=1, row=2)
        bgreen.grid(column=2, row=2)
        bblue.grid(column=1, row=3)
        bwhite.grid(column=2, row=3)
        boff.grid(column=1, row=4)
        bbreak.grid(column=2, row=4)

        # rt.overrideredirect(True)
        rt.iconbitmap('c:/Python27/DLLs/py.ico')
        rt.resizable(False, False)
        rt.title(u"LED测试")
        rt.update()  # update window ,must do
        curWidth = rt.winfo_reqwidth()  # get current width
        curHeight = rt.winfo_height()  # get current height
        scnWidth, scnHeight = rt.maxsize()  # get screen width and height
        # now generate configuration information
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight*2,
                                  (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        rt.geometry(tmpcnf)
        rt.deiconify()
        rt.mainloop()
        rt.destroy()
        print who
        return who


if __name__=='__main__':
    d=dialog({})
    d.count({"n":"5"})