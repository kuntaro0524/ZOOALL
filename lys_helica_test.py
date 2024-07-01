import sys,math,numpy,os
import LoopMeasurement
import Zoo
import AttFactor
import AnaShika
import Condition
import Hebi

conditions = [
              Condition.Condition(uname="lys2",
                        pucks_and_pins=[
                                        ["CPS1005", [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                       ],
                        h_beam=8.5, #[um square shaped]
                        v_beam=18.0, #[um square shaped]
                        raster_exp=0.02, # [sec.] normally 0.02sec
                        osc_width=0.1, #[deg.]
                        total_osc=100.0, #[deg.]
                        exp_henderson=0.05, #[sec] DUMMY
                        exp_time=0.05, #Fixed value
                        distance=120.0, #[mm]
                        att_raster=1000.0, #[um] # Raster attenuator
                        shika_minscore=15,
                        shika_mindist=0,
                        loop_size="large",
			helical_hbeam=2.0,
                        helical_vbeam=18.0,
			phosec=2.5E12,
                        ntimes=1,
              ),
              ]

# Iwata root
root_dir="/isilon/users/target/target/Staff/kuntaro/160921/"

if __name__ == "__main__":

	import time
	import socket
	import Zoo
	import LoopMeasurement
	import Beamsize
	from html_log_maker import ZooHtmlLog
	import traceback

        # Gonio mount position
        # sx,sy,sz are for quick automatic centering
        # the values are replaced by that of previous sample
        # position. But initially 'Cmount position' is used
        sx=-0.0762
        sy=-10.27
        sz=0.35
        sphi=177

        ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #ms.connect(("192.168.163.1", 10101))
        ms.connect(("172.24.242.41", 10101))

        zoo=Zoo.Zoo()
        zoo.connect()

	## MAIN
	def check_abort(lm):
        	print "Abort check"
        	ret = lm.isAbort()
        	if ret: print "ABORTABORT"
        	return ret
	# check_abort()

       	if os.path.exists(root_dir):
               	print "%s already exists"%root_dir
       	else:
               	os.makedirs(root_dir)

	name="kuntaro"
       	open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s\n"%(name,root_dir))
       	html_maker = ZooHtmlLog(root_dir, name, online=True)

       	config_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
       	config_file="%s/bss/bss.config"%config_dir
       	att_fact=AttFactor.AttFactor(config_file)

       	for cond in conditions:
               	att_idx=att_fact.getAttIndexConfig(cond.att_raster)

               	# 2015/11/21 K.Hirata added
               	# beam size is changed for each condition
               	bsc=Beamsize.Beamsize(ms,config_dir)
               	bsc.changeBeamsizeHV(cond.h_beam,cond.v_beam)
	
               	try: html_maker.add_condition(cond)
               	except: print traceback.format_exc()
	
               	for trayid, pin_list in cond.pucks_and_pins:
                       	for pinid in pin_list:
                               	prefix="%s-%s-%02d"%(cond.uname,trayid,pinid)
                               	print "Doing %s"%prefix

                               	lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
				
				# pin_path
				pin_path="%s/%s/"%(root_dir,prefix)

                               	if check_abort(lm): break # Abort check

                               	lm.prepCentering()
                               	lm.prepDataCollection()
                               	lm.setBeamsize(cond.h_beam,cond.v_beam)
                               	lm.setWavelength(1.0000)

                               	# mount
                               	zoo.getSampleInformation()
                               	time.sleep(5.0)
                               	try:
                                       	zoo.mountSample(trayid,pinid)
                               	except MyException,ttt:
                                       	print "Sample mount failed!!"
                                       	break

                               	# Move Gonio XYZ to the previous pin
                               	lm.moveGXYZphi(sx,sy,sz,sphi)

                               	# centering
                               	# 2015/11/21 Loop size can be set
                               	try:
                                       	# rwidth:  Horizontal scan range [um]
                                       	# rheight: Vertical   scan range [um]
                                       	rwidth,rheight=lm.centering(cond.loop_size)
                               	except MyException,ttt:
                                       	print "failed in centering"
                                       	print "Go to next sampl,e"
                                       	continue

                               	# Save Gonio XYZ to the previous pins
				print rwidth,rheight
                               	sx,sy,sz,sphi=lm.saveGXYZphi()

                                if check_abort(lm): break # Abort check

                                # Initial 2D scan 
                                scan_id="2d"
                                gxyz=sx,sy,sz
                                # Scan step is set to the same to the beam size
                                # Experimental settings
                                scan_mode="2D"
                                scanv_um=rheight
                                scanh_um=rwidth
                                vstep_um=cond.v_beam
                                hstep_um=cond.h_beam

                                schfile,raspath=lm.rasterMaster(scan_id,scan_mode,cond.v_beam,cond.h_beam,scanv_um,
                                        scanh_um,vstep_um,hstep_um,gxyz,sphi,att_idx=att_idx,distance=cond.distance,exptime=0.02)

                                # Do 2D raster
                                zoo.doRaster(schfile)
                                zoo.waitTillReady()

				# Hebi instance
				hebi=Hebi.Hebi(zoo,lm,gxyz,sphi)

                                # Distance for searching near grids
                                if cond.h_beam > cond.v_beam:
                                        crysize=(cond.h_beam+1.000)/1000.0 # [mm]
                                else:
                                        crysize=(cond.v_beam+1.000)/1000.0 # [mm]
                                print "Crystal size is set to %8.2f[mm]"%crysize

                                raster_path="%s/%s/scan/%s/"%(root_dir,prefix,scan_id)

				cxyz=sx,sy,sz
        			#def getCrystals(self,raster_path,scan_id,thresh_nspots=30,crysize=0.10,max_ncry=50):
				crystal_list=hebi.getCrystals(raspath,scan_id,thresh_nspots=cond.shika_minscore,crysize=crysize,max_ncry=10)
				# hbeam_um, vbeam_um : helical beam size
				# phosec: photon flux of this beam size
				# exptime: exposure time for each frame
				# distance: camera distance

        			hebi.mainLoop(crystal_list,raspath,cond.helical_hbeam, cond.helical_vbeam,
					cond.phosec,cond.exp_time,cond.distance,cond.total_osc,cond.osc_width)

	zoo.disconnect()
	ms.close()
