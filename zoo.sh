#!/bin/bash
# 2015/07/22 K.Hirata
# Special setting for automatic data collection
# Configure files are in this directory 

# 2015/09/26 K.Hirata
# For suno3 experiments
# ZooConfig directory is moved from ~/Staff/ZooTest/
# zoo.csh is modified in this directory

# 2017/04/11
# ZOOM OUT
# move to x14 and fit pint axis
python ~/PPPP/10.Zoo/Libs/zoom_out.py

# Check the current beamsize.config
CONFDIR=/isilon/blconfig/bl32xu.rh7/bss/
ZOOCONFDIR="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/bss/"
#BLCONFIG="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
LOG=`ls -latr $CONFDIR/beamsize.config`
CURRENT_BSCONFIG=`echo $LOG | awk '{print $11}'`
FULLPATH=$CONFDIR/$CURRENT_BSCONFIG
#cp -f $FULLPATH $ZOOCONFDIR/
NEWFILE=$ZOOCONFDIR/$CURRENT_BSCONFIG
#echo "REPLACING" $NEWFILE $ZOOCONFDIR/beamsize.config
#ln -sf $NEWFILE $ZOOCONFDIR/beamsize.config

# Recover camera.inf
#VIDEO_CONFI_ORIG=/isilon/blconfig/bl32xu/video/
#echo "Camera inf file is copied from the original .bak file"
#ls -latr $VIDEO_CONFI_ORIG/camera.inf
#LOG=`ls -latr $VIDEO_CONFI_ORIG/camera.inf`
#CAMERAINF_HONTAI=`echo $LOG | awk '{print $11}'`
#echo "$CAMERAINF_HONTAI.bak $CAMERAINF_HONTAI"
#\cp -f $VIDEO_CONFI_ORIG/$CAMERAINF_HONTAI.bak $VIDEO_CONFI_ORIG/$CAMERAINF_HONTAI


# 2015/07/22 Succeeded in the data collection at the end of June
#VIDEOSRV="/isilon/Common/CentOS4/videosrv_jul02_2015a"
# 2016/09/26 Problems relating 5 connections were solved. Test use.
#VIDEOSRV="/isilon/Common/CentOS4/videosrv_sep26_2016"
# 2018/12/11 replaced to the latest version
##VIDEOSRV="/usr/local/bss/videosrv"
# 2019/03/15 replaced to the DFK72 version YKp190315
VIDEOSRV="/usr/local/bss/videosrv3"

### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes
xsetroot -cursor_name star

######### For VIDEOSRV (remote) #########
sleep 1
##ssh 192.168.163.6 "killall $VIDEOSRV"  # for ARTRAY
killall $VIDEOSRV    # for DFK72  YK@190315
sleep 5

# Please do not start videosrv with this script 161003
##ssh -XC -c arcfour 192.168.163.6 "$VIDEOSRV --artray 3" &  #  for ARTRAY
#BLCONFIG=/blconfig $VIDEOSRV --dfk 3 &  ### for DFK72  YK@190315
#BLCONFIG=/blconfig $VIDEOSRV --v4l2 &  ### for WAT3921 YK@200119

# Is this required???
#BLCONFIG=/blconfig $VIDEOSRV --load_json=/blconfig/video/vg51/vg51.json --grab_mode opencv &  ### for vg51 YK@201002

#sleep 2
#ssh -XC -c arcfour 192.168.163.6 "/usr/local/bss/videosrv --artray 3 --v4l2" &

xsetroot -cursor_name top_left_arrow

############### SHIKA Backend ##########################
# Cheetah

echo "Starting Cheetah"
#wget -O - http://ramchan:8080/start/$(id -u)/$(id -g) 2>/dev/null
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
 #if ! ssh -oBatchMode=yes 192.168.163.10 hostname
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
echo "\n\n" | /usr/local/bss/bss --server --console  --admin
#echo "\n\n" | /usr/local/bss/bss --server --console


# After BSS shutdown
sleep 1
##ssh 192.168.163.6 "killall $VIDEOSRV"    # for ARTRAY
killall $VIDEOSRV      # for DFK72 YK@190315
sleep 1
killall bss

END:
