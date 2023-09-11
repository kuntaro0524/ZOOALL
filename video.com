#!/bin/csh
#set VIDEOSRV="/isilon/Common/CentOS4/videosrv_sep26_2016"

######### For VIDEOSRV (remote) #########
sleep 1
ssh 192.168.163.6 "killall videosrv"
# --artray 3 = 4x4 binning
ssh -XC -c arcfour 192.168.163.6 "/isilon/Common/CentOS4/videosrv_sep26_2016 --artray 3" &
sleep 1

