import sys,os,math,codecs

class ESA:
	def __init__(self,csvfile):
		self.csvfile=csvfile
		self.esalines=[]

		condic={
			"Username":"nyan",
			"DataDire@:"/isilon/users/target/target/AutoUsers/160514/",
			"puck_and_pins":"THU-D05,"1,2,3,4,5,6,7,8,9,10",THU-D06,001-010,THU-D08,"1,2,3,7-16",
			"wavelength":1,
			"h_beam":10,
			"v_beam":15,
			"raster_exp":0.02,
			"osc_width":0.2,
			"total_osc":5,
			"exp_henderson":0.52,
			"exp_time":0.1,
			"istance":320,
			"att_raster":300,
			"shika_minscore":10,
			"shika_mindist":50,
			"shika_maxhits":50,
			"loop_size":"small",
			"offset_angle":20
		}


	def readESAfile(self):
		f=open(sys.argv[1],"r")
		lines=f.readlines()

		#print lines
		for line in lines:
			cols=line.strip().split(",")
			self.esalines.append(cols)
		#print self.esalines

	def readConditions(self):
		for esa in self.esalines:
			print esa

esa=ESA(sys.argv[1])
esa.readESAfile()
esa.readConditions()
