#!/bin/sh
#selectCCD=None
#selectCCD=MX225HS
#selectCCD=MX225HS_TEST
#selectCCD=MX225HE
#selectCCD=Q315r
selectCCD=EIGER9M

### set for New videosrv on NVIDIA GPU
LIBGL_ALWAYS_INDIRECT=yes

#date > ~/test.log
#echo "**************************************" >> ~/test.log
#echo "" >> ~/test.log
#echo "  startup BSS  " >> ~/test.log
#echo "" >> ~/test.log
#echo "**************************************" >> ~/test.log

xsetroot -cursor_name star

if [ $selectCCD == "MX225HS" ]; then 
#ssh 192.168.163.32 /usr/local/bss/restart_marccd_on_this_host.sh
 echo "kill CCD server"
 ########For MX225HS###########
 ssh 192.168.163.32 "killall  marccd_server_socket"
 sleep 1
 ssh 192.168.163.32 "killall  hsserver_legacy"
 sleep 1
 echo "Startup CCD server"
 #ssh 192.168.163.32 "hsserver_legacy" &
# TEST : outputting stdin/stderr to a file : it seemed to work very well K.Hirata
# 2014.10.17 1:40AM
  #ssh 192.168.163.32 "hsserver_legacy>&/tmp/hserver_output" & # comment-out 150215 10:26
  ssh 192.168.163.32 "hsserver_legacy>&/dev/null" &

# TEST : outputting stdin/stderr to a /dev/null
#ssh 192.168.163.32 "hsserver_legacy>&/dev/null" &

fi

if [ $selectCCD == "MX225HS_TEST" ]; then 
#ssh 192.168.163.32 /usr/local/bss/restart_marccd_on_this_host.sh
echo "TEST mode for MX225HS"
echo "No action for booting HS server"

fi

if [ $selectCCD == "MX225HE" ]; then 
 echo "kill CCD server"
  #########For MX225HE###########
  ssh 192.168.163.32 "xhost +"
  ssh 192.168.163.32 "killall  marccd" &
  sleep 1
  ssh 192.168.163.32 "killall  marccd_server_socket" &
  sleep 1
  ssh 192.168.163.32 "marccd -rf" -display :0.0 &
fi

if [ $selectCCD == "Q315r" ]; then 
 username=`whoami`
 ssh -l $username 192.168.2.202 "setenv DISPLAY :0"
sleep 1
 ssh -l $username 192.168.2.202 "killall -9 det_api_workstation" &
sleep 1
 ssh -l $username 192.168.2.202 "killall -9 ccd_image_gather" &
sleep 1
 ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
sleep 1
 ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
sleep 1
fi

############### SHIKA Backend ##########################
if [ $selectCCD == "EIGER9M" ]; then 

# Cheetah
echo "Starting Cheetah"
#wget -O - http://ramchan:8080/start/$(id -u)/$(id -g) 2>/dev/null
/usr/local/bss/startcheetah.sh
#wget -O - http://ramchan:8080/stop 2>/dev/null

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

fi
## /EIGER stuff

######### For VIDEOSRV (remote) #########
sleep 1
python /isilon/BL32XU/BLsoft/PPPP/03.GUI/00.Pint/121008/zoom_pint.py &
sleep 1
ssh 192.168.163.6 "killall  videosrv"
#ssh -XC -c arcfour 192.168.163.6 "/usr/local/bss/videosrv --artray 0" &
ssh -XC -c arcfour 192.168.163.6 "/usr/local/bss/videosrv --artray --v4l2" &
sleep 1

#ssh 192.168.163.5 "killall  videosrv" &
#ssh -X 192.168.163.5 "/usr/local/bss/run_videosrv" &

xsetroot -cursor_name top_left_arrow

######### For Monitoring permittion of HOME dir ########
#/usr/local/bin/ChkChmod.csh &
#sleep 1

##### start BSS main routine
# Normal user operation mode
#/usr/local/bss/bss --quick
/usr/local/bss/bss --console

# For staff tuning
#/usr/local/bss/bss --admin --notune

# For zigzag scan test 2015/05/29
#/usr/local/bss/bss_may29_2015_zigzag --admin --notune

# Plate screening test 20120708 by YK
##/usr/local/bss/bss_July8_2012_hase7 --admin --notune

######### For VIDEOSRV (local) #########
#ps auxww | grep videosrv | grep -v grep | awk '{print $2}'| xargs kill
##ps auxww | grep videosrv | grep -v grep | awk '{print $2}'| xargs kill
######### For VIDEOSRV (remote) #########
sleep 1
ssh 192.168.163.6 "killall  videosrv"
sleep 1
killall  videosrv
