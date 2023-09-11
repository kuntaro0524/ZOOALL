import sys,os,math,cv2,socket,time
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import Zoo
import LoopMeasurement

if __name__ == "__main__":
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#ms.connect(("192.168.163.1", 10101))
	ms.connect(("172.24.242.41", 10101))

	zoo=Zoo.Zoo()
	zoo.connect()

	skip=True

	# Directory
	root_dir="/isilon/users/target/target/iwata/150723_BL32XU/Auto/"
	if os.path.exists(root_dir):
		continue
	else:
		os.makedirs(root_dir)
	# Experimental conditions
	uname="toyoda"
	beamsize=10.0
	osc_width=0.5
	total_osc=10.0
	exp_henderson=0.7
	exp_time=0.15
	distance=350.0

	for trayid in [2]:
		for pinid in [4]:
			prefix="%s-%02d-%02d"%(uname,trayid,pinid)
			print("Doing %s"%prefix)

			lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)

			lm.prepCentering()
			lm.prepDataCollection()

			# mount
			zoo.getSampleInformation()

			try:
				zoo.mountSample(trayid,pinid)
			except MyException as ttt:
				print("Sample mount failed!!")
				break

			# centering
			lm.centering()

			raster_schedule=lm.prepRaster()
			lm.setBeamsize(beamsize)

			zoo.doRaster(raster_schedule)
			zoo.waitTillReady()

			try:
				glist,phi_mid=lm.shikaTalk()
			except MyException as tttt:
				print("Skipping this loop!!")
				continue

			# Precise centering
			time.sleep(5.0)

			multi_sch=lm.genMultiSchedule(phi_mid,glist,osc_width,total_osc,exp_henderson,exp_time,distance)
			time.sleep(5.0)

			zoo.doDataCollection(multi_sch)
			zoo.waitTillReady()

	zoo.disconnect()
