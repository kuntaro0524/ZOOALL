#!/bin/bash

eiger_dl_server=192.168.223.172
eiger_cheetah_node1=192.168.223.82
#eiger_cheetah_node2=192.168.223.80

## K. Sakurai added at 2022.12.16
zenity --info --title="BSS" --text="BSS_startup.sh has been running" --width 150 --timeout 10 >/dev/null &

## K. Sakurai added at 2021.10.29
#if [ -f "/usr/local/bss/BSS_is_executing.py" ]
# then
#  python3 /usr/local/bss/BSS_is_executing.py &
# fi


## EIGER begin

# Cheetah
echo "Starting Cheetah"
/usr/local/bss/startcheetah.sh

for i in {1..10}
do
 sleep 1
 cheetah_ok=0
 ssh $eiger_cheetah_node1 "/oys/xtal/cctbx/snapshots/dials-v1-14-13/build/bin2/yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && break
# ssh $eiger_cheetah_node1 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && break
# ssh $eiger_cheetah_node2 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" && break
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
 if ! ssh -oBatchMode=yes $eiger_dl_server hostname
 then
  notify-send "BSS startup ERROR" "SSH to $eiger_dl_server NOT configured!!" -i gnome-log -t 10000
  aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
  exit
 fi

# Hit-extract server test
 if ! ssh -oBatchMode=yes $eiger_cheetah_node1 hostname
 then
  notify-send "BSS startup ERROR" "SSH to $eiger_cheetah_node1 NOT configured!!" -i gnome-log -t 10000
  aplay /usr/lib64/libreoffice/share/gallery/sounds/falling.wav > /dev/null 2>&1
  exit
 fi


## EIGER end
############ For log copy daemon ############
killall cp_config.com
/staff/Common/SW/cp_config.com bl44xu 10 &

# echo "\n\n" | /usr/local/bss/bss --console --server --admin --quick --notune
#echo "\n\n" | /usr/local/bss/bss --console --server  --quick
echo "\n\n" | /usr/local/bss/bss --console --server --admin --quick


####### for log copy daemeon ###########
killall cp_config.com

