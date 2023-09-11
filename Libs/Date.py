import datetime
import time

class Date:

    def __init__(self):
        self.tdy=datetime.datetime.today()
        self.today=datetime.date.today().isoformat()

    def getNowMyFormat(self,option="sec"):
        ttime=datetime.datetime.now()
        if option == "sec":
            timestr=datetime.datetime.strftime(ttime, '%y%m%d%H%M%S')
        elif option == "min":
            timestr=datetime.datetime.strftime(ttime, '%y%m%d%H%M')
        elif option == "hour":
            timestr=datetime.datetime.strftime(ttime, '%y%m%d%H')
        else:
            timestr=datetime.datetime.strftime(ttime, '%y%m%d')

        return timestr

    def getToday(self):
        print(datetime.datetime.now())
        return self.today

    def getTodayDire(self):
        today=self.getToday()
        today=today[2:]
        tmp=today.replace("-","")
        return tmp

    def getTimeDire(self):
        line=str(self.tdy)
        current_time=line.split()[1]

        #print current_time
        icut=current_time.rfind(":")

        return current_time[:icut].replace(":","")

    def getOkutsuTime(self,timestr):
        timestr=timestr[:timestr.rfind(".")]
        tt=datetime.datetime.strptime(timestr,"%Y/%m/%d %H:%M:%S")
        return tt

    def getTimeFromZooDB(self,timestr):
        tt=datetime.datetime.strptime(timestr,"%Y%m%d%H%M%S")
        return tt

    def getDiffMin(self,tstart,tend):
        diff = tend - tstart
        dmin = diff.seconds/60.0
        return dmin

    #tt=datetime.datetime.today()
    #print tt.year,tt.month,tt.day
    #datestr,timestr=timestr.split()
    #print datestr,timestr
    #ystr,mstr,dstr=datestr.split("/")
    #print "Year:%s"%ystr
    #print "Month:%s"%mstr
    #print "Date:%s"%dstr
    #tt.year=ystr
    #tt.month=mstr
    #tt.day=dstr

    def getDiffSec(self,dtstart,dt1):
        diff=dt1-dtstart
        #print diff.days
        #print diff.seconds

        seconds=diff.days*24*60*60+diff.seconds

        return seconds

if __name__=="__main__":
    #print (tmptime-ppp).seconds
    date=Date()

    #print date.getToday()
    #print date.getTodayDire()
    #print date.getTimeDire()
    #print date.getOkutsuTime("2011/06/20 06:57:20.067763")
    t1= date.getTimeFromZooDB("20190127120507")
    t2= date.getTimeFromZooDB("20190127120638")
    print(date.getDiffMin(t1,t2))
