import datetime
import time

"""
start
mount_finished
centering_finished
raster_start
raster_end
data_collection_start
data_collection_end
"""

class StopWatch:
    def __init__(self):
        self.sw_dict={}

    def setTime(self,key):
        nowtime=datetime.datetime.now()
        self.sw_dict[key]=nowtime
        print self.sw_dict[key]

    def getDsecBtw(self,begtime_tag,endtime_tag):
        begtime=self.sw_dict[begtime_tag]
        endtime=self.sw_dict[endtime_tag]
        print begtime,endtime
        t_delta=(endtime-begtime).seconds
        return t_delta

    def getTime(self,key):
        picked_time=self.sw_dict[key]
        tstr=picked_time.strftime('%Y/%m/%d %H:%M')
        #return self.sw_dict[key]
        return tstr

    def getNowStr(self):
        nowtime=datetime.datetime.now()
        tstr=nowtime.strftime('%Y%m%d%H%M%S')
        return tstr

if __name__=="__main__":
    sw=StopWatch()
    #sw.setTime("Start")
    #time.sleep(1.0)
    #sw.setTime("End")

    print sw.getNowStr()

    #p=sw.getDsecBtw("Start","End")
    #print "%8.3f sec"%p
    #print "%30s"%sw.getTime("Start")
    #print sw.getTime("End")
