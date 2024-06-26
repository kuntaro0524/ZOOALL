from tkinter import *

def timer():
   time = int(buff.get())
   if time > 0:
       frame.after(1000, timer)
       time -= 1
       buff.set(str(time))

frame = Tk()
import tkinter as Tk
import time
 
WID = 10
 
class Timer(Tk.Frame):
    def __init__(self,master=None): 
        Tk.Frame.__init__(self,master)
 
        self.master.title('megatimer')
 
        minute = Tk.Label(self,text=u'min',font='Arial, 12')
        seconds = Tk.Label(self,text=u'sec',font='Arial, 12')
 
        self.s1 = Tk.Spinbox(self, from_ = 0, to = 99, increment = 1, width = WID)
        self.s2 = Tk.Spinbox(self, from_ = 0, to = 59, increment = 1, width = WID)
 
        self.tokei=Tk.Label(self,text=u'00:00',font='Arial, 25')
 
        b1 = Tk.Button(self,text='Start',command=self.start)
        b2 = Tk.Button(self,text='Reset',command=self.stop)
 
        minute.grid(row=0, column=1, padx=5, pady=2,sticky=Tk.W)
        self.s1.grid(row=0, column=0, padx=5, pady=2)
        seconds.grid(row=0, column=3, padx=5, pady=2,sticky=Tk.W)
        self.s2.grid(row=0, column=2, padx=5, pady=2)
        b1.grid(row=1, column=0,columnspan=2, padx=5, pady=2,sticky=Tk.W+Tk.E)
        b2.grid(row=1, column=2,columnspan=2, padx=5, pady=2,sticky=Tk.W+Tk.E)
        self.tokei.grid(row=2, column=0,columnspan=4, padx=5, pady=2,sticky=Tk.W+Tk.E)
 
    def start(self): 
        self.started=True
        self.kake()
        self.finish = time.time() + self.s3
        self.count()
 
    def count(self):
        if self.started:
            t = self.finish - time.time()
            if t < 0:
                self.tokei.config(text="####R$RR#RR#R#W")
 
            else:
                self.tokei.config(text='%02d:%02d'%(t/60,t%60)) 
                self.after(100, self.count)
 
 
    def stop(self): 
        self.started=False
        self.tokei.config(text='00:00')
 
    def kake(self): 
        ss1=self.s1.get()
        ss2=self.s2.get()
        c1=int(ss1)
        c2=int(ss2)
        self.s3=c1*60+c2
 
if __name__ == '__main__':
    f = Timer()
    f.pack()
    f.mainloop()
buff = StringVar()
buff.set('10')

entry  = Entry(frame, textvariable = buff)
entry.pack(side='left')
button = Button(frame, text = 'START', command = timer)
button.pack(side='right')

frame.mainloop()

