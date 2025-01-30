#!/bin/bash -f

### \rm -rf all_run.sh arc.lst *tmp merge_* _kamo* report_*.html *tgz nikudango_*.log make_archive.log

shopt -s expand_aliases

module unload xds dials
module load xds/20230630
module load dials/3-19-0

which yamtbx.python

#2021-12-09 17:03:59 - ZooNavigator - INFO - goAround - 341 - All measurements have been finished.
# ~/ZOO32XU/ZooLogs/zoo_211209.log

#StartTime=$(date +%Y:%m:%d:%H:%M)
StartDate=`date '+%y%m%d'`
#PREFIX=`pwd | awk -F"/" '{print $NF}'`
#PREFIX=`basename $(pwd)`
PREFIX=`basename $(pwd)  | awk -F"_" '{print $NF}'`
ZooCsv=`ls -rt ZOOPREP_*.csv | tail -1`
ZooDB=`ls -rt zoo_*.db | tail -1`
CDIR=`pwd`
DownloadError=0

NewZoo=True
#NewZoo=False

Wait=True
#Wait=False

KAMO_LargeWedge=True
#KAMO_LargeWedge=False

sge_pe_name='par'

#StartDate="211209"
#StartTime="2021:12:09:16:00:00"

DATE=`date +%Y-%m-%dT%H:%M`
#echo "Start Time =" ${StartTime}
echo "Start Date =" ${StartDate}
echo "ZooCsv=" ${ZooCsv}
echo "PREFIX =" ${PREFIX}

echo $KAMO_LargeWedge $Wait

BFlag=`grep -e "helical" -e "mix" -e "single" ${ZooCsv} | wc -l`
echo "BFlag= " ${BFlag}
if [ ${BFlag} -gt 0 ]; then
  echo "not only mutli"
  nproc=4
  echo ""
else
  echo "only mutli"
  nproc=4
  echo ""
fi

MFlag=`grep -e "multi" -e "mix" ${ZooCsv} | wc -l`
echo "MFlag= " ${MFlag}
if [ ${MFlag} -le 0 ]; then
	nproc=16
	echo "only helical and single"
else
	nproc=4
fi

echo $BFlag, $MFlag, $nproc

if [ $KAMO_LargeWedge == True ]; then
 echo $KAMO_LargeWedge
 if [ $Wait == True ]; then
    echo "start KAMO LargeWedge for waiting"
    #source /opt/xtal/ccp4-7.1/bin/ccp4.setup-csh
    #setenv DATE `date +%Y-%m-%dT%H:%M`
    DATE=`date +%Y-%m-%dT%H:%M`
    echo $DATE
    cd ${CDIR}
    pwd
    echo "for kamo helical wait" >> which.tmp
    which yamtbx.python >> which.tmp
    which pointless >> which.tmp
    #kamo bl=32xu use_tmpdir_if_available=False batch.engine=slurm nproc=${nproc} exclude_dir='_kamo*' &
    #kamo bl=32xu use_tmpdir_if_available=False sge_pe_name=${sge_pe_name} batch.engine=slurm nproc=${nproc} exclude_dir='_kamo*' &
    kamo bl=32xu use_tmpdir_if_available=False batch.mem_per_cpu=12G batch.engine=slurm nproc=${nproc} exclude_dir='_kamo*' &
    if [ $? != 0 ]; then
       echo "error stop!!![kamo_buttagiri]"
       exit 1
    fi
    #cd _kamoproc
    #bash ~/Staff/kawano/scripts/ForKAMO/UntillFinish.sh $DATE
    #bash ~/Staff/kawano/scripts/ForKAMO/rerun_kamo.sh
 elif [ $Wait == False ]; then
    echo "start KAMO LargeWedge for not waiting"
    #source /opt/xtal/ccp4-7.1/bin/ccp4.setup-csh
    #setenv DATE `date +%Y-%m-%dT%H:%M`
    DATE=`date +%Y-%m-%dT%H:%M`
    echo $DATE
    cd ${CDIR}
    pwd
    echo "for kamo helical nowait" >> which.tmp
    which yamtbx.python >> which.tmp
    which pointless >> which.tmp

    #kamo bl=other use_tmpdir_if_available=False nproc=${nproc} batch.engine=slurm exclude_dir='_kamo*' &
    #kamo bl=other use_tmpdir_if_available=False nproc=${nproc} batch.engine=slurm auto_close=nogui exclude_dir='_kamo*' &
    kamo bl=other use_tmpdir_if_available=False batch.mem_per_cpu=12G batch.engine=slurm nproc=${nproc} auto_close=nogui exclude_dir='_kamo*' &
    if [ $? != 0 ]; then
       echo "error stop!!![kamo_buttagiri]"
       exit 1
    fi
    #cd _kamoproc
    #bash ~/Staff/kawano/scripts/ForKAMO/UntillFinish.sh $DATE
    #bash ~/Staff/kawano/scripts/ForKAMO/rerun_kamo.sh
  fi
