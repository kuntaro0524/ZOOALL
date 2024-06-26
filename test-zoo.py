import sys,os,math,cv2,socket,time,copy
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
from MyException import * 
import Zoo
import LoopMeasurement
import Beamsize

class Condition:
	def __init__(self, uname, pucks_and_pins, h_beam, v_beam, raster_exp, osc_width, total_osc, exp_henderson, exp_time, distance, att_raster, shika_minscore, shika_mindist, loop_size):
		# adopt init args
		for k, v in locals().items():
			if k == "self": continue
			setattr(self, k, v)

		self._check_errors()
	# __init__()

	def _check_errors(self):
		prohibit_chars = set(" /_*")
		assert not prohibit_chars.intersection(self.uname)

		assert type(self.pucks_and_pins) == list
		assert all(map(lambda x: len(x)==2, self.pucks_and_pins))
		for puck, pins in self.pucks_and_pins:
			assert type(puck) == str
			assert not prohibit_chars.intersection(puck)
			assert all(map(lambda x: 1 <= x <= 16, pins))
	# _check_errors()

	def customized_copy(self, **kwds):
		c = copy.copy(self)
		for k, v in kwds.items():
			assert hasattr(c, k)
			setattr(c, k, v)
		self._check_errors()
		return c
	# customized_copy()

	def make_shika_direction(self, scandir):
		ofs = open(os.path.join(scandir, "shika_auto.config"), "w")
		if self.shika_minscore is not None: ofs.write("min_score= %.3f\n" % self.shika_minscore)
		if self.shika_mindist is not None: ofs.write("min_dist= %.3f\n" % self.shika_mindist)
		ofs.close()
	# make_shika_direction()
		
# class Condition
		

def check_abort(lm):
	print "Abort check"
	ret = lm.isAbort()
	if ret: print "ABORTABORT"
	return ret
# check_abort()

def run(zoo, ms, root_dir, name, sx, sy, sz, sphi, conditions):
	if os.path.exists(root_dir):
		print "%s already exists"%root_dir
	else:
		os.makedirs(root_dir)

	open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s\n"%(name,root_dir))

	for cond in conditions:
		att_idx=int(cond.att_raster/100.0)

		# 2015/11/21 K.Hirata added
		# beam size is changed for each condition
		config_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
		bsc=Beamsize.Beamsize(ms,config_dir)
		bsc.changeBeamsizeHV(cond.h_beam,cond.v_beam)
	
		for trayid, pin_list in cond.pucks_and_pins:
			for pinid in pin_list:
				prefix="%s-%s-%02d"%(cond.uname,trayid,pinid)
				print "Doing %s"%prefix

				lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)

				if check_abort(lm): return # Abort check
	
				lm.prepCentering()
				lm.prepDataCollection()
				lm.setBeamsize(cond.h_beam,cond.v_beam)
	
				cond.make_shika_direction(lm.raster_dir)

				# mount
				#zoo.getSampleInformation()
	
				#try:
					#zoo.mountSample(trayid,pinid)
				#except MyException,ttt:
					#print "Sample mount failed!!"
					#break
	
				# Move Gonio XYZ to the previous pin
				lm.moveGXYZphi(sx,sy,sz,0.0)
	
				# centering
				# 2015/11/21 Loop size can be set
				try:
					lm.centering(cond.loop_size)
				except MyException,ttt:
					print "failed in centering"
					print "Go to next sampl,e"
					continue
	
				# Save Gonio XYZ to the previous pin
				sx,sy,sz,sphi=lm.saveGXYZphi()
	
				# Capture the crystal image before experiment
				capture_name="before.ppm"
				lm.captureImage(capture_name)

				if check_abort(lm): return # Abort check
	
				raster_schedule=lm.prepRaster(dist=cond.distance,att_idx=att_idx,exptime=cond.raster_exp)
	
				zoo.doRaster(raster_schedule)
				zoo.waitTillReady()
	
				try:
					glist,phi_mid=lm.shikaTalk()
				except MyException, tttt:
					print "Skipping this loop!!"
					continue
	
				if check_abort(lm): return # Abort check

				# Precise centering
				time.sleep(5.0)
				multi_sch=lm.genMultiSchedule(phi_mid,glist,cond.osc_width,cond.total_osc,cond.exp_henderson,cond.exp_time,cond.distance)
				time.sleep(5.0)
	
				zoo.doDataCollection(multi_sch)
				zoo.waitTillReady()
	
				# Rotate phi to the scan angle to capture the image
				lm.moveGXYZphi(sx,sy,sz,sphi)
				# Capture the crystal image after experiment
				capture_name="after.ppm"
				lm.captureImage(capture_name)
	
				if pinid%6==0:
					zoo.cleaning()
					zoo.waitTillReady()

				if check_abort(lm): return # Abort check


	open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s finished\n"%(name,root_dir))
# run()

if __name__ == "__main__":
	# Gonio mount position
	# sx,sy,sz are for quick automatic centering
	# the values are replaced by that of previous sample
	# position. But initially 'Cmount position' is used
	sx=0.9212
	sy=-0.2383
	sz=-0.0551
	sphi=0.0
	
	# Puck number
	conditions = [Condition(uname="zoo-test2", 
				pucks_and_pins=[["1", range(1,2)],
				],
	                        h_beam=10.0, #[um square shaped]
	                        v_beam=18.0, #[um square shaped]
				raster_exp=0.02, # [sec.] normally 0.02sec
	                        osc_width=1.0, #[deg.]
	                        total_osc=10.0, #[deg.]
	                        exp_henderson=0.5, #[sec]
	                        exp_time=0.2, #Fixed value
	                        distance=150.0, #[mm]
	                        att_raster=1500.0, #[um] # Raster attenuator
	                        shika_minscore=100,
	                        shika_mindist=300,
                                loop_size="small",
	              ),
	              ]

	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ms.connect(("192.168.163.1", 10101))

	zoo=Zoo.Zoo()
	zoo.connect()

	# Nureki root
        nureki_root="/isilon/users/target/target/Staff/2015B/151125/09.TestZoo/"

	run(zoo, ms,
            root_dir=nureki_root,
	    name="151126-zoo-check",
	    sx=sx, sy=sy, sz=sz, sphi=sphi, conditions=conditions)

	zoo.disconnect()
	ms.close()
