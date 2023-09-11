import sys,os,math


lines=open(sys.argv[1],"r").readlines()

for line in lines:
    cols = line.split()
    print("%s = cond['%s']"% (cols[0], cols[0]))

