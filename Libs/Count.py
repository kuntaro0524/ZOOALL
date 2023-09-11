import sys
import socket
import time
import datetime
import math
import timeit

from Received import *
from File import *
from AnalyzePeak import *

class Count:
    def __init__(self,server,ch1,ch2):
        self.s=server
        self.ch1=ch1+1
        self.ch2=ch2+1
        self.is_count=0

    # String/Bytes communication via a socket
    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def testing(self,cnttime):
        strtime=str(cnttime)+"sec"
        #print strtime
        com0="put/bl_32in_st2_counter_1/init"
        com1="put/bl_32in_st2_counter_1/clear"
        com2="put/bl_32in_st2_counter_1/30sec"
        com3="get/bl_32in_st2_counter_1/query"

        # counter set
        recbuf=self.communicate(com0)

        # counter clear
        recbuf=self.communicate(com1)

        # set integration time 
        recbuf=self.communicate(com2)

        while(1):
            recbuf = self.communicate(com3)
            cnt_buf=Received(recbuf).get(3)
            info_list=cnt_buf.split('_')
            value=int(info_list[2].replace("count",""))
            print(value)
            time.sleep(0.05) # wait

        return True

    def setCountSec(self,cnttime):
        strtime=str(cnttime)+"sec"
        #print strtime
        com1="put/bl_32in_st2_counter_1/clear"
        com2="put/bl_32in_st2_counter_1/"+strtime

        # counter clear
        recbuf=self.s.communicate(com1)
        # set integration time 
        recbuf=self.communicate(com2)

        return True

    def setCountMsec(self,cnttime):
        strtime=str(cnttime)+"msec"
        #print strtime
        com1="put/bl_32in_st2_counter_1/clear"
        com2="put/bl_32in_st2_counter_1/"+strtime

        # counter clear
        recbuf=self.communicate(com1)

        # set integration time 
        recbuf = self.communicate(com2)

        self.time_msec=cnttime/1000.0

        return True

    def getStoredCount(self,time_msec):
        com3="get/bl_32in_st2_counter_1/query"
        time.sleep(time_msec) # wait
        recbuf=self.communicate(com3)

        # obtain the 3rd column in the returned buffer
        cnt_buf=Received(recbuf).get(3)

        print(cnt_buf)

        return cnt_buf

    def __storeCountMsec(self,cnttime):
        strtime=str(cnttime)+"msec"
        #print strtime
        com1="put/bl_32in_st2_counter_1/clear"
        com2="put/bl_32in_st2_counter_1/"+strtime
        com3="get/bl_32in_st2_counter_1/query"

        # counter clear
        recbuf=self.communicate(com1)

        # get counter value
        recbuf=self.communicate(com2)
        time_msec=cnttime/1000.0
        time.sleep(time_msec) # wait

        recbuf=self.communicate(com3)

        # obtain the 3rd column in the returned buffer
        cnt_buf=Received(recbuf).get(3)

        return cnt_buf

    def __storeCount(self,cnttime):
        strtime=str(cnttime)+"sec"
        com1="put/bl_32in_st2_counter_1/clear"
        com2="put/bl_32in_st2_counter_1/"+strtime
        com3="get/bl_32in_st2_counter_1/query"

        # counter clear
        recbuf=self.communicate(com1)

        # get counter value
        recbuf=self.communicate(com2)
        time.sleep(cnttime) # wait
        recbuf=self.communicate(com3)

        # obtain the 3rd column in the returned buffer
        cnt_buf=Received(recbuf).get(3)

        return cnt_buf

    def getCount(self,time):
        retinfo=self.__storeCount(time)
        #print retinfo
        info_list=retinfo.split('_')

        ch1_value=int(info_list[self.ch1].replace("count",""))
        ch2_value=int(info_list[self.ch2].replace("count",""))

        rtn_list=[ch1_value,ch2_value]

        return rtn_list

    def getCountMsec(self,time):
        retinfo=self.__storeCountMsec(time)
        #print retinfo
        info_list=retinfo.split('_')

        ch1_value=int(info_list[self.ch1].replace("count",""))
        ch2_value=int(info_list[self.ch2].replace("count",""))

        rtn_list=[ch1_value,ch2_value]

        return rtn_list

    def getPIN(self,gain):
        if self.is_count==0:
            current=self.getCount(1.0)
            print(current)
            self.is_count==1
            const_gain=math.pow(10,float(gain-1.0))
            value=current[0]/const_gain
            str="Count:%8d PIN value: %8.3f uA"%(current[0],value)

        return str

    # usage: after shutter
    def simpleCountBack(self,shutter,ch1,ch2,inttime,ndata):
        if self.isInit==False:
            self.init()
        # shutter close
        print("Shutter close: estimation of background")
        shutter.close()
        # average back ground
        ave1,ave2=self.simpleCount(ch1,ch2,inttime,ndata)

        # shutter open
        print("Shutter open: estimation of actual count")
        self.prepScan()
        ave3,ave4=self.simpleCount(ch1,ch2,inttime,ndata,ave1,ave2)

        print("Average ch1: %8d ch2: %8d\n"%(ave3,ave4))
        return ave3,ave4

    def simpleCount(self,ch1,ch2,inttime,ndata,back1=0,back2=0):
        if self.isInit==False:
                self.init()
        counter=Count(self.s,ch1,ch2)
        f=File("./")

        prefix="%03d"%f.getNewIdx3()
        ofilename="%s_count.scn"%prefix
        of=open(ofilename,"w")

        # initialization
        starttime=time.time()
        strtime=datetime.datetime.now()
        of.write("#### %s\n"%starttime)
        of.write("#### %s\n"%strtime)
        ttime=0
        for i in arange(0,ndata,1):
            currtime=time.time()
            ttime=currtime-starttime
            ch1,ch2=counter.getCount(inttime)
            ch1=ch1-back1
            ch2=ch2-back2
            of.write("12345 %8.4f %12d %12d\n" %(ttime,ch1,ch2))
        of.close()

        # file open
        ana=AnalyzePeak(ofilename)
        x,y1,y2=ana.prepData3(1,2,3)

        py1=ana.getPylabArray(y1)
        py2=ana.getPylabArray(y2)

        mean1=py1.mean()
        mean2=py2.mean()
        std1=py1.std()
        std2=py2.std()

        of=open(ofilename,"a")

        of.write("COUNTER1:%5d Average: %12.5f Std.:%12.5f (%8.3f perc.)\n"%(3,py1.mean(),py1.std(),py1.std()/py1.mean()*100.0))
        of.write("COUNTER2:%5d Average: %12.5f Std.:%12.5f (%8.3f perc.)\n"%(0,py2.mean(),py2.std(),py2.std()/py2.mean()*100.0))

        of.close()
        return mean1,mean2

    def getPrecisePIN(self,gain):
        if self.is_count==0:
                current=self.getCount(1.0)
                self.is_count==1
        const_gain=math.pow(10,float(gain-1.0))
        value=current[0]/const_gain
        str="Count:%8d PIN value: %8.3f uA"%(current[0],value)

        return str

    def calcPIN(self,energy):
        print("calcPIN")
        #flux=(3.6/energy)*(1/(1-exp(absorption)*2.33*0.03)*(currennt/1.602E-19)

if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))
        
        counter=Count(s,0,3)
        print(counter.getCount(1.0))

        f=File("./")

        ofile=open("intensity.dat","w")
        while(1):
                ti=datetime.datetime.now()
                ch1,ch2=counter.getCount(1.0)
                ofile.write("%10s%10d%10d\n"%(ti,ch1, ch2))
                ofile.flush()
                #print "%s %12d" %(ti,ch2)
                time.sleep(1.0)

        s.close()
