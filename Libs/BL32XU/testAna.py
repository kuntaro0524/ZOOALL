import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import AnaShika

if __name__=="__main__":
        cxyz=(1.0960,   -10.0954,    -0.3053)
        phi=0.0
        prefix="kun-CPS1010-03_"
        spot_finder="/isilon/users/target/target/Staff/kuntaro/171218/kun-CPS1010-03/scan/_spotfinder"
        diffscan_path="/isilon/users/target/target/Staff/kuntaro/171218/kun-CPS1010-03/scan/"

        ashika=AnaShika.AnaShika(spot_finder,cxyz,phi)
        nimages_all=3901
        completeness=0.99
	hbeam=0.010
	vbeam=0.015
	

        ashika.readSummary(prefix,nimages_all,completeness,timeout=120)
        ashika.reProcess(prefix,"n_spots")

	scan_id="kun-CPS1010-03"
	crystals=ashika.findCrystals(scan_id,"n_spots",dist_thresh=0.0151,score_thresh=20)

	cry_index=0
	single=[]
	non_single=[]

	for crystal in crystals:
		if crystal.getSize()==1:
			single.append(crystal)
		else:
			non_single.append(crystal)

	## Non good crystal clusters
	size_thresh=0.100
	dist_cry_thresh=0.05 # tate houkou 
	ng_clusters=[]
	ok_clusters=[]

	ok_file=open("ok_cluster.dat","w")
	ng_file=open("ng_cluster.dat","w")
	index=0
	for non_single_crystal in non_single:
		xlist,ylist=non_single_crystal.getXYlist()
		hsize,vsize=non_single_crystal.getDimensions(hbeam,vbeam)

		if hsize > size_thresh or vsize > size_thresh:
			ng_clusters.append(non_single_crystal)
			for x,y in zip(xlist,ylist):
				ng_file.write("%8.5f %8.5f %8.5f %8.5f\n"%(x,y,hsize,vsize))
			ng_file.write("\n\n")
		else:
			ok_clusters.append(non_single_crystal)
			for x,y in zip(xlist,ylist):
				ok_file.write("%8.5f %8.5f %8.5f %8.5f\n"%(x,y,hsize,vsize))
			ok_file.write("\n\n")
		index+=1
		print "plot \"nonsingle.dat\" i %d u 1:2 \\"%index

	# Check overlap
	print "#########################"
	perfect=[]
	kabutteru_index_list=[]
	check_list=[0]*len(crystals)
	for index1 in range(0,len(crystals)):
		crystal1=crystals[index1]
        	crystal1.setDiffscanLog(diffscan_path)

		for index2 in range(index1+1,len(crystals)):
			crystal2=crystals[index2]
        		crystal2.setDiffscanLog(diffscan_path)
			print "Crystal1 %5d Crystal2 %5d\n"%(index1,index2)
			# Left no houga ookii suuchi
			l1xyz,r1xyz=crystal1.findHoriEdges()
			l2xyz,r2xyz=crystal2.findHoriEdges()

			l1=l1xyz[1]
			r1=r1xyz[1]
			l2=l2xyz[1]
			r2=r2xyz[1]
			if (l2>=r1 and l2<=l1) or (r2>=r1 and r2<=l1):
				kabutteru_index_list.append((index1,index2))
				check_list[index1]=1
				check_list[index2]=1
			elif (l1>=r2 and l1<=l2) or (r1>=r2 and r1<=l2):
				kabutteru_index_list.append((index1,index2))
				check_list[index1]=1
				check_list[index2]=1

	# Perfect OK crystal
	logfile=open("perfect.dat","w")
	index=0
	for c in check_list:
		if c==0:
			cry=crystals[index]
			x1a,y1a=cry.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				logfile.write("%8.5f %8.5f\n"%(x1,y1))
			perfect.append(cry)
		index+=1
	logfile.close()

	# Kabutteiru crystals no nearest distance calculation (x,z only)
	logfile=open("kabutteru.dat","w")
	hontouni_kabutteru_index_list=[]
	for c1,c2 in kabutteru_index_list:
		print c1,c2
		cry1=crystals[c1]
		cry2=crystals[c2]
		x1a,y1a=cry1.getXYlist()
		x2a,y2a=cry2.getXYlist()

		for y1,y2 in zip(y1a,y2a):
			if numpy.fabs(y1-y2) < dist_cry_thresh:
				hontouni_kabutteru_index_list.append((index1,index2))
				break

		for x1,y1 in zip(x1a,y1a):
			logfile.write("%8.5f %8.5f\n"%(x1,y1))
		logfile.write("\n\n")
		for x2,y2 in zip(x2a,y2a):
			logfile.write("%8.5f %8.5f\n"%(x2,y2))
		logfile.write("\n\n")

	print kabutteru_index_list

	sfile=open("single.dat","w")
	print "SINGLE"
	for single_crystal in single:
		xlist,ylist=single_crystal.getXYlist()
		hsize,vsize=single_crystal.getDimensions(hbeam,vbeam)
		for x,y in zip(xlist,ylist):
			sfile.write("%8.5f %8.5f %8.5f %8.5f\n"%(x,y,hsize,vsize))
		sfile.write("\n\n")