fi


LastTray=`tail -1 ${ZooCsv} | tail -1 | awk -F ',' '{print $4}'`
LastWell=`tail -1 ${ZooCsv} | tail -1 | awk -F ',' '{print $5}' | awk -F '-' '{print $NF}' | awk -F '+' '{print $NF}'`
LastID=`printf "%s-%02s" ${LastTray} ${LastWell}`
echo "Last Pin ID" $LastID

if [ $NewZoo == True ]; then
  #ZooLog="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_${StartDate}.log"
  #ZooLog=`ls -rt /isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_*.log | tail -1`
  ZooLog=`ls -rt /staff/bl32xu/BLsoft/ZOO32XU/ZooLogs/zoo_*.log | tail -1`
else
  ZooLog=`ls -rt /staff/bl32xu/BLsoft/NewZoo/ZooLogs/zoo_*.log | tail -1`
fi
echo ${ZooLog}
echo ""

StartTime=`grep "Start processing " ${ZooLog} | grep -e "${ZooCsv}" -e "${ZooDB}" | tail -1 | awk '{print $1":"$2}' | sed 's/-/:/g'`
echo "StartTime =" ${StartTime}
echo ""

if [ $Wait == True ]; then
  while [ -z "${StartTime}" ]
  do
    if [ $NewZoo == True ]; then
      ZooLog=`ls -rt /staff/bl32xu/BLsoft/ZOO32XU/ZooLogs/zoo_*.log | tail -1`
    else
      ZooLog=`ls -rt /staff/bl32xu/BLsoft/NewZoo/ZooLogs/zoo_*.log | tail -1`
    fi
    ZooCsv=`ls -rt ZOOPREP_*.csv | tail -1`
    ZooDB=`ls -rt zoo_*.db | tail -1`
    StartTime=`grep "Start processing " ${ZooLog} | grep -e "${ZooCsv}" -e "${ZooDB}" | tail -1 | awk '{print $1":"$2}' | sed 's/-/:/g'`
    echo "StartTime =" ${StartTime}
    echo "Now Waiting For Start measurement for ${PREFIX} in ${ZooLog}"
    echo ""
    echo "Now date" date
    #DownloadError=`find ./ -name 'download_eiger*log' | xargs grep -e ' Download timeout!' | wc -l`
    #echo 'No. of Download error =' ${DownloadError}
    sleep 300
  done

  FlagStartLastPin=`grep " Processing " ${ZooLog} | grep " ${LastID} "`
  while [ -z "${FlagStartLastPin}" ]
  do
    if [ $NewZoo == True ]; then
      ZooLog=`ls -rt /staff/bl32xu/BLsoft/ZOO32XU/ZooLogs/zoo_*.log | tail -1`
    else
      ZooLog=`ls -rt /staff/bl32xu/BLsoft/NewZoo/ZooLogs/zoo_*.log | tail -1`
    fi
    FlagStartLastPin=`grep " Processing " ${ZooLog} | grep " ${LastID} "`
    echo "FlagStartLastPin = " ${FlagStartLastPin}
    echo "Waiting start measurement for Last Pin: ${LastID}"
    echo "Now date" date
    sleep 600
  done

  FinishTime=`grep "All measurements have been finished" ${ZooLog} | tail -1 | awk '{print $1":"$2}' | sed 's/-/:/g'`
  echo "Finish Time =" ${FinishTime}
  echo ""

  while [[ "${FinishTime//':'}" -le "${StartTime//':'}" ]]
  do
    #echo "FinishTime < StartTime"
    echo "Now Waiting for Finish Measurement"
    sleep 600
    echo ""
    echo "Now date" date
    FinishTime=`grep "All measurements have been finished" ${ZooLog} | tail -1 | awk '{print $1":"$2}' | sed 's/-/:/g'`
    echo "Start Time =" ${StartTime}
    echo "Finish Time =" ${FinishTime}
    echo ""
  done

  echo "All measurements have been finished at ${FinishTime}"
  echo "waiting about 30sec"
  sleep 300
