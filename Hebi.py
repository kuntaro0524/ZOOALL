import sys,math,numpy,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import datetime
import LoopMeasurement
import Zoo
import AttFactor
import AnaShika
import Condition
import MyException
import StopWatch
import CrystalSpot

class Hebi:
	def __init__(self,zoo,lm,cxyz_2d,phi_face,wavelength,numCry=5,scan_dist=300.0):
		# Important class
		self.zoo=zoo
		# LoopMeasurement class
		self.lm=lm
		
		# Face angle
		self.phi_face=phi_face

		# At BL32XU 
		# scan h_beam, v_beam in [um]
		self.scan_hbeam=2.0
		self.scan_vbeam=5.0

		# list of found crystals
		self.cxyz_2d=cxyz_2d

		# Attenuator factor
		self.attfactor=AttFactor.AttFactor()

		# X-ray parameter
		self.wavelength=wavelength
		self.trans=0.1 # transmission for scan : CONFUSING in unit

		# Time out for waiting scan result (5mins)
		self.timeout=300.0
	
		# Limit number of crystals
		self.nCry=numCry

		# Limit of photon flux density for 1/2 diffracting power
		self.photon_density_limit=1.0E10

		# Completeness threshold in analysis for SHIKA result
		self.comp_thresh=0.99

		# Scan camera distance
		self.scan_dist=scan_dist # mm
	
	# Transmission in Left/Right edges of 1x5um beam
	def setTrans(self,trans_per):
		# Convert trans in [%] to a simple transmission
		self.trans=trans_per/100.0

	# Initial edge determinations from 2D raster scan
	# at face angle.
        def findRoughEdges(self,crystal,raster2d_path):
                # We should consider the conditions as below
                # if len(crystals)!=1:
                # sorting the crystal by 'crystal size' in CrystalSpot class
                # will be very important in near future.
		if crystal.getSize()==1:
			print "This crystal size is very small! >> SKIPPED"
			raise MyException.MyException("findRoughEdges: No good grids.")
		else:
			crystal.setDiffscanLog(raster2d_path)
                	left_code,right_code=crystal.findHoriEdges()

                return left_code,right_code

	# Initial findings of edges at face angle
	def faceScan(self,scan_id,center,phi_face):
		#self.scan_hbeam=1.0
		#self.scan_vbeam=5.0
		vrange_um=35.0
		hrange_um=34.0
                vstep_um=5.0
                hstep_um=2.0
		scan_mode="2D"

                # Wavelength is limited to 1.0A. Transmission is set to 10%
                att_thick=self.attfactor.getBestAtt(self.wavelength,self.trans)
                att_idx=self.attfactor.getAttIndexConfig(att_thick)

                print "Face scan at XYZ=",center

		# Limited to 50 Hz
                schfile,raspath=self.lm.rasterMaster(scan_id,scan_mode,self.scan_vbeam,self.scan_hbeam,
			vrange_um,hrange_um,vstep_um,hstep_um,center,phi_face,att_idx=att_idx,
			distance=self.scan_dist,exptime=0.02)
                self.zoo.doRaster(schfile)
                self.zoo.waitTillReady()
		print "faceScan finished!"
		return raspath

	# Final centering for both edges
	def finalVscan(self,scan_id,center,phi_start,scanv_um=100.0):
                scan_mode="Vert"
		scanh_um=10.0 # Dummy value
		vstep_um=5.0
		hstep_um=1.0 #Dummy value

                # Wavelength is limited to 1.0A. Transmission is set to 10%
                att_thick=self.attfactor.getBestAtt(self.wavelength,self.trans)
                att_idx=self.attfactor.getAttIndexConfig(att_thick)
		
		# scan h_beam, v_beam in [um]
		#self.scan_hbeam=1.0
		#self.scan_vbeam=5.0
                schfile,raspath=self.lm.rasterMaster(scan_id,scan_mode,self.scan_vbeam,self.scan_hbeam,
			scanv_um,scanh_um,vstep_um,hstep_um,center,phi_start,att_idx=att_idx,distance=self.scan_dist,exptime=0.1)

                self.zoo.doRaster(schfile)
                self.zoo.waitTillReady()

		return raspath

	# 2017/12/18 for kohebi 
        # Final centering for both edges
        def finalVscanZenbu(self,scan_id,center,phi_start,scanv_um,hbeam,vbeam):
                scan_mode="Vert"
                scanh_um=10.0 # Dummy value
                vstep_um=5.0
                hstep_um=1.0 #Dummy value

                # Wavelength is limited to 1.0A. Transmission is set to 10%
                att_thick=self.attfactor.getBestAtt(self.wavelength,self.trans)
                att_idx=self.attfactor.getAttIndexConfig(att_thick)

                # scan h_beam, v_beam in [um]
                schfile,raspath=self.lm.rasterMaster(scan_id,scan_mode,vbeam,hbeam,
                        scanv_um,scanh_um,vstep_um,hstep_um,center,phi_start,att_idx=att_idx,distance=self.scan_dist,exptime=0.1)

                self.zoo.doRaster(schfile)
                self.zoo.waitTillReady()

                return raspath

	# Vertical scan 
	# 2016/12/13
	# self.phi_face
	# This routine is made for sorting irradiation points in one crystal
	def scoreLists(self,scan_id,gxyz_list,scanv_um=500.0):
                scan_mode="Vert"
		scanh_um=10.0 # Dummy value
		vstep_um=5.0
		hstep_um=1.0 #Dummy value
		thresh_nspots=10
		# scan h_beam, v_beam in [um]
		#self.scan_hbeam=1.0
		#self.scan_vbeam=5.0

                # Wavelength is limited to 1.0A. Transmission is set to 10%
                att_thick=self.attfactor.getBestAtt(self.wavelength,self.trans)
                att_idx=self.attfactor.getAttIndexConfig(att_thick)

        	#print ashika.getTotalScore(prefix,kind="total_integrated_signal")
		
		# Each goniometer coordinate on the crystal
		data_idx=1
		raster_root=self.lm.raster_dir
		# List for sort
		score_array=[]
		for gxyz in gxyz_list:
			# At face angle
			scan_id_each="%s-point%03d-face"%(scan_id,data_idx)
                	schfile1,raspath1=self.lm.rasterMaster(scan_id_each,scan_mode,self.scan_vbeam,self.scan_hbeam,
				scanv_um,scanh_um,vstep_um,hstep_um,gxyz,self.phi_face,att_idx=att_idx,
				distance=self.scan_dist,exptime=0.1)
                	self.zoo.doRaster(schfile1)
                	self.zoo.waitTillReady()
			# Score analysis
			prefix="%s_"%scan_id_each
                	ashika=self.readSummaryDat(raspath1,prefix,gxyz,self.phi_face,
                        	thresh_nspots=thresh_nspots,comp_thresh=self.comp_thresh)
        		score_face=ashika.getTotalScore(prefix,kind="total_integrated_signal")
			print "FACE score=",score_face

			# At +90 deg
			phi90=self.phi_face+90.0
			scan_id_each="%s-point%03d-90apert"%(scan_id,data_idx)
                	schfile2,raspath2=self.lm.rasterMaster(scan_id_each,scan_mode,self.scan_vbeam,self.scan_hbeam,
				scanv_um,scanh_um,vstep_um,hstep_um,gxyz,phi90,att_idx=att_idx,
				distance=self.scan_dist,exptime=0.1)
                	self.zoo.doRaster(schfile2)
                	self.zoo.waitTillReady()
			# Score analysis
			prefix="%s_"%scan_id_each
                	ashika=self.readSummaryDat(raspath2,prefix,gxyz,phi90,
                        	thresh_nspots=thresh_nspots,comp_thresh=self.comp_thresh)
        		score_90=ashika.getTotalScore(prefix,kind="total_integrated_signal")
			print "FACE+90 score=",score_90
			total_score=score_face+score_90
			score_array.append((gxyz,total_score))
			print "###### TOTAL SCORE:",total_score
			data_idx+=1

		# Sorting score
		# Higher score -> lower index: option "reverse=True"
		print "BEFORE SORT",score_array
		sorted_crystal_list=sorted(score_array,key=lambda x:x[1],reverse=True)
		print "AFTER  SORT",sorted_crystal_list

		return sorted_crystal_list

        # Vertical scan & centering
        # 2016/12/18
        # each point : each centering
        def scoreListsWithCentering(self,scan_id,gxyz_list,scanv_um=500.0):
                scan_mode="Vert"
                scanh_um=10.0 # Dummy value
                vstep_um=5.0
                hstep_um=1.0 #Dummy value
                thresh_nspots=10
                # scan h_beam, v_beam in [um]
                #self.scan_hbeam=1.0
                #self.scan_vbeam=5.0

                # Wavelength is limited to 1.0A. Transmission is set to 10%
                att_thick=self.attfactor.getBestAtt(self.wavelength,self.trans)
                att_idx=self.attfactor.getAttIndexConfig(att_thick)

                #print ashika.getTotalScore(prefix,kind="total_integrated_signal")

                # Each goniometer coordinate on the crystal
                data_idx=1
                raster_root=self.lm.raster_dir
                # List for sort
                score_array=[]
                for gxyz in gxyz_list:
                        # At face angle
                        scan_id_each="%s-point%03d-face"%(scan_id,data_idx)
                        schfile1,raspath1=self.lm.rasterMaster(scan_id_each,scan_mode,self.scan_vbeam,self.scan_hbeam,
                                scanv_um,scanh_um,vstep_um,hstep_um,gxyz,self.phi_face,att_idx=att_idx,
                                distance=self.scan_dist,exptime=0.1)
                        self.zoo.doRaster(schfile1)
                        self.zoo.waitTillReady()
                        # Score analysis
                        prefix="%s_"%scan_id_each
                        ashika=self.readSummaryDat(raspath1,prefix,gxyz,self.phi_face,
                                thresh_nspots=thresh_nspots,comp_thresh=self.comp_thresh)
                        score_face=ashika.getTotalScore(prefix,kind="total_integrated_signal")
                        print "FACE score=",score_face

			# Center coordinate at the face
                	#grav_xyz_face00=ashika.getGravCenter(prefix)
                        grav_xyz_face00=self.lm.shikaGravXYZ(gxyz,self.phi_face,raspath1,scan_id_each,thresh_nspots=5)

                        # At +90 deg
                        phi90=self.phi_face+90.0
                        scan_id_each="%s-point%03d-90apert"%(scan_id,data_idx)
                        schfile2,raspath2=self.lm.rasterMaster(scan_id_each,scan_mode,self.scan_vbeam,self.scan_hbeam,
                                scanv_um,scanh_um,vstep_um,hstep_um,gxyz,phi90,att_idx=att_idx,
                                distance=self.scan_dist,exptime=0.1)
                        self.zoo.doRaster(schfile2)
                        self.zoo.waitTillReady()
                        # Score analysis
                        prefix="%s_"%scan_id_each
                        ashika=self.readSummaryDat(raspath2,prefix,gxyz,phi90,
                                thresh_nspots=thresh_nspots,comp_thresh=self.comp_thresh)
                        score_90=ashika.getTotalScore(prefix,kind="total_integrated_signal")
                        print "FACE+90 score=",score_90
                        total_score=score_face+score_90

			# Center coordinate at the face
                        grav_xyz_face90=self.lm.shikaGravXYZ(gxyz,phi90,raspath2,scan_id_each,thresh_nspots=5)
			
			# Centering with the information
			xfin=(grav_xyz_face00[0]+grav_xyz_face90[0])/2.0
			yfin=(grav_xyz_face00[1]+grav_xyz_face90[1])/2.0
			zfin=(grav_xyz_face00[2]+grav_xyz_face90[2])/2.0
			xyzfin=xfin,yfin,zfin

                        score_array.append((xyzfin,total_score))
                        print "###### TOTAL SCORE:",total_score
                        data_idx+=1

                # Sorting score
                # Higher score -> lower index: option "reverse=True"
                print "BEFORE SORT",score_array
                sorted_crystal_list=sorted(score_array,key=lambda x:x[1],reverse=True)
                print "AFTER  SORT",sorted_crystal_list

                return sorted_crystal_list

	def setCrystalSize(self):
                # scan h_beam, v_beam in [um]
                if self.scan_hbeam > self.scan_vbeam:
			self.crysize=(self.scan_hbeam+0.1)/1000.0 # [um]
		else:
			self.crysize=(self.scan_vbeam+0.1)/1000.0 # [um]

	# analyze 2D raster result The second edition
	# under conditions: 1(H) x 5(V) um beam is utilized for 2D raster scan
	def anaFaceScan2(self,raster_path,scan_id,cxyz,phi,thresh_nspots=5,direction="none"):
		# Function for sorting crystals
                def compCryScore(x,y):
                        a=x.score_total
                        b=y.score_total
                        #print "SCORE COMPARE",a,b
                        if a==b: return 0
                        if a<b: return 1
                        return -1
                        #print thresh_nspots,crysize

                # scan_id & prefix are different each other
                prefix="%s_"%scan_id
		
		# crystal size is set to the larger beam size + 0.1 um
		self.setCrystalSize()
		ashika=self.readSummaryDat(raster_path,scan_id,cxyz,phi,
			thresh_nspots=thresh_nspots,comp_thresh=self.comp_thresh)

		# Find 4 corners : in RELATIVE(X,Y) coordinates from 
		# summary.dat
		# lu: LeftUpper, ld: LeftDown, ru: RightUpper, rd: RighDown
		# all of grids are assumed to be good.
		lu,ld,ru,rd=ashika.getCorners(prefix)
	 	grav_xy=ashika.getGravCenter(prefix)
		print "Grav xy=",grav_xy
		target_corner=ashika.getTargetCorner(lu,ld,ru,rd,grav_xy)
		print "Target corner=",target_corner
		max_score=ashika.getMaxScore(prefix)
		threshold_score=int(max_score*0.8)
		print "Score threshold=",threshold_score

		gx,gy,gz=ashika.findNearestGrid(threshold_score,prefix,target_corner,raster_path)
		print "final xyz=",gx,gy,gz
		ret_gxyz=(gx,gy,gz)

		return ret_gxyz

	def anaVscan(self,cxyz,vphi,raster_path,scan_id,thresh_nspots=3,margin=0.005,crysize=0.01,comp_thresh=0.95):
		try:
                	v_grav=self.lm.shikaGravXYZ(cxyz,vphi,raster_path,scan_id,
                        	thresh_nspots=thresh_nspots,crysize=crysize,comp_thresh=comp_thresh)
		except:
			print "anaVscan: No good grids were not found on this scan."
			raise MyException.MyException("anaVscan: No good grids!!!!!")
		
		return v_grav

	def getGoodTrans(self):
		print "faceScan"
		return 1.0

        # Relating to the summary.dat
	# copied from LoopMeasurement
        def readSummaryDat(self,raster_path,scan_id,cxyz,phi,thresh_nspots=30,comp_thresh=0.95):
                # SHIKA analysis
                shika_dir="%s/_spotfinder/"%raster_path
                ashika=AnaShika.AnaShika(shika_dir,cxyz,phi)
                ashika.setSummaryFile("summary.dat")
                # scan_id & prefix are different each other
                prefix="%s"%scan_id
		print "Searching prefix is %s"%prefix

                # N grids on the 2D raster scan
                ngrids=self.lm.raster_n_height*self.lm.raster_n_width

                # SHIKA waiting for preaparation
                # 12 minutes
                try:
                        ashika.readSummary(prefix,ngrids,comp_thresh=comp_thresh,timeout=self.timeout)

                except:
                        raise MyException.MyException("shikaSumSkipStrong failed to wait summary.dat")

                return ashika

        # coded on 2016/06/27
        # using new AnaShika.py
        # max_ncry : max number of crystals for data collection
	# copied from LoopMeasurement and modified
	# "thresh_nspots" is normally 'cond.shika_minscore'
        def getCrystals(self,raster_path,scan_id,thresh_nspots=30,crysize=0.10,max_ncry=50):
                def compCryScore(x,y):
                        a=x.score_total
                        b=y.score_total
                        print "SCORE COMPARE",a,b
                        if a==b: return 0
                        if a<b: return 1
                        return -1
                        print thresh_nspots,crysize

                # SHIKA analysis
                ashika=self.readSummaryDat(raster_path,scan_id,self.cxyz_2d,self.phi_face)
                # Setting threshold for searching
                ashika.setThresh(thresh_nspots)

                # Crystal finding
                print "Crystal size = %8.5f"%crysize
                crystals=ashika.findCrystals(scan_id,dist_thresh=crysize)
                n_cry=len(crystals)
                print "Crystals %5d\n"%n_cry

                # Sorting better crystals by total number of spots
                # The top of crystal is the best one
                # The bottom is the worst one
                crystals.sort(cmp=compCryScore)

		return crystals

	def logXYZ(self,xyz):
		strings="%9.4f %9.4f %9.4f"%(xyz[0],xyz[1],xyz[2])
		return strings

	def calcDist(self,xyz1,xyz2):
		x1,y1,z1=xyz1
		x2,y2,z2=xyz2

		dx=x1-x2
		dy=y1-y2
		dz=z1-z2

		distance=math.sqrt(dx*dx+dy*dy+dz*dz)

		return distance

	def setPhotonDensityLimit(self,photon_density_limit):
		print "photon density limit =%e"%self.photon_density_limit
		self.photon_density_limit=photon_density_limit

	# 2016/12/10 added for detecting crystal size
	def checkCrysizeAt(self,scan_id,gxyz):
		scan_length=500.0
		# At face angle
		Lv_d=self.finalVscan(scan_id,gxyz,self.phi_face,scan_length)
		return 1

	# Inteligent crystal list maker for helical/small wedge data collection
	def kohebi(self,raster_path,scan_id,thresh_nspots,crysize,max_ncry):
                def compCryScore(x,y):
                        a=x.score_total
                        b=y.score_total
                        print "SCORE COMPARE",a,b
                        if a==b: return 0
                        if a<b: return 1
                        return -1
                        print thresh_nspots,crysize

                size_thresh=0.100
                dist_cry_thresh=0.04 # tate houkou 
		hbeam=0.010
		vbeam=0.015

                # SHIKA analysis
                ashika=self.readSummaryDat(raster_path,scan_id,self.cxyz_2d,self.phi_face)
                # Setting threshold for searching
                ashika.setThresh(thresh_nspots)
		diffscan_path=raster_path

                # Crystal finding
                print "Crystal size = %8.5f"%crysize
                crystals=ashika.findCrystals(scan_id,dist_thresh=0.0151,score_thresh=thresh_nspots)
                n_cry=len(crystals)
                print "Crystals %5d\n"%n_cry
	
		# Check overlap
		print "#########################"
		perfect_crystals=[]
		kabutteru_index_list=[]
		check_list=[0]*len(crystals)
		for index1 in range(0,len(crystals)):
			crystal1=crystals[index1]
        		crystal1.setDiffscanLog(diffscan_path)
	
			for index2 in range(index1+1,len(crystals)):
				crystal2=crystals[index2]
        			crystal2.setDiffscanLog(diffscan_path)
				#print "Crystal1 %5d Crystal2 %5d\n"%(index1,index2)
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
		print "KABUTTERU=",kabutteru_index_list
	
		# Kabutteiru crystals no nearest distance calculation (x,z only)
		kaburidat=open("%s/kabutteru.dat"%raster_path,"w")
		hontouni_kabutteru_index_list=[]
		for c1,c2 in kabutteru_index_list:
			print "INDEX=",c1,c2
			cry1=crystals[c1]
			cry2=crystals[c2]
			x1a,y1a=cry1.getXYlist()
			x2a,y2a=cry2.getXYlist()
			bad_flag=False
			for y1,y2 in zip(y1a,y2a):
				if numpy.fabs(y1-y2) < dist_cry_thresh:
					hontouni_kabutteru_index_list.append((c1,c2))
					for x1,y1 in zip(x1a,y1a):
						kaburidat.write("%8.5f %8.5f\n"%(x1,y1))
					kaburidat.write("\n\n")
					for x2,y2 in zip(x2a,y2a):
						kaburidat.write("%8.5f %8.5f\n"%(x2,y2))
					kaburidat.write("\n\n")
					check_list[c1]=-1
					check_list[c2]=-1
	
	
		## Non good crystal clusters
		index=0
		for crystal in crystals:
                	if crystal.getSize()==1:
				check_list[index]=10
	
			else:
				hsize,vsize=crystal.getDimensions(hbeam,vbeam)
				print "hsize,vsize=",hsize,vsize
				if hsize > size_thresh or vsize > size_thresh:
					check_list[index]=-2
			index+=1
	
		# NG clusters (larger than crystal size)
		ngfile=open("%s/ng.dat"%raster_path,"w")
		ng_crystals=[]
		index=0
		# check_list: 
		# -2: very large crystal bunch in SHIKA heat map
		# -1: very near to the neighbor crystals
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
		gfile=open("%s/good.dat"%raster_path,"w")
		good_crystals=[]
		index=0
		for c in check_list:
			print "CHECKLIST=",c
			# check_list: c=10 -> single crystal (grid consists of 1)
			if c>0 and c!=10:
				cry=crystals[index]
				x1a,y1a=cry.getXYlist()
				for x1,y1 in zip(x1a,y1a):
					gfile.write("%8.5f %8.5f\n"%(x1,y1))
				good_crystals.append(cry)
			index+=1
		gfile.close()
	
		# Single crystal
		singlefile=open("%s/single.dat"%raster_path,"w")
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
	
		print "Initial single crystals",len(single_crystals)
	
		# make crycodes
		def makeCryCode(x,y,score,imgnum):
     			# Adding this to the list of grids
       			cx,cy,cz=self.cxyz_2d
       			crycodes=CrystalSpot.CrystalSpot(cx,cy,cz,self.phi_face)
   			crycodes.addXY(x,y,score,imgnum,isCheck=True)
			return crycodes
	
		# for ZUTAZUTA list
		# This list includes very large or overlapped crystal bunches
		# then "small wedge data collection" was applied 
		bad_index=[]
		# each crystal
		print "ZUTAZUTA=",len(zutazuta)
		for cryindex in range(0,len(zutazuta)):
			x1a,y1a,scorea,imgna=zutazuta[cryindex].getInfo()
			bad_index=[0]*len(x1a)
			print "NUMBER OF GRIDS",cryindex,len(x1a)
			# each grid
			for index1 in range(0,len(x1a)):
                        	if bad_index[index1]==1:
                                	continue
				x1=x1a[index1]
				y1=y1a[index1]
				score1=scorea[index1]
				imgnum1=imgna[index1]
				for index2 in range(index1+1,len(x1a)):
                                	print "comparison cry1,cry2=",index1,index2
                                	print "bad_index=",bad_index
                                	if bad_index[index2]==1:
                                        	continue
					x2=x1a[index2]
					y2=y1a[index2]
					score2=scorea[index2]
					imgnum2=imgna[index2]
					dx=x1-x2
					dy=y1-y2
					#print x1,y1,x2,y2,dx,dy
					dist=math.sqrt(dx*dx+dy*dy)
                                	print "distance(%d,%d)=%8.5f mm"%(index1,index2,dist)
					if dist <= vbeam:
						bad_index[index2]=1
				print "BAD",len(bad_index)
			print "Final bad index=",bad_index
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
			print "GOOD points=",ncount
	
		print "SINGLE :",len(single_crystals)
		print "GOOD   :",len(good_crystals)
		print "PERFECT:",len(perfect_crystals)

		# Single crystal
		sss=open("%s/single_new.dat"%raster_path,"w")
		index=0
		for s in single_crystals:
			x1a,y1a=s.getXYlist()
			for x1,y1 in zip(x1a,y1a):
				sss.write("%8.5f %8.5f\n"%(x1,y1))
		sss.close()

		# Perfect OK crystal
		perfile=open("%s/perfect.dat"%raster_path,"w")
		index=0
		for c in check_list:
			if c==0:
				cry=crystals[index]
				x1a,y1a=cry.getXYlist()
				for x1,y1 in zip(x1a,y1a):
					perfile.write("%8.5f %8.5f\n"%(x1,y1))
				perfect_crystals.append(cry)
			index+=1
		perfile.close()

		return single_crystals,good_crystals,perfect_crystals

	# phosec_meas: measured flux or theoretical value
	def mainLoop(self,crystal_list,raster2d_path,hbeam_um,vbeam_um,
				phosec_meas,exptime,distance,total_osc,osc_width,logfile,ntimes=1,reduced_fac=1.0):

		self.sche_str=[]
		cry_index=0
		sw=StopWatch.StopWatch()

		# Angle offset (+)(-) 
		offset_angle=total_osc/2.0

		# Scan angle settings 2017/04/25
		#    Total Oscillation     data collection    centering
		#          45.0 ->      -22.5 -  +22.5 deg   -22.5, +22.5
		#          90.0 ->      -45.0 -  +45.0 deg   -45.0, +45.0
		#         180.0 ->      -90.0 -  +90.0 deg   -90.0, +90.0
		#         270.0 ->     -135.0 - +135.0 deg   -90.0, +90.0
		if total_osc <= 180.0:
			lv_phi=self.phi_face-offset_angle
			rv_phi=self.phi_face+offset_angle
		else:
			lv_phi=self.phi_face-90.0
			rv_phi=self.phi_face+90.0

		print "CRYSTAL LIST=%5d"%len(crystal_list)

		for crystal in crystal_list:
			if cry_index >= self.nCry:
				print "Number of dataset required has been done!"
				break
			try:
				l_pos,r_pos=self.findRoughEdges(crystal,raster2d_path)
			except:
				cry_index+=1
				logfile.write("ERR: crystal size is too small.\n")
				print "Skipping this crystal"
				continue
			start_time=datetime.datetime.now()
			sw.setTime("start")
			crystal_score=crystal.getTotalScore()
			logfile.write(">>>> \n %s\n <<<<<\n"%raster2d_path)
			logfile.write("=== Crystal No. %02d ===  %s\n"%(cry_index,sw.getTime("start")))
			logfile.write("Score of this crystal: %8d\n"%crystal_score)
			logfile.write("Rough left  edge %s\n"%(self.logXYZ(l_pos)))
			logfile.write("Rough right edge %s\n"%(self.logXYZ(r_pos)))

			if l_pos==-999:
				cry_index+=1
				print "Skipping this crystal because grid is one!"
				continue
		
			# L edge scan 2D at face angle
                	scan_id_L="lface-%02d"%cry_index
                        print "L edge horizontal : XYZ=",self.logXYZ(l_pos)
			lras_d=self.faceScan(scan_id_L,l_pos,self.phi_face)
			# R edge scan 2D at face angle
                	scan_id_R="rface-%02d"%cry_index
                        print "R edge horizontal : XYZ=",r_pos
			rras_d=self.faceScan(scan_id_R,r_pos,self.phi_face)

			# Analyze 2D face scan : score threshold is set to 5.0!!
			#def anaFaceScan(self,raster_path,scan_id,cxyz,phi,thresh_nspots=30):
			try:
				Lface=self.anaFaceScan2(lras_d,scan_id_L,l_pos,self.phi_face,thresh_nspots=5)
				Rface=self.anaFaceScan2(rras_d,scan_id_R,r_pos,self.phi_face,thresh_nspots=5)
			except:
				cry_index+=1
				logfile.write("ERR: Failed to find good face points(2D).\n")
				print "Failed to find good 2D face points"
				continue

			lx,ly,lz=Lface
			rx,ry,rz=Rface

			logfile.write("Face  left  edge %s\n"%(self.logXYZ(Lface)))
			logfile.write("Face  right edge %s\n"%(self.logXYZ(Rface)))

			# Final vertical scan5
        		# Left
			scan_id_Lv="lv-fin-%02d"%cry_index

			if math.fabs(offset_angle) > 26.0:
				scan_length=500.0 #[um]
			else:
				scan_length=60.0

			Lv_d=self.finalVscan(scan_id_Lv,Lface,lv_phi,scan_length)

			# Right
			scan_id_Rv="rv-fin-%02d"%cry_index
			Rv_d=self.finalVscan(scan_id_Rv,Rface,rv_phi,scan_length)

			# Conduct vertical scan at start/end oscillation angle
			try:
                		L_fin=self.anaVscan(Lface,lv_phi,Lv_d,scan_id_Lv)
                		R_fin=self.anaVscan(Rface,rv_phi,Rv_d,scan_id_Rv)
			except:
				cry_index+=1
				print "Vertical scan: failed to find good points."
				logfile.write("ERR: Failed to find good vertical points.\n")
				continue

			logfile.write("Final Left  edge %s\n"%(self.logXYZ(L_fin)))
			logfile.write("Final Right edge %s\n"%(self.logXYZ(R_fin)))
			len_hel_vec=self.calcDist(L_fin,R_fin)*1000.0 #[um]
			#logfile.write("Helical vector %8.3f[um]\n"%(len_hel_vec))

			# Make helical schedule file
			prefix="cry%02d"%cry_index

			# Crystal is shorter than 50um
			if len_hel_vec < 50.0: # total osc = 50.0 deg
				start_phi=self.phi_face-offset_angle/2.0
				end_phi=self.phi_face+offset_angle/2.0
			elif len_hel_vec < 20.0: # total osc = 20.0 deg
				start_phi=self.phi_face-10.0
				end_phi=self.phi_face+10.0
			else:
				start_phi=self.phi_face-offset_angle
				end_phi=self.phi_face+offset_angle

			# Photon density limit was set to LoopMeasurement
			# this is not so natural. Someday please fix this part
			logfile.write("HEBI: photon_density_limit=%6.1e [phs/um^2]\n"%self.photon_density_limit)
			self.lm.setPhotonDensityLimit(self.photon_density_limit)

			try:
        			helical_sch=self.lm.genHelical(start_phi,end_phi,osc_width,L_fin,R_fin,
					hbeam_um,vbeam_um,exptime,distance,prefix,phosec_meas,logfile,crystal_id="unknown",
					ntimes=ntimes,reduced_fac=reduced_fac)
                        	self.zoo.doDataCollection(helical_sch)
                        	self.zoo.waitTillReady()
				sw.setTime("end")
				consumed_time=sw.getDsecBtw("start","end")
				logfile.write("Consuming time for this crystal %5.1f[sec]\n"%(consumed_time))
			except:
				logfile.write("ERR: Failed to find crystal.\n")

			logfile.flush()
			cry_index+=1

		#return helical_sch
        # phosec_meas: measured flux or theoretical value
	# ds_index: for avoiding overwriting scanned images
	# This routine does not conduct 'precise' 2D scan for edge detection with small beam
	# but just 'vertical' scans for both edges.
        def roughEdgeHelical(self,crystal_list,raster2d_path,hbeam_um,vbeam_um,
                                phosec_meas,exptime,distance,total_osc,osc_width,logfile,ntimes=1,reduced_fac=1.0,ds_index=0):

                self.sche_str=[]
                cry_index=0
                sw=StopWatch.StopWatch()

		#j#jif total_osc>90.0:
			#jprint "oscillation width for each data should be decreased"
			#jsystem.exit(1)
			
                # Angle offset (+)(-) 
		if total_osc >= 180.0:
                	offset_angle=90.0
		else:
                	offset_angle=total_osc/2.0

                # Scan angle settings 2017/04/25
                #    Total Oscillation     data collection    centering
                #          45.0 ->      -22.5 -  +22.5 deg   -22.5, +22.5
                lv_phi=self.phi_face-offset_angle
                rv_phi=self.phi_face+offset_angle

                logfile.write("CRYSTAL LIST=%5d"%len(crystal_list))

                for crystal in crystal_list:
                        if cry_index >= self.nCry:
                                print "Number of dataset required has been done!"
                                break
                        try:
                                l_pos,r_pos=self.findRoughEdges(crystal,raster2d_path)
                        except:
                                cry_index+=1
                                logfile.write("ERR: crystal size is too small.\n")
                                print "Skipping this crystal"
                                continue
                        start_time=datetime.datetime.now()
                        sw.setTime("start")
                        crystal_score=crystal.getTotalScore()
                        logfile.write(">>>> \n %s\n <<<<<\n"%raster2d_path)
                        logfile.write("=== Crystal No. %02d ===  %s\n"%(cry_index,sw.getTime("start")))
                        logfile.write("Score of this crystal: %8d\n"%crystal_score)
                        logfile.write("Rough left  edge %s\n"%(self.logXYZ(l_pos)))
                        logfile.write("Rough right edge %s\n"%(self.logXYZ(r_pos)))

                        if l_pos==-999:
                                cry_index+=1
                                print "Skipping this crystal because grid is one!"
                                continue

                        # Vertical scan Left edge
                        scan_id_Lv="lv-%02d-%02d"%(ds_index,cry_index)
                        scan_length=50.0

        		#def finalVscanZenbu(self,scan_id,center,phi_start,scanv_um=100.0,hbeam,vbeam):
                        Lv_d=self.finalVscanZenbu(scan_id_Lv,l_pos,lv_phi,scan_length,hbeam_um,vbeam_um)

                        # Right
                        scan_id_Rv="rv-%02d-%02d"%(ds_index,cry_index)
                        Rv_d=self.finalVscanZenbu(scan_id_Rv,r_pos,rv_phi,scan_length,hbeam_um,vbeam_um)

                        # Conduct vertical scan at start/end oscillation angle
                        try:
                                L_fin=self.anaVscan(l_pos,lv_phi,Lv_d,scan_id_Lv)
                                R_fin=self.anaVscan(r_pos,rv_phi,Rv_d,scan_id_Rv)
                        except:
                                cry_index+=1
                                print "Vertical scan: failed to find good points."
                                logfile.write("ERR: Failed to find good vertical points.\n")
                                continue

                        logfile.write("Final Left  edge %s\n"%(self.logXYZ(L_fin)))
                        logfile.write("Final Right edge %s\n"%(self.logXYZ(R_fin)))
                        len_hel_vec=self.calcDist(L_fin,R_fin)*1000.0 #[um]

                        # Make helical schedule file
                        prefix="cry-%02d-%02d"%(ds_index,cry_index)

                        start_phi=self.phi_face-offset_angle
                        end_phi=self.phi_face+offset_angle

                        # Photon density limit was set to LoopMeasurement
                        # this is not so natural. Someday please fix this part
                        logfile.write("HEBI: photon_density_limit=%6.1e [phs/um^2]\n"%self.photon_density_limit)
                        self.lm.setPhotonDensityLimit(self.photon_density_limit)
                        try:
                                helical_sch=self.lm.genHelical(start_phi,end_phi,osc_width,L_fin,R_fin,
                                        hbeam_um,vbeam_um,exptime,distance,prefix,phosec_meas,logfile,crystal_id="unknown",
                                        ntimes=ntimes,reduced_fac=reduced_fac)
                                self.zoo.doDataCollection(helical_sch)
                                self.zoo.waitTillReady()
                                sw.setTime("end")
                                consumed_time=sw.getDsecBtw("start","end")
                                logfile.write("Consuming time for this crystal %5.1f[sec]\n"%(consumed_time))
                        except:
                                logfile.write("ERR: Failed to find crystal.\n")

                        logfile.flush()
                        cry_index+=1


	# phosec_meas: measured flux or theoretical value
	# 2016/12/09 If a single crystal is mounted on the cryo-loop, scan range of vertical scan on 
	# both crystal edges should be longer in order to catch any crystals
	# This function is called in following situations
	# 1) just arter 2D raster scan is finished.
	# 2) gonio phi is still at the 'face angle' where 2D scan is held.
	# *** Rotation range definition in calling this function was removed on 2016/12/09
	# Because this function should center 3D coordinates of both crystal edges correctly for
	# distributing irradiation points on the crystal.
	# Then it should do precise centering at 0, 90 degrees not in 0,45 or something narrower.
	# This property is different from the case for data collection. 
	def findCrystalVector(self,crystal,cry_index,raster2d_path,logfile,isSingle=True):
		self.sche_str=[]
		sw=StopWatch.StopWatch()
		scan_length=500.0 # in [um] for vertical scan

		# From 2D raster scan results, rough positions of both edges were
		# determined.
		try:
			l_pos,r_pos=self.findRoughEdges(crystal,raster2d_path)
		except:
			logfile.write("ERR: crystal size is too small.\n")
			raise MyException.MyException("findCrystalVecotor: Too small.")

		start_time=datetime.datetime.now()
		sw.setTime("start")
		crystal_score=crystal.getTotalScore()
		logfile.write(">>>> \n %s\n <<<<<\n"%raster2d_path)
		logfile.write("=== findCrystalVector ===  %s\n"%(sw.getTime("start")))
		logfile.write("Score of this crystal: %8d\n"%crystal_score)
		logfile.write("Rough left  edge %s\n"%(self.logXYZ(l_pos)))
		logfile.write("Rough right edge %s\n"%(self.logXYZ(r_pos)))

		if l_pos==-999:
			raise MyException.MyException("findCrystalVecotor: L position find failed.")
			return
	
		# L edge scan 2D at face angle
               	scan_id_L="lface-%02d"%cry_index
                print "L edge horizontal : XYZ=",self.logXYZ(l_pos)
		lras_d=self.faceScan(scan_id_L,l_pos,self.phi_face)
		# R edge scan 2D at face angle
               	scan_id_R="rface-%02d"%cry_index
                print "R edge horizontal : XYZ=",r_pos
		rras_d=self.faceScan(scan_id_R,r_pos,self.phi_face)

		# Analyze 2D face scan : score threshold is set to 5.0!!
		#def anaFaceScan(self,raster_path,scan_id,cxyz,phi,thresh_nspots=30):
		try:
			Lface=self.anaFaceScan2(lras_d,scan_id_L,l_pos,self.phi_face,thresh_nspots=5)
			Rface=self.anaFaceScan2(rras_d,scan_id_R,r_pos,self.phi_face,thresh_nspots=5)
		except:
			raise MyException.MyException("findCrystalVecotor: Failed to find good face points")
			return

		lx,ly,lz=Lface
		rx,ry,rz=Rface

		logfile.write("Face left  edge %s\n"%(self.logXYZ(Lface)))
		logfile.write("Face Right edge %s\n"%(self.logXYZ(Rface)))

		# Final vertical scan
		start_phi=self.phi_face-90.0
		# Very long scan length
               	scan_id_Lv="lv-fin-%02d"%cry_index
		Lv_d=self.finalVscan(scan_id_Lv,Lface,start_phi,scan_length)
		end_phi=self.phi_face+90.0

		scan_id_Rv="rv-fin-%02d"%cry_index
		Rv_d=self.finalVscan(scan_id_Rv,Rface,end_phi,scan_length)

		# Conduct vertical scan at start/end oscillation angle
		try:
               		L_fin=self.anaVscan(Lface,start_phi,Lv_d,scan_id_Lv)
               		R_fin=self.anaVscan(Rface,end_phi,Rv_d,scan_id_Rv)
		except:
			raise MyException.MyException("findCrystalVecotor: Vertical scan: failed to find good points.")

		logfile.write("Final Left  edge %s\n"%(self.logXYZ(L_fin)))
		logfile.write("Final Right edge %s\n"%(self.logXYZ(R_fin)))
		len_hel_vec=self.calcDist(L_fin,R_fin)*1000.0 #[um]
		logfile.write("Helical vector %8.3f[um]\n"%(len_hel_vec))

		# Make helical schedule file
		prefix="cry%02d"%cry_index

		return L_fin,R_fin,len_hel_vec

