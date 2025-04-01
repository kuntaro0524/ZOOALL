#!/bin/sh
ZOOCONFDIR="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
LOG=`ls -latr $BLCONFIG/bss/beamsize.config`
CURRENT_BSCONFIG=`echo $LOG | awk '{print $11}'`
FULLPATH=$BLCONFIG/bss/$CURRENT_BSCONFIG
cp -f $FULLPATH $ZOOCONFDIR/bss/
NEWFILE=$ZOOCONFDIR/bss/$CURRENT_BSCONFIG
echo $NEWFILE
ln -sf $NEWFILE $ZOOCONFDIR/beamsize.config
