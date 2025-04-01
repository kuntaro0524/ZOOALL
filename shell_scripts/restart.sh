#!/bin/bash
bss_jobid=15863
vs_jobid=15866

kill $bss_jobid
kill $bs_jobid

bash ~/ZOO32XU/zoo.sh &
