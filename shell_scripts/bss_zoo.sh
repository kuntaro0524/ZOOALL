#!/bin/sh
# 2015/07/22 K.Hirata
# Special setting for automatic data collection
# Configure files are in this directory 

# 2015/09/26 K.Hirata
# For suno3 experiments
# ZooConfig directory is moved from ~/Staff/ZooTest/
# zoo.csh is modified in this directory

selectCCD="EIGER9M"

# 2017/04/11
# ZOOM OUT
# move to x14 and fit pint axis
python ~/PPPP/10.Zoo/Libs/zoom_out.py

### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes
xsetroot -cursor_name star

######### For VIDEOSRV (remote) #########
sleep 1
ssh 192.168.163.6 "killall /usr/local/bss/videosrv"
sleep 2

# Please do not start videosrv with this script 161003
ssh -XC -c arcfour 192.168.163.6 "/usr/local/bss/videosrv --artray 3 --v4l2" &
sleep 2
xsetroot -cursor_name top_left_arrow

############### SHIKA Backend ##########################
if [ $selectCCD == "EIGER9M" ]; then

# Cheetah
echo "Starting Cheetah"
/usr/local/bss/startcheetah.sh

for i in {1..10}
do
 sleep 1
 cheetah_ok=0
 ssh 192.168.163.34 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && \
 ssh 192.168.163.31 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && break
 notify-send "BSS startup" "Cheetah not up. retrying (${i})."
 notify-send "BSS startup" "`/usr/local/bss/startcheetah.sh`"
 cheetah_ok=1
done

if [ "$cheetah_ok" == "1" ]
then
 notify-send "BSS startup ERROR" "Can't start cheetah!!" -i gnome-log -t 10000
 aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
 exit
fi

# Download server test
 if ! ssh -oBatchMode=yes 192.168.163.9 hostname
 then
  notify-send "BSS startup ERROR" "SSH to local-raid NOT configured!!" -i gnome-log -t 10000
  aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
  exit
 fi

# Hit-extract server test
if ! ssh -oBatchMode=yes 192.168.163.34 hostname
then
 notify-send "BSS startup ERROR" "SSH to 192.168.163.34 NOT configured!!" -i gnome-log -t 10000
 aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
 exit
fi

# 171114 changed
echo "BSS startup"
echo "\n\n" | /usr/local/bss/bss --server --console 

# After BSS shutdown
sleep 1
ssh 192.168.163.6 "killall $VIDEOSRV"

fi

END:
