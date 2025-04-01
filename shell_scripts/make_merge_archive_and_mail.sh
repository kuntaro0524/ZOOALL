#!/bin/bash

title=$1
sstring=$2

# Making file list for 'merge_blend' and 'start from 1.5A resolution'
ls | grep merge_blend | grep $2 > file.lst

# Making archive file
yamtbx.python ~/PPPP/18.Report/make_archive_for_merged_final.py file.lst $1

# archive file path
arcfile=`ls *$1*`

echo $arcfile

# Copy this file to /isilon/BL32XU/TMP/
cp -f $arcfile /isilon/BL32XU/TMP/

echo "Running directory: $PWD" > message.txt
#xxxxcat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" kunio.hirata@riken.jp << message.tx
cat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" kunio.hirata@riken.jp