fi

sleep 30
# Remake SHIKA Report
bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/remake_html_shika_reports.sh &
sleep 30

if [ ${BFlag} -gt 0 ]; then
    echo "not only multi"
    echo "start buttagiri KAMO"
	#source /opt/xtal/ccp4-7.1/bin/ccp4.setup-csh
        #source ~/.kpython_setting
	#setenv DATE `date +%Y-%m-%dT%H:%M`
        #DATE=`date +%Y-%m-%dT%H:%M`
	#echo $DATE
        echo $SHELL
        cd ${CDIR}
        pwd
	echo "for kamo_buttagiri no wait" >> which.tmp
        which yamtbx.python >> which.tmp
        which pointless >> which.tmp

        kamo bl=other split_data_by_deg=30.0 workdir=_kamo_30deg use_tmpdir_if_available=False nproc=4 batch.mem_per_cpu=8G batch.engine=slurm auto_close=nogui exclude_dir='_kamo*'
        #kamo bl=other split_data_by_deg=30.0 workdir=_kamo_30deg use_tmpdir_if_available=False nproc=4 batch.engine=slurm auto_close=nogui exclude_dir='_kamo*'
        #kamo bl=other split_data_by_deg=30.0 workdir=_kamo_30deg use_tmpdir_if_available=False nproc=4 batch.engine=slurm exclude_dir='_kamo*' &
        if [ $? != 0 ]; then
                echo "error stop!!![kamo_buttagiri]"
                exit 1
	fi
	#cd _kamo_30deg
else
    echo "only multi"
fi


echo "sleep 300sec"
sleep 300

bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/UntillFinish.sh $DATE
bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/KillKamo.sh ${CDIR}

#bash ~/Staff/kawano/scripts/ForKAMO/rerun_kamo.sh

echo "Finish KamoButtagiri"
echo "sleep 30sec"
sleep 30

#setenv DATE `date +%Y-%m-%dT%H:%M`
DATE=`date +%Y-%m-%dT%H:%M`
echo $DATE
echo $SHELL
cd ${CDIR}
pwd

echo "make_nikudango"

echo "for make_nikudango" >> which.tmp
which yamtbx.python >> which.tmp
which pointless >> which.tmp
which kamo.auto_multi_merge >> which.tmp
#yamtbx.python /staff/Common/kunpy/kamo_process/make_niku_dango.py --beamline BL32XU
yamtbx.python /staff/bl45xu/bin/make_niku_dango.py --beamline BL32XU
if [ $? != 0 ]; then
    echo "error stop!!![make_niku_dango.py]"
    exit 1
fi

echo "Finish make_nikudango"
sleep 30

