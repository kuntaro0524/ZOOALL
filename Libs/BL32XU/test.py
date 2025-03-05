import sys,os,math


lines=open(sys.argv[1],"r").readlines()


for line in lines:
	if line.rfind("n_spots")!=-1:
		print line

