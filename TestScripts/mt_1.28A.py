import socket
import time
import datetime

# My library
import Morning

def time_now():
	strtime=datetime.datetime.now().strftime("%H:%M:%S")
	return strtime

def date_now():
	strtime=datetime.datetime.now().strftime("%Y%m%d-%H%M")
	return strtime

if __name__=="__main__":
	mng=Morning.Morning("./")

	# Beam position log
	bplogname="/isilon/BL32XU/BLsoft/Logs/beam.log"
	bplog=open(bplogname,"aw")

	# Morning log file
	tstr=datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
	fname="MT_%s.dat"%tstr
	logf=open(fname,"w")

	# FLAGS (All flags should be true)
	# ALL True
	DTTUNE=NEEDLE_X=NEEDLE_ZZ=COAX_Z=TUNE_ZZ=EVACUATE_NEEDLE=True
	PREP_BC=WAIT=STYTUNE=COLLISCAN=MEAS_FLUX=True

	# Comment out if you would like to skip the process
	#DTTUNE=False
	#NEEDLE_X=False
	#NEEDLE_ZZ=False
	#COAX_Z=False
	#TUNE_ZZ=False
	#EVACUATE_NEEDLE=False
	#PREP_BC=False
	#WAIT=False
	#STYTUNE=False
	#COLLISCAN=False
	#MEAS_FLUX=False

	if DTTUNE==True:
		# dttune
		mng.changeE(9.68625)
		dttune_fwhm,dttune_center=mng.dttunePeak()
		logf.write("%10s %10s FWHM: %8.2f pls Center: %8.2f pls\n"%(time_now(),"DTTUNE",dttune_fwhm,dttune_center))
		logf.flush()

	if NEEDLE_X==True:
		# Needle X-ray center
		mng.prepScan()
		cx,cy,cz=mng.needleXcenter()
		logf.write("%10s %10s Gonio-Enc(XYZ)=%10.4f%10.4f%10.4f\n"%(time_now(),"N-XCEN",cx,cy,cz))
		logf.flush()

	if NEEDLE_ZZ==True:
		# Needle ZZ X-ray center
		curr_zz,fin_zz=mng.scanZZneedleX()
		d_zz=0.5*(fin_zz-curr_zz) #[um]
		logf.write("%10s %10s %10d%10d Diff=%10.4f[um]\n"%(time_now(),"ZZ-CEN",curr_zz,fin_zz,d_zz))
		logf.flush()

	if COAX_Z==True:
		# Coax Z center with needle capture
		ini_coz,fin_coz=mng.tuneCoaxZ(2)
		d_coz=0.5*(fin_coz-ini_coz) #[um]
		logf.write("%10s %10s %10d%10d Diff=%10.4f[um]\n"%(time_now(),"Coax-Z",ini_coz,fin_coz,d_coz))

	if TUNE_ZZ==True and NEEDLE_ZZ==True:
		# ZZ center & Coax Z center difference
		diff=d_coz-d_zz
		logf.write("Difference of movement of ZZ & CoaxZ = %10.4f[um] (from coax Z)\n"%diff)
		logf.flush()

	if EVACUATE_NEEDLE==True:
		#######################
		# Evacuate needle
		#######################
		sx,sy,sz=mng.evacNeedle(15)

	if PREP_BC==True:
		# Scintillator set position
		mng.prepBC()
		# Attenuator 1000um for 12.3984 keV 0.1 mm TCS apert
		mng.setAtt(1000)

	if WAIT==True:
		#######################
		# Wait for 180 sec
		#######################
		print("Waiting for thermal equilibrium of scintillator stage")
		time.sleep(60.0)

	if STYTUNE==True:
		# Open shutter
		mng.prepScan()

		# ST-Y tune
        	sty_curr,sty_tuned=mng.stageYtuneCapture()
		d_sty=(sty_tuned-sty_curr)*1000.0 #[um]
		logf.write("%10s %10s PREV=%9.4f CURR=%9.4f Diff=%10.4f[um]\n"%(time_now(),"St-y",sty_curr,sty_tuned,d_sty))
		logf.flush()

        	#def doCapAna(self,prefix,avetime=10,nrepeat=1,thicktune=True):
		picy,picz=mng.doCapAna("morning",10,1,False)

		mng.saveBP(picy,picz)
		logf.write("%10s %10s code (Y,Z) = (%5d,%5d)\n"%(time_now(),"BeamCen",picy,picz))
		logf.flush()

		# Finish (remove beam monitor)
		mng.finishBC()

	if COLLISCAN==True:
		# Collimator scan
		logstr=mng.colliScan()
		logf.write("%s"%logstr)
		logf.flush()

	# Flux measurement
	if MEAS_FLUX==True:
        	pin_uA,iic_nA,phosec=mng.measureFlux()
		logf.write("IC=%5.1f nA PIN=%5.1f uA PHOSEC=%5.2e phs/sec\n"%(iic_nA,pin_uA,phosec))

	# Finish tuning
	mng.finishExposure()

	# Gonio move
	if EVACUATE_NEEDLE==True:
		#######################
		# Return to the original position
		#######################
		mng.moveXYZmm(sx,sy,sz)

	mng.allFin()
	logf.close()

	# Evacuate all for manual unmount
