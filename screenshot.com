#!/bin/csh
set TIME=720
set WORK=1

while( $WORK <= $TIME )
echo $WORK
# Screen shot to Log directory
import -window root ScreenShots/$1.png
sleep 60
@ WORK = $WORK + 1
end
