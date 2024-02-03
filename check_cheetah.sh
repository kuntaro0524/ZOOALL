#!/bin/sh

#ssh ramchan "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py"

 echo "check into 192.168.163.34"
 ssh 192.168.223.82 "yamtbx.python /usr/local/cheetah_daemon/check_cheetah.py" 
sleep 1

echo "To (re)start Cheetah, run startcheetah.sh"
