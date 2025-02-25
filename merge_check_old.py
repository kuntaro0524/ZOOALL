# 2020/10/15 
# check whether merge calculations have been finished
# just run 'python merge_check.py' 

import os
import sys
import glob

multimerge_sh_list = glob.glob("merge_*/slurm-*.out") # when merge calculations were carried out by ofp01
multimerge_sh_list += glob.glob("merge_*/multimerge.sh.o*") # when merge calculations were carried out by oys
multimerge_sh_list = sorted(multimerge_sh_list)
cnt_merge_dir = len(multimerge_sh_list)
cnt_finished = 0

print "--------------------------------------"
for multimerge_sh in multimerge_sh_list:
    merge_path = multimerge_sh.split('/')[0]
    print "Merge Dir: %s" % merge_path

    last_line = open(multimerge_sh).readlines()[-1].rstrip()
    print last_line
    if last_line.startswith("finished"):
        cnt_finished += 1
    print "--------------------------------------"

print "# or merge dir: %d" % (cnt_merge_dir)
print "Finished:       %d" % (cnt_finished)
        
        
