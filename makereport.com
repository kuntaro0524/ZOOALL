#!/bin/bash

dbfile=$1
title=$2

echo $dbfile

# At the data collection directory
#yamtbx.python ~/ZOO32XU/Libs/ZOOhtmlMaker.py $dbfile $2
yamtbx.python /isilon/users/target/target/PPPP/10.Zoo/Libs/ZOOreporter.py $dbfile $title

# For _kamoproc
cd _kamoproc/
yamtbx.python /isilon/users/target/target/PPPP/18.Report/XDSReporter.py . report_$2.html
cd ../

# Time stamp
timestr=`date "+%y%m%d%H%M"`
arcfile=${timestr}_${2}_report.tgz

echo "making $arcfile"

# archive a file
tar cvfz $arcfile ./*html _kamoproc/*html _kamoproc/contents/

# Copy this file to /isilon/BL32XU/TMP/
cp $arcfile /isilon/BL32XU/TMP/

echo "Running directory: $PWD" > message.txt
echo " ############################# " >> message.txt
echo " <<<<< contents >>>>> " >> message.txt
echo " report_*.html : brief report of ZOO data collection (to be obsoleted)" >> message.txt
echo " quick.html    : brief report of ZOO data collection (to be enhanced)" >> message.txt
echo "_kamoproc/correct.html : data statistics from XDS can be checked." >> message.txt
echo "You can check data quality of crystals by using correct.html on WEB browser." >> message.txt

#xxxxcat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" kunio.hirata@riken.jp << message.tx
cat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" kunio.hirata@riken.jp
