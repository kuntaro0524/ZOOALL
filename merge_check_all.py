# 2020/10/15 
# check whether merge calculations have been finished
# just run 'python merge_check.py' 

import os
import sys
import glob

multimerge_sh_list = glob.glob("_kamo*/merge_*/slurm-*.out") # when merge calculations were carried out by ofp01
#multimerge_sh_list += glob.glob("_kamo_30deg/merge_*/slurm-*.out") # when merge calculations were carried out by ofp01
multimerge_sh_list += glob.glob("_kamo*/merge_*/multimerge.sh.o*") # when merge calculations were carried out by oys
#multimerge_sh_list += glob.glob("_kamo_30deg/merge_*/multimerge.sh.o*") # when merge calculations were carried out by oys
multimerge_sh_list += glob.glob("_kamo*/merge_*/par.o*") # when merge calculations were carried out by local (at BL45XU)
#multimerge_sh_list += glob.glob("_kamo_30deg/merge_*/par.o*") # when merge calculations were carried out by local (at BL45XU) 
multimerge_sh_list = sorted(multimerge_sh_list)
cnt_merge_dir = len(multimerge_sh_list)
cnt_finished = 0
cnt_error = 0
error_list = ""

print(multimerge_sh_list, len(multimerge_sh_list))

print "--------------------------------------"
for multimerge_sh in multimerge_sh_list:
    merge_path = multimerge_sh.split('/')[0]
    print "Merge Dir: %s" % multimerge_sh

    fmulti = open(multimerge_sh).readlines()
    flen = len(fmulti)
    for x in range(flen-1):
        if fmulti[x].count("Error"):
            print(fmulti[x])
            error_list += "%s\n" % multimerge_sh
            cnt_error += 1
    if fmulti[-1].startswith("finished"):
        print(fmulti[-1])
        cnt_finished += 1
#    last_line = open(multimerge_sh).readlines()[-1].rstrip()
#    print last_line
#    if last_line.startswith("finished"):
#        cnt_finished += 1
    print "--------------------------------------"

print "# or merge dir: %d" % (cnt_merge_dir)
print "Error:          %d" % (cnt_error)
print "Finished:       %d" % (cnt_finished)
        
print "-- ERROR LIST ----------------------------"
print error_list
