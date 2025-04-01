import sys,os,math,cv2,socket,time
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import Zoo
import LoopMeasurement
from ZooConditions import conditions

if __name__ == "__main__":

	"""
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ms.connect(("192.168.163.1", 10101))

	zoo=Zoo.Zoo()
	zoo.connect()

	#skip=True

	# Directory
	root_dir="/isilon/users/target/target/iwata/150724-BL32XU-Auto/"
	if os.path.exists(root_dir):
		print "%s already exists"%root_dir
	else:
		os.makedirs(root_dir)
	"""
	# Puck number
	puck_list=["1893"]

	# Experimental conditions
	uname="Im"
	beamsize=10.0
	osc_width=1.0
	total_osc=5.0
	exp_henderson=0.7
	exp_time=0.15
	distance=300.0
	# Raster attenuator
	att_raster=500.0 #[um]
	att_idx=int(att_raster/100.0)
	print "ATT INDEX=",att_idx

	# Test of reading conditions from ZooConditions
	condition=conditions['COLLECTION']

	# each parameter setting
	beamsize=condition['BEAM_SIZE']
	osc_width=condition['OSC_WIDTH']
	total_osc=condition['TOTAL_OSC']
	exp_henderson=condition['EXP_HENDERSON']
	exp_time=condition['EXP_TIME']
	distance=condition['DISTANCE']
	att_raster=condition['ATT_RASTER']

	print beamsize,osc_width,total_osc,exp_henderson,exp_time,distance,att_raster


"""
	for trayid in puck_list:
		for pinid in np.arange(1,17):
		#for pinid in [11,12,13,14,15,16]:
			prefix="%s-%s-%02d"%(uname,trayid,pinid)
			print "Doing %s"%prefix

			lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)

			lm.prepCentering()
			lm.prepDataCollection()

			# mount
			zoo.getSampleInformation()

			try:
				zoo.mountSample(trayid,pinid)
			except MyException,ttt:
				print "Sample mount failed!!"
				break

			# centering
			lm.centering()

			raster_schedule=lm.prepRaster(att_idx=att_idx)
			lm.setBeamsize(beamsize)

			zoo.doRaster(raster_schedule)
			zoo.waitTillReady()

			try:
				glist,phi_mid=lm.shikaTalk()
			except MyException, tttt:
				print "Skipping this loop!!"
				continue

			# Precise centering
			time.sleep(5.0)
			multi_sch=lm.genMultiSchedule(phi_mid,glist,osc_width,total_osc,exp_henderson,exp_time,distance)
			time.sleep(5.0)

			zoo.doDataCollection(multi_sch)
			zoo.waitTillReady()

			if pinid%7==0:
				zoo.cleaning()
				zoo.waitTillReady()
	zoo.disconnect()
"""
