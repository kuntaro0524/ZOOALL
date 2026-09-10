#!/bin/tcsh

if ($$ != `pgrep -fo $0`) then
    notify-send "`basename $0` is aleady running."
    exit 1
endif

videosrv &
sleep 10
yamtbx.python /isilon/BL45XU/videosrv0.py

# Cheetah
/usr/local/bss/startcheetah.sh

#date > ~/test.log
#echo "**************************************" >> ~/test.log
#echo "" >> ~/test.log
#echo "  startup BSS  " >> ~/test.log
#echo "" >> ~/test.log
#echo "**************************************" >> ~/test.log

#########For MX225HE###########
#setenv username `whoami`
#echo $username
#ssh -l $username 192.168.195.109 "xhost +"
#ssh -l $username 192.168.195.109 "killall -9 marccd_server_socket" &
#ssh -l $username 192.168.195.109 "marccd -rf >& /dev/null" -display :0.0 &

#########For Q315_remote_1###########
#setenv username `whoami`
#ssh -l $username 192.168.2.202 "setenv DISPLAY :0"
#ssh -l $username 192.168.2.202 "killall -9 det_api_workstation" &
#ssh -l $username 192.168.2.202 "killall -9 ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e det_api_workstation" &
#ssh -l $username 192.168.2.202 "xterm -display :0 -e ccd_image_gather" &
###############################


#echo "restart --user "$gid":"$uid"" > /isilon/blconfig/bl45xu/watchfurka/PILATUS_user.tmp && mv /isilon/blconfig/bl45xu/watchfurka/PILATUS_user.tmp /isilon/blconfig/bl45xu/watchfurka/PILATUS_user

#########For BSS (all beamline)###########
#/usr/local/bss/bss --admin --notune
echo "\n\n" | /usr/local/bss/bss --server --console  --websocket

ps auxww | grep videosrv | grep -v grep | awk '{print $2}'| xargs kill

#########For Q315_local#############
#ps auxww | grep det_api_workstation | grep -v grep | awk '{print $2}'| xargs kill
#ps auxww | grep ccd_image_gather | grep -v grep | awk '{print $2}'| xargs kill
#rm -f /dkc/*

#########For Q315_remote_2##########
#ssh -l $username 192.168.2.202 "killall -9 det_api_workstation" &
#ssh -l $username 192.168.2.202 "killall -9 ccd_image_gather" &
#rm -f /dkc/*
###################################

#########For MX225HE#########
#ssh -l $username 192.168.195.109 "killall -9 marccd_server_socket" &


#echo "**************************************" >> ~/test.log
#echo "" >> ~/test.log
#echo "  shutting down BSS  " >> ~/test.log
#echo "" >> ~/test.log
#echo "**************************************" >> ~/test.log


