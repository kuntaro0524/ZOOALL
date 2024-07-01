import sys,os,math

class ZooStatus:
	def __init__(self,data_root_dir):
		self.stat_file="%s/.status"%data_root_dir
		self.isOpen=0
                self.status={
                        "mount"		:0,
                        "center"	:0,
                        "raster"	:0
		}

	def read(self):
		self.ofile=open(self.stat_file,"r")
		line=self.ofile.readlines()

	def prep(self):
		self.ofile=open(self.stat_file,"a")

	def finish(self,process):
		self.status[process]=1
		self.ofile=open(self.stat_file,"w")

		for process in ["mount","center","raster"]:
			self.ofile.write("%s %d\n"%(process,self.status[process]))
	
		self.ofile.close()

if __name__ == "__main__":
	zs=ZooStatus("/isilon/users/target/target/Staff/kuntaro/160701/Auto/")
	print zs.status
	zs.finish("center")
	#zs.finish("mount")
	#zs.finish("raster")
