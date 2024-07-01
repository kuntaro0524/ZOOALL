from GonioVec import *

# 2013/10/11 K.Hirata
# MX225HS readout mode is different from MX225HE
# MX225HS
# 0: Normal
# 1: High gain
# 2: Low noise
# 3: High dynamic

# 2014/05/14 K.Hirata
# MX225HS readout mode is different from MX225HE
# MX225HS
# 0: Normal
# 1: High gain
# 2: Low noise
# 3: High dynamic
# The mode should be '0' for fast-data acquisition

# 2015/12/19 Tranlated to here for Zoo
# 2016/06/03 Crystal ID for KAMO

class ScheduleBSS_HS:
#class ScheduleBSS:

	def __init__(self):
		self.dir="~/"
		self.dataname="test"
		self.crystal_id="unknown"
		self.offset=0
		self.exptime=1.0
		self.wavelength=1.0
		self.startphi=0.0
		self.endphi=90.0
		self.stepphi=1.0
		self.cl=200.0
		self.att_index=0
		self.isAdvanced=0
		self.npoints=1
		self.astep=0
		self.ainterval=1
		self.scan_interval=1
		self.beamsize_idx=0
		self.x1=1.0
		self.y1=1.0
		self.z1=1.0
		self.x2=1.0
		self.y2=1.0
		self.z2=1.0
		self.isSlow=False
		self.isReadBeamSize=False

	def setDir(self,dir):
		self.dir=dir
	def setCrystalID(self,crystal_id):
		self.crystal_id=crystal_id
	def setDataName(self,dataname):
		self.dataname=dataname
	def setOffset(self,offset):
		self.offset=offset
	def setExpTime(self,exptime):
		self.exptime=exptime
	def setWL(self,wavelength):
		self.wavelength=wavelength
	def setScanCondition(self,startphi,endphi,stepphi):
		self.startphi=startphi
		self.endphi=endphi
		self.stepphi=stepphi
	def setCameraLength(self,cl):
		self.cl=cl
	def setAttIdx(self,index):
		self.att_index=index
	def setAttThickness(self,thickness):
		# thickness [um]
        	self.att_index=self.getAttIndex(thickness)
	def setScanInt(self,scan_interval):
		self.scan_interval=scan_interval
	def setSlowOn(self):
		self.isSlow=True
	def stepAdvanced(self,startvec,endvec,astep,ainterval,startphi,stepphi,interval):
		self.astep=astep/1000.0 # [mm]
		self.ainterval=ainterval
		self.scan_interval=interval
		self.setAdvancedVector(startvec,endvec)
		# calculation of vector length
		gv=GonioVec()
		lvec=gv.makeLineVec(startvec,endvec)
		length=gv.calcDist(lvec)*1000.0
		print length
		# npoints
		self.npoints=int(length/astep)
		self.isAdvanced=1
		# rotation
		self.stepphi=stepphi
		self.startphi=startphi
		# end phi
		self.endphi=self.startphi+self.stepphi*self.npoints*ainterval*self.scan_interval

	def setAdvanced(self,npoints,astep,ainterval):
		self.npoints=npoints
		self.astep=astep
		self.ainterval=ainterval
		self.isAdvanced=1

	def setAdvancedVector(self,start,end):
		self.x1=float(start[0])
		self.y1=float(start[1])
		self.z1=float(start[2])
		self.x2=float(end[0])
		self.y2=float(end[1])
		self.z2=float(end[2])

	def make(self,sch_file):
		# Firstly remove the 'sch_file'
		#command="/bin/rm -f %s"%sch_file
		#print command
		#os.system(command)

		ofile=open(sch_file,"w")

		ofile.write("Job ID: 0\n")
		ofile.write("Status: 0 # -1:Undefined  0:Waiting  1:Processing  2:Success  3:Killed  4:Failure  5:Stopped  6:Skip  7:Pause\n")
		ofile.write("Job Mode: 0 # 0:Check  1:XAFS  2:Single  3:Multi\n")
		ofile.write("Crystal ID: %s\n"%self.crystal_id)
		ofile.write("Tray ID: Not Used\n")
		ofile.write("Well ID: 0 # 0:Not Used\n")
		ofile.write("Cleaning after mount: 0 # 0:no clean, 1:clean\n")
		ofile.write("Not dismount: 0 # 0:dismount, 1:not dismount\n")
		ofile.write("Data Directory: %s\n"%self.dir)
		ofile.write("Sample Name: %s\n"%self.dataname)
		ofile.write("Serial Offset: %5d\n"%self.offset)
		ofile.write("Number of Wavelengths: 1\n")
		ofile.write("Exposure Time: %8.2f 1.000000 1.000000 1.000000 # [sec]\n"%self.exptime)
		ofile.write("Direct XY: 2000.000000 2000.000000 # [pixel]\n")
		ofile.write("Wavelength: %8.4f 1.020000 1.040000 1.060000 # [Angstrom]\n"%self.wavelength)
		ofile.write("Centering: 3 # 0:Database  1:Manual  2:Auto  3:None\n")
		ofile.write("Detector: 0 # 0:CCD  1:IP\n")
		ofile.write("Scan Condition: %8.2f %8.2f %8.2f  # from to step [deg]\n"%(self.startphi,self.endphi,self.stepphi))
		ofile.write("Shutterless measurement: 1 # 0:no, 1:yes\n")
		ofile.write("Scan interval: %5d  # [points]\n"%self.scan_interval)
		ofile.write("Wedge number: 1  # [points]\n")
		ofile.write("Wedged MAD: 1  #0: No   1:Yes\n")
		ofile.write("Start Image Number: 1\n")
		ofile.write("Goniometer: 0.00000 0.00000 0.00000 0.00000 0.00000 #Phi Kappa [deg], X Y Z [mm]\n")
		ofile.write("CCD 2theta: 0.000000  # [deg]\n")
		ofile.write("Detector offset: 0.0 0.0  # [mm] Ver. Hor.\n")
		ofile.write("Camera Length: %8.3f  # [mm]\n"%self.cl)
		#ofile.write("Beamstop position: 20.000000  # [mm]\n")
		ofile.write("IP read mode: 1  # 0:Single  1:Twin\n")
		#ofile.write("DIP readout diameter: 400.000000  # [mm]\n")
		ofile.write("CMOS frame rate: 3.000000  # [frame/s]\n")
		ofile.write("CCD Binning: 2  # 1:1x1  2:2x2\n")

		if self.isSlow==True:
			ofile.write("CCD Adc: 1  # 0:Standard 1:High Gain 2:Low noise 3:Do not use (select Slow)\n")
		else :
			ofile.write("CCD Adc: 0  # 0:Normal  1:High gain 2:Low noise 3:Do not use (select Normal)\n")

		ofile.write("CCD Transform: 1  # 0:None  1:Do\n")
		ofile.write("CCD Dark: 1  # 0:None  1:Measure\n")
		ofile.write("CCD Trigger: 0  # 0:No  1:Yes\n")
		ofile.write("CCD Dezinger: 0  # 0:No  1:Yes\n")
		ofile.write("CCD Subtract: 1  # 0:No  1:Yes\n")
		ofile.write("CCD Thumbnail: 0  # 0:No  1:Yes\n")
		ofile.write("CCD Data Format: 0  # 0:d*DTRK  1:RAXIS\n")
		ofile.write("Oscillation delay: 100.000000  # [msec]\n")
		ofile.write("Anomalous Nuclei: Mn  # Mn-K\n")
		ofile.write("XAFS Mode: 0  # 0:Final  1:Fine  2:Coarse  3:Manual\n")
		ofile.write("Attenuator: %5d\n"%self.att_index)
		ofile.write("XAFS Condition: 1.891430 1.901430 0.000100  # from to step [A]\n")
		ofile.write("XAFS Count time: 1.000000  # [sec]\n")
		ofile.write("XAFS Wait time: 30  # [msec]\n")
		ofile.write("Transfer HTPFDB: 0  # 0:No, 1:Yes\n")
		ofile.write("Number of Save PPM: 0\n")
		ofile.write("Number of Load PPM: 0\n")
		ofile.write("PPM save directory: /tmp\n")
		ofile.write("PPM load directory: /tmp\n")
		ofile.write("Advanced mode: %d # 0: none, 1: vector centering, 2: multiple centering\n"%self.isAdvanced)
		ofile.write("Advanced vector centering type: 1 # 0: set step, 1: auto step, 2: gradual move\n")
		ofile.write("Advanced npoint: %d # [mm]\n"%self.npoints)
		ofile.write("Advanced step: %8.4f # [mm]\n"%self.astep)
		ofile.write("Advanced interval: %d # [frames]\n"%self.ainterval)
		ofile.write("Advanced gonio coordinates 1: %12.5f %12.5f %12.5f # id, x, y, z\n"%(self.x1,self.y1,self.z1))
		ofile.write("Advanced gonio coordinates 2: %12.5f %12.5f %12.5f # id, x, y, z\n"%(self.x2,self.y2,self.z2))
		ofile.write("Comment:  \n")

		ofile.close()

	def readBeamSizeConf(self):
		config="/blconfig/bss/beamsize.config"
		ifile=open(config,"r")
		lines=ifile.readlines()
		ifile.close()
		#print lines

		self.beamsize_list=[]
		flag=False
		idx=0
		for line in lines:
			cols=line.split()
			if len(cols)==0:
				#print "kara",line
				continue
			if cols[0]=="_beam_size_begin:":
				flag=True
				idx+=1
				continue
			if flag==True and cols[0]=="_beam_size_end:":
				size_info=beam_h,beam_v,tcs_h,tcs_v
				self.beamsize_list.append(size_info)
				flag=False
				continue
			if flag==True:
				#print idx,line
				if cols[0].find("_label:")!=-1:
					beam_h=float(cols[2])
					beam_v=float(cols[5])
				if line.find("_object_parameter: tc1_slit_1_width")!=-1:
					tcs_h=float(cols[2])
				if line.find("_object_parameter: tc1_slit_1_height")!=-1:
					tcs_v=float(cols[2])

		#print self.beamsize_list
		self.isReadBeamSize=True

	def setBeamSizeHV(self,beamh,beamv):
		if self.isReadBeamSize==False:
			self.readBeamSizeConf()

		idx=1
		for size in self.beamsize_list:
			hsize=size[0]
			vsize=size[1]
			if hsize==beamh and vsize==beamv:
				self.beamsize_idx=idx
				break
			else:
				idx+=1
				continue

		if self.beamsize_idx==0:
			print "Aimed beam size was not found in beamsize.config"
		return self.beamsize_idx

#_beam_size_begin:
#_label: [h 1.00 x  v 10.00 um]
#_outline: [rectangle 0.0010 0.0100 0.0 0.0 ]
#_object_parameter: tc1_slit_1_width 0.040 mm
#_object_parameter: tc1_slit_1_height 0.5 mm
#_flux_factor: 1.000
#_beam_size_end:

if __name__=="__main__":
	t=ScheduleBSS()
	adstep=2.0

	#startphi=0.0
	#stepphi=1.0
	#interval=1

	#print "DIR THICKNESS SX SY SZ EX EY EZ"
	#ovec=(float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]))
	#vvec=(float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8]))
	#hvec=(float(sys.argv[9]),float(sys.argv[10]),float(sys.argv[11]))

	#for i in range(0,5):
		#t.setDir(sys.argv[1])
		#t.setCameraLength(120)
		#t.setAttThickness(600)
		#t.stepAdvanced(svec,evec,adstep,1,startphi,stepphi,interval)
		#t.setDataName("low_%02d"%i)
		#t.make("tmp1%02d.sch"%i)

	#print t.setBeamSizeHV(1,10)
        #def makeMultiPos(self,schfile,cencode,beam_h,beam_v):
	print t.makeMultiPos("test.sch",[0,0,0],1,10)
