import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import AnaShika
import CrystalSpot

#####
if __name__=="__main__":
        cxyz=(1.0960,   -10.0954,    -0.3053)
        phi=0.0
        prefix="kun-CPS1010-03_"
	scan_d="/isilon/users/target/target/Staff/kuntaro/171218-kohebi/test14-CPS1010-07/scan/2d"
        spot_finder="%s/_spotfinder"%scan_d
        diffscan_path=scan_d

        ashika=AnaShika.AnaShika(spot_finder,cxyz,phi)
        nimages_all=47*83
        completeness=0.99
        hbeam=0.010
        vbeam=0.015

        ashika.readSummary(prefix,nimages_all,completeness,timeout=120)
        ashika.reProcess(prefix,"n_spots")

        scan_id="2d"
        crystals=ashika.findCrystals(scan_id,"n_spots",dist_thresh=0.0151,score_thresh=20)

        cry_index=0
        single=[]
        non_single=[]

        for crystal in crystals:
                if crystal.getSize()==1:
                        single.append(crystal)
                else:
                        non_single.append(crystal)

		size_thresh=0.100
		dist_cry_thresh=0.04 # tate houkou 
		
	
		cry_index=0
	
	# Check overlap
	print("#########################")
	perfect=[]
	kabutteru_index_list=[]
	check_list=[0]*len(crystals)
	for index1 in range(0,len(crystals)):
		crystal1=crystals[index1]
       		crystal1.setDiffscanLog(diffscan_path)

		for index2 in range(index1+1,len(crystals)):
			crystal2=crystals[index2]
       			crystal2.setDiffscanLog(diffscan_path)
			print("Crystal1 %5d Crystal2 %5d\n"%(index1,index2))
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
	perfile=open("perfect.dat","w")
	index=0
	for c in check_list:
		if c==0:
			cry=crystals[index]
			x1a,y1a=cry.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				perfile.write("%8.5f %8.5f\n"%(x1,y1))
			perfect.append(cry)
		index+=1
	perfile.close()

	print("KABUTTERU",kabutteru_index_list)
	# Kabutteiru crystals no nearest distance calculation (x,z only)
	logfile=open("kabutteru.dat","w")
	hontouni_kabutteru_index_list=[]
	for c1,c2 in kabutteru_index_list:
		print("INDEX=",c1,c2)
		cry1=crystals[c1]
		cry2=crystals[c2]
		x1a,y1a=cry1.getXYlist()
		x2a,y2a=cry2.getXYlist()
		bad_flag=False
		for y1,y2 in zip(y1a,y2a):
			if numpy.fabs(y1-y2) < dist_cry_thresh:
				hontouni_kabutteru_index_list.append((c1,c2))
				for x1,y1 in zip(x1a,y1a):
					logfile.write("%8.5f %8.5f\n"%(x1,y1))
				logfile.write("\n\n")
				for x2,y2 in zip(x2a,y2a):
					logfile.write("%8.5f %8.5f\n"%(x2,y2))
				logfile.write("\n\n")
				check_list[c1]=-1
				check_list[c2]=-1


	## Non good crystal clusters
	index=0
	for crystal in crystals:
               	if crystal.getSize()==1:
			check_list[index]=10

		else:
			hsize,vsize=crystal.getDimensions(hbeam,vbeam)
			print("hsize,vsize=",hsize,vsize)
			if hsize > size_thresh or vsize > size_thresh:
				check_list[index]=-2
		index+=1

	# NG clusters (larger than crystal size)
	ngfile=open("ng.dat","w")
	ng_crystals=[]
	index=0
	for c in check_list:
		if c==-2 or c==-1:
			cry=crystals[index]
			x1a,y1a=cry.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				ngfile.write("%8.5f %8.5f\n"%(x1,y1))
			ngfile.write("\n\n")
			ng_crystals.append(cry)
		index+=1
	ngfile.close()

	# Zutazuta list
	zutazuta=[]
	index=0
	for c in check_list:
		if c<0:
			cry=crystals[index]
			zutazuta.append(cry)
		index+=1


	# Mar OK crystal
	gfile=open("good.dat","w")
	good_cry=[]
	index=0
	for c in check_list:
		print("CHECKLIST=",c)
		if c>0 and c!=10:
			cry=crystals[index]
			x1a,y1a=cry.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				gfile.write("%8.5f %8.5f\n"%(x1,y1))
			good_cry.append(cry)
		index+=1
	gfile.close()

	# Single crystal
	singlefile=open("single.dat","w")
	single_crystals=[]
	index=0
	for c in check_list:
		if c==10:
			cry=crystals[index]
			x1a,y1a=cry.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				singlefile.write("%8.5f %8.5f\n"%(x1,y1))
			single_crystals.append(cry)
		index+=1
	singlefile.close()

	print("Initial single crystals",len(single_crystals))

	# make crycodes
	def makeCryCode(x,y,score,imgnum):
     		# Adding this to the list of grids
       		cx,cy,cz=cxyz
       		crycodes=CrystalSpot.CrystalSpot(cx,cy,cz,phi)
   		crycodes.addXY(x,y,score,imgnum,isCheck=True)
		return crycodes

	# for ZUTAZUTA list
	bad_index=[]
	# each crystal
	print("ZUTAZUTA=",len(zutazuta))
	for cryindex in range(0,len(zutazuta)):
		x1a,y1a,scorea,imgna=zutazuta[cryindex].getInfo()
		bad_index=[0]*len(x1a)
		print("Crysal index",cryindex," NUMBER OF GRIDS",len(x1a))
		# each grid
		print("*******Comparison loop started*****")
		for index1 in range(0,len(x1a)):
			if bad_index[index1]==1:
				continue
			x1=x1a[index1]
			y1=y1a[index1]
			score1=scorea[index1]
			imgnum1=imgna[index1]
			for index2 in range(index1+1,len(x1a)):
				print("comparison cry1,cry2=",index1,index2)
				print("bad_index=",bad_index)
				if bad_index[index2]==1:
					continue

				x2=x1a[index2]
				y2=y1a[index2]
				score2=scorea[index2]
				imgnum2=imgna[index2]
				dx=x1-x2
				dy=y1-y2
				dist=math.sqrt(dx*dx+dy*dy)
				print("distance(%d,%d)=",index1,index2,dist)
				if dist <= vbeam:
					print("distance is shorter than vbeam")
					print("bad_index.append ",index2)
					bad_index[index2]=1
			print("BAD",len(bad_index))
		print("Final bad index=",bad_index)
		ncount=0
		for i in range(0,len(bad_index)):
			if bad_index[i]==0:
				x1a,y1a,scorea,imgna=zutazuta[cryindex].getInfo()
				x=x1a[i]
				y=y1a[i]
				score=scorea[i]
				imgnum=imgna[i]
				crycode=makeCryCode(x,y,score,imgnum)
				single_crystals.append(crycode)
				ncount+=1
		print("GOOD points=",ncount)

	print("SINGLE:",len(single_crystals))
	print("GOOD: ", len(good_cry))
	#print "ZUTAZUTA:",len(zutazuta)
	# Single crystal
	sss=open("single_new.dat","w")
	index=0
	for s in single_crystals:
		x1a,y1a=s.getXYlist()
		for x1,y1 in zip(x1a,y1a):
			sss.write("%8.5f %8.5f\n"%(x1,y1))
	sss.close()
