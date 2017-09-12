from Tkinter import *
from tkMessageBox import *

class dialog():
    def __init__(self,argv):
        pass

    def confrim(self,argv):
        def answer():
            showerror("Answer", "Sorry, no answer available")

        def callback():
            if askyesno('Verify', 'Really quit?'):
                showwarning('Yes', 'Not yet implemented')
            else:
                showinfo('No', 'Quit has been cancelled')

        Button(text='Quit', command=callback).pack(fill=X)
        Button(text='Answer', command=answer).pack(fill=X)
        mainloop()

if __name__=='__main__':
    d=dialog()
    d.confrim()