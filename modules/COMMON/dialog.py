import Tkinter as tk

class dialog():
    def __init__(self,argv):
        pass


    def info(self,argv):
        try:
            msg=argv['msg']
        except:
            msg='Example'
        top = tk.Tk()
        w = tk.Label(top, text=msg,font=('Times', '66', 'bold italic'),foreground='#ff00dd',background='#999999')
        w.pack()
        top.mainloop()


if __name__=='__main__':
    d=dialog({})
    d.info({})