echo "start auto merge"
#source /opt/xtal/ccp4-7.1/bin/ccp4.setup-sh
sed -i.bak 's/min_aredun=2.0/min_aredun=1.5/' merge_inputs/*.sh
sed -i.bak 's/=sge/=slurm/g' merge_inputs/*.sh
sed -i.bak 's/ batch.engine=/ batch.mem_per_cpu=5G batch.engine=/g' merge_inputs/*.sh
#sed -i.bak 's/ merge.clustering=cc   / merge.clustering=cc   merge.cc_clustering.cc_to_distance="sqrt(1-cc^2)"   /' merge_inputs/*.sh

EXELFILE=`ls *.xlsx`
CSVFILES=`ls merge_inputs/*csv`

for L in ${CSVFILES}
do
 echo ${EXELFILE} $L
 kpython staff/bl32xu/Staff/kawano/scripts/ForKAMO/change_anom_flag.py ${EXELFILE} ${L}
done

#kpython staff/bl32xu/Staff/kawano/scripts/ForKAMO/change_anom_flag02.py

echo "for merge" >> which.tmp
which yamtbx.python >> which.tmp
which pointless >> which.tmp
which kamo.auto_multi_merge >> which.tmp

#bash all_run.sh
yamtbx.python /staff/Common/mizuno/stbio/merge_sch.py

echo "Wait for start auto merge"
sleep 300

bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/UntillFinish.sh $DATE

echo "FinishCheck Done"
sleep 30

find ./ -name ".tmp-*.jpt" | xargs \rm

echo "for goto_toilet" >> which.tmp
which yamtbx.python >> which.tmp
which pointless >> which.tmp
export prefix=$(basename `pwd`)
#yamtbx.python /staff/Common/kunpy/zoo_report/goto_toilet.py `basename ${PWD}  | awk -F"_" '{print $NF}'` -c -b BL32XU
yamtbx.python /staff/bl45xu/bin/goto_toilet.py `basename ${PWD}  | awk -F"_" '{print $NF}'` -c -b BL32XU

echo "finish goto_tilet.py"
#bash ~/Staff/kawano/scripts/ForKAMO/add_SHIKA_toToilet.sh
echo "wait 30sec after toilet"
sleep 30

echo "BFlag = " ${BFlag}
if [ ${BFlag} -gt 0 ]; then
    echo "not only multi"
    cd ${CDIR}/_kamo_30deg
    pwd
    bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/make_automergeReport.sh
    echo "finish automergeReport in _kamo_30deg"
fi

sleep 30
echo "MFlag = " ${MFlag}
if [ ${MFlag} -gt 0 ]; then
    echo "only multi"
    cd ${CDIR}/_kamoproc
    pwd
    bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/make_automergeReport.sh
    echo "finish automergeReport in _kamoproc"
fi

cd ${CDIR}

#echo "firefox ./report_*.html _kamoproc/all_mergeReport.html _kamoproc/correct.html _kamo_30deg/all_mergeReport.html &"
#firefox ./report_*.html _kamoproc/all_mergeReport.html _kamoproc/correct.html _kamo_30deg/all_mergeReport.html &

echo "make hits_only.h5"
module unload dials
module load dials/1-14-13
cd ${CDIR}
pwd
sbatch /staff/bl32xu/Staff/kawano/scripts/mk_onlyhits.sh

echo "All Job Finished"

#echo 'No. of Download error =' ${DownloadError}

bash /staff/bl32xu/Staff/kawano/scripts/ForKAMO/DLCheck.sh
eog /staff/bl32xu/Staff/2024B/download_anal/DL-time*_`basename ${CDIR}`.png &

echo "firefox ./report_*.html _kamoproc/all_mergeReport.html _kamoproc/correct.html _kamo_30deg/all_mergeReport.html &"
firefox ./report_*.html _kamoproc/all_mergeReport.html _kamoproc/correct.html _kamo_30deg/all_mergeReport.html &
