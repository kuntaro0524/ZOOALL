# coding: utf-8
import tkinter
import tkinter.font as font
import tkinter.messagebox as tkmsg
import re
import datetime

class PyTimer(tkinter.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.createWidgets()

    def createWidgets(self):
        self.font1 = font.Font(family="Helvetica", size=10)
        
        self.label1 = tkinter.Label(root,text="CountDownTimer",font=self.font1)
        self.label1.pack(padx=2,pady=2,fill="both",expand=1)

        self.edit2 = tkinter.Entry(root,width=16,font=self.font1,justify="center")
        self.edit2.pack(padx=2,pady=2,fill="both",expand=1)
        
        self.frame1 = tkinter.Frame(root)
        self.frame1.button6 = tkinter.Button(self.frame1,text="25分",command=self.startTimer25min,font=self.font1)
        self.frame1.button6.pack(padx=2,pady=2,fill="both",expand=1,side="left")
        self.frame1.button7 = tkinter.Button(self.frame1,text="5分",command=self.startTimer05min,font=self.font1)
        self.frame1.button7.pack(padx=2,pady=2,fill="both",expand=1,side="left")
        self.frame1.pack(fill="both",expand=1)
        
        self.button5 = tkinter.Button(root,text="Start",command=self.startTimer,font=self.font1)
        self.button5.pack(padx=2,pady=2,fill="both",expand=1)

        self.time = 0
        self.timeSet = ""
        self.bTimer = False

    def startTimer25min(self):
        if not self.bTimer:
            self.edit2.delete(0,tkinter.END)
            self.edit2.insert(tkinter.END,"25")
            self.startTimer()

    def startTimer05min(self):
        if not self.bTimer:
            self.edit2.delete(0,tkinter.END)
            self.edit2.insert(tkinter.END,"5")
            self.startTimer()
    
    def startTimer(self):
        if(self.edit2.get() != ""):
            str = self.edit2.get()
            self.time = 0
            match = re.match(r'([0-9]+)\:([0-9]+)',str)

            self.timeSet = str
            if match:
                self.time = int(match.group(1))*60.0 + int(match.group(2))
            else:
                self.time = int(str)*60.0

            if self.bTimer:    
                self.bTimer = False
                self.button5.configure(text = "Start")
                #self.after(100,self.countDownTimer)
                print("stop Timer")
            else:
                self.bTimer = True
                self.button5.configure(text = "Stop")
                print("start Timer")
                self.after(200,self.countDownTimer)                
                

    def countDownTimer(self):
        self.time = self.time - 0.2
        #print(self.time)
        m_min = int(self.time/60)
        m_sec = int(self.time-m_min*60)
        self.edit2.delete(0,tkinter.END)
        self.edit2.insert(tkinter.END,"%02d:%02d" % (m_min,m_sec))
        
        if self.time <= 0:
            print("Time is Over!")
            self.bTimer = False
            self.button5.configure(text = "Start")
            
            dt_now = datetime.datetime.now()
            m_str = self.timeSet+'mins passed\nat '+str(dt_now.hour)+':'+str(dt_now.minute)
            tkmsg.showinfo('pyTimer',m_str)
                        
            self.edit2.delete(0,tkinter.END)
            self.edit2.insert(tkinter.END,self.timeSet)
        else:
            if self.bTimer:
                self.after(200,self.countDownTimer)


iX = 200-15
iY = 150-35

root = tkinter.Tk()
root.title("pyTimer")
root.geometry(str(iX)+"x"+str(iY))

app = PyTimer(master=root)
app.mainloop()