# Iwata root
if __name__ == "__main__":
	import time
	import socket
	import Zoo
	import LoopMeasurement
	import Beamsize
	from html_log_maker import ZooHtmlLog
	import traceback

        sx=0.5925
        sy=-10.5494
        sz=0.1419
        sphi=90.0

        zoo=Zoo.Zoo()
        zoo.connect()
        ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #ms.connect(("192.168.163.1", 10101))
        ms.connect(("172.24.242.41", 10101))

	root_dir="/isilon/users/target/target/Staff/kuntaro/171218-kohebi/test14-CPS1010-07/"
	raster_path="%s/"%root_dir
	
	scan_id="2d"
        lm=LoopMeasurement.LoopMeasurement(ms,root_dir,scan_id)
	cxyz=sx,sy,sz
	hebi=Hebi(zoo,lm,cxyz,sphi,1.0,numCry=100,scan_dist=300.0)

	raster_path="%s/scan/2d/"%root_dir

        hebi.kohebi(raster_path,scan_id,thresh_nspots=20,crysize=0.0151,max_ncry=100)
	#hebi.anaVscan(cxyz,sphi,raster_path,scan_id,thresh_nspots=5,margin=0.005,crysize=0.051,comp_thresh=0.01)

	zoo.disconnect()
	ms.close()
