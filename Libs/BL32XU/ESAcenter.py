import os,sys,math

class Experiment:
	def __init__(self):
		self.username="hirata"
		self.root_dir="/isilon/users/target/target/Staff/2016A/160524/"
	def setUserName(self,username):
		self.username=username
	def setRootDir(self,root_dir):
		self.root_dir=root_dir

class PuckPin:
	def __init__(self,puckid):
		self.puckid=puckid
		self.pins=[]
		self.colflag=[]
		self.isInit=False

	def init(self):
		dummy_es=ExpSetting()
		for i in range(0,17):
			self.pins.append(dummy_es)
			self.colflag.append(False)
		self.isInit=True

	def setPin(self,pin_id,es):
		apparent_pinid=pin_id
		if self.isInit==False: self.init()
		self.pins[pin_id]=es
		self.colflag[pin_id]=True

	def getAllPins(self):
		pin_list=[]
		for i in range(0,17):
			pin=self.pins[i]
			colflag=self.colflag[i]
			if colflag==True:
				pin_list.append((i,pin.esadic))
		return pin_list

	def printAllPins(self):
		for i in range(0,17):
			pin=self.pins[i]
			colflag=self.colflag[i]
			if colflag==True:
				print i,colflag,pin.esadic

class ExpSetting:
	def __init__(self):
		# Setting default values
		self.esadic={
			"mode":"multi",			# "multi", "single", "helical", "ssrox"
			"Username":"kuntaro",		# user name
			"collection_name":"DUM",	# data collection name for report
			"rootdir":"/isilon",		# root directory
			"sample_name":"sample",		# sample name
			"wavelength":1.00000,		# [angstrome]
			"h_beam_raster":10.0,		# horizontal beam size [um] raster scan
			"v_beam_raster":15.0,		# vertical beam size [um] raster scan
			"h_beam_dc":10.0,		# horizontal beam size [um] data collection
			"v_beam_dc":15.0,		# vertical beam size [um] data collection
			"raster_exp":0.02,		# raster scan exposure time [sec]
			"osc_width":0.2,		# oscillation width [deg.]
			"total_osc":5.0,		# total oscillation of each crystal [deg.]
			"dose_limit":10.0,		# Dose limit for data collection [MGy]
			"exp_time":0.1,			# exposure time [sec]
			"distance":320.0,		# camera distance[mm]
			"att_raster":50.0,		# Transmission at raster scan [%]
			"shika_minscore":10,		# SHIKA score for crystal findings [spots]
			"shika_mindist":50.0,		# SHIKA crystal size [um]
			"shika_maxhits":50,		# SHIKA maximum number of datasets [datasets]
		       	"n_times":1,			# N times for dose slicing
		       	"reduced_fac":1.0,		# Reduced factor compared to the dose_limit
			"loop_size":"small",		# "small","large","smaller"
			"offset_angle":0.0		# [angstrome]
		}

	def convertDic2Param(self):
		for key in  self.esadic.keys():
			print key,self.esadic[key]
                        setattr(self, key, self.esadic[key])
		
	def checkCondition(self):
		# For multi crystal strategies
		if self.esadic["mode"]=="multi":
			print "MULTI"

	def setShikaParam(self,shika_minscore,shika_mindist,shika_maxhits):
		self.esadic["shika_minscore"]=shika_minscore
		self.esadic["shika_mindist"]=shika_mindist
		self.esadic["shika_maxhits"]=shika_maxhits

	def setRotation(self,osc_width,osc_range):
		self.esadic["osc_width"]=osc_width
		self.esadic["osc_range"]=total_osc

	def setExpTime(self,raster_exp,exp_frame,dose_limit):
		self.esadic["raster_exp"]=raster_exp
		self.esadic["exp_time"]=exp_frame
		self.esadic["exp_henderson"]=exp_limit

	def setParam(self,key,value):
		print "SONOMAMA",key,value
		if value.replace(".","").isdigit()==True:
			fvalue=float(value)
			self.esadic[key]=fvalue
			print "FLOAT VALUE:",key,fvalue
		else:
			self.esadic[key]=value

	def showParam(self):
		print self.esadic

class ESA:
	def __init__(self,esafile):
		self.esafile=esafile
		self.ex=Experiment()
		self.cond=ExpSetting()
			
		self.initFlag=False

	def init(self):
		# ESA reading
		lines=open(self.esafile,"r").readlines()

		# Convertion kaigyou for MAC excel sheet
		new_lines=[]
		if len(lines)==1:
    			for line in lines:
        			tmp_line=line.replace("\r","\n")
        			new_lines=tmp_line.split("\n")
		else:
    			new_lines=lines

		self.lines=new_lines

		self.initFlag=True
		pplist=[]

	def setPuckCondition(self,line,cond):
		line1=line.strip().replace("\"","")
		cols=line1.split(",")
		puckid=cols[1]
	
		#print "COLS:",cols

		puck=PuckPin(puckid)
		for i in range(2,len(cols)):
			if cols[i]=="":
				#print "BREAK",cols[i]
				continue
			if cols[i].rfind("-")!=-1:
				cols_sub=cols[i].split("-")
				#print "SUB",cols_sub
				first_pin=int(cols_sub[0])
				end_pin=int(cols_sub[1])+1
				#print first_pin,end_pin
				for j in range(first_pin,end_pin):
					pinid=j
					puck.setPin(pinid,cond)
			else:
				#print i,cols[i]
				#puck.addCondition(pinlist,cond)
				pinid=int(cols[i])
				puck.setPin(pinid,cond)
		#puck.printAllPins()
		return puck

	def readESA(self):
		cond=ExpSetting()

		if self.initFlag==False:
			self.init()
		puck_list=[]
		
		for line in self.lines:
			cols=line.strip().split(",")
			cond.setParam(cols[0],cols[1])
			if line.rfind("puck_and_pins")!=-1:
				puck_list.append(self.setPuckCondition(line,cond))
		
		for p in puck_list:
			pin_conds=p.getAllPins()
			for cond in pin_conds:
				pinid,each_conds=cond

		return puck_list

if __name__=="__main__":
	esa=ESA(sys.argv[1])
	pucks=esa.readESA()

	#print pucks
	#pucks[0].pins[1].convertDic2List()

	ppp=pucks[0].pins[1]
	ppp.convertDic2List()

	#for puck in pucks:
		#for pinid in range(1,17):
			##print puck.puckid
			##if puck.colflag[pinid]==True:
				#print puck.puckid,puck.pins[pinid].esadic["Username"],puck.pins[pinid].esadic["exp_time"]
			#print puck.colflag
