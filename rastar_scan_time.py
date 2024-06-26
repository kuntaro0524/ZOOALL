import os,sys, datetime
import numpy as np
lines = open(sys.argv[1], "r").readlines()

block_num = 0
raster_block = []
for line in lines:
    if line.rfind("JOB Raster scan started.") != -1:
        #print line
        block_num += 1
        tmp_block = []

    if line.rfind("FILE_NAME") != -1:
        name_block = line

    if line.rfind("Now invoke the shutterless scan movement") != -1:
        #print line
        cols = line.split()
        timestr = cols[6]+" "+cols[8]
        
        # "2019/05/16 09:59:21:979."
        i = timestr.rfind(":")
        timestr = timestr[:i]
        #date_now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        date_now = datetime.datetime.strptime(timestr, '%Y/%m/%d %H:%M:%S')
        tmp_block.append(date_now)
        #print date_now

    if line.rfind(" Job Raster scan finished.") != -1:
        raster_block.append(tmp_block)

#print raster_block

for each_scan in raster_block:
    nlen = len(each_scan)
    #print nlen
    time_list = []
    for i in range(0, nlen):
        if i == 0:
            continue
        else:
            prev = each_scan[i-1]
            this = each_scan[i]
            diff = float((this - prev).seconds)
            time_list.append(diff)
    #print len(time_list)
    time_array = np.array(time_list)
    mean_time = time_array.mean()
    #print block
    starting_time = each_scan[0]
    ending_time = each_scan[-1]
    print "START_TIME=",starting_time, 
    print "END_TIME=",ending_time, 
    print "Consumed time: ", ending_time - starting_time, 
    print "MEAN_TIME=",mean_time, len(time_list)
