#!/bin/sh

finished=""

while true
do
 if [ ! -e ~/.zoo_current ]
 then
  sleep 10; continue
 fi

 cfg=(`cat ~/.zoo_current`)
 name=${cfg[0]}
 root=${cfg[1]}

 if [ "${root}" == "${finished}" ]
 then
  sleep 10; continue
 fi

 tmp=`mktemp`
 #tmp=/dev/stdout
 
 log=`ls -rt /isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/log/bss_*.log | tail -n1`
 
 echo "ROOT DIR= $root" > $tmp
 LANG=C date >> $tmp
 echo "" >> $tmp
 
 
 echo "Last 10 lines of $log" >> $tmp
 echo "  (`stat $log | grep Modify`)" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat -n $log | tail -n10 | tr -d '\000' >> $tmp
 echo "" >> $tmp

 echo "Last errors in the log" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat -n $log | egrep -i "(fail|error)" | tail -n10 | tr -d '\000' >> $tmp
 echo "" >> $tmp
 
 echo "Last 10 scan results" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 for f in `grep -l scan_complete $root/*/scan/_spotfinder/*selected.dat | xargs \ls -rt | tail -n10`
 do
  nhits=`wc -l $f | awk '{print $1}'`
  summarydat=`echo $f | sed -e "s,/[^/]*selected.dat,/summary.dat,"`
  maxscore=`awk 'BEGIN{a=-1}/n_spots/{if($5>a)a=$5}END{print a}' $summarydat`
  tmpname=`echo $f | sed -e "s,${root},,; s,/_spotfinder.*,,"`
  echo "  $tmpname hits=$((nhits-2)) max_score=$maxscore" >> $tmp
 done
 echo "" >> $tmp

 echo "Last 10 img files" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 #find $root -type f -name \*.img -printf "%T+ %p\n" | sort | tail -n10 | sed -e "s,$root,," >> $tmp
 find `ls -drt $root/* | tail -n2 ` -type f -name \*_master.h5 -printf "%T+ %p\n" | sort | tail -n10 | sed -e "s,$root,," >> $tmp
 echo "" >> $tmp

 echo "Zoo progress log" >> $tmp
 echo "--------------------------------------------------------------------------" >> $tmp
 cat "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_progress.log" | tail -n20 | tr -d '\000' >> $tmp

 
 if [ "${cfg[2]}" == "finished" ]
 then
  echo "Job finished. Bye!" >> $tmp
  finished=$root
 fi

 nkf -j $tmp
 #nkf -j $tmp | mail -s "[Message from ZOO] $name" -c k.yamashita@spring8.or.jp,ykawano@spring8.or.jp hirata@spring8.or.jp
 nkf -j $tmp | mail -s "[Message from ZOO] $name" keitaro.yamashita@riken.jp
 
 rm $tmp

 echo "sleeping.."
 sleep 1800

done
