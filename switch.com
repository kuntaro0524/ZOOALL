#!/bin/sh

sleep 2
killall bss

BLCONFIG="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"


### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes
xsetroot -cursor_name star

######### For VIDEOSRV (remote) #########
sleep 1
ssh 192.168.163.6 "killall videosrv"
sleep 2

ssh -XC -c arcfour 192.168.163.6 "videosrv --artray 3" &

xsetroot -cursor_name top_left_arrow

############### SHIKA Backend ##########################
# Cheetah
echo "Starting Cheetah"
wget -O - http://ramchan:8080/start/$(id -u)/$(id -g) 2>/dev/null

# For console mode BSS running
echo "\n\n" | /usr/local/bss/bss --server --console  --admin


# After BSS shutdown
sleep 1
ssh 192.168.163.6 "killall $VIDEOSRV"

END:
