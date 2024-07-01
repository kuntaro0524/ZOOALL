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

	root_dir="/isilon/users/target/target/Staff/ZooTest/"
	beamsize=10.0

	for trayid in [1]:
		for pinid in [8,9,10,11,12,13,14,15,16]:
			prefix="suno%02d-%02d"%(trayid,pinid)
			print "Doing %s"%prefix

			lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)

			lm.prepCentering()
			lm.prepDataCollection()

			# mount
			zoo.getSampleInformation()
			zoo.mountSample(trayid,pinid)
			zoo.waitTillReady()

			# centering
			lm.centering()

			raster_schedule=lm.prepRaster()
			lm.setBeamsize(beamsize)

			zoo.doRaster(raster_schedule)
			zoo.waitTillReady()

			try:
				glist,phi_mid=lm.shikaTalk()
			except MyException, tttt:
				print "Skipping this loop!!"
				continue

			osc_width=1.0
			total_osc=10.0
			exp_henderson=0.5
			exp_time=0.15
			distance=250.0

			time.sleep(5.0)

			multi_sch=lm.genMultiSchedule(phi_mid,glist,osc_width,total_osc,exp_henderson,exp_time,distance)
			time.sleep(5.0)

			zoo.doDataCollection(multi_sch)
			zoo.waitTillReady()

	zoo.disconnect()
