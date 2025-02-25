	# 2015/12/18 coded K.Hirata
        # multi_sch=lm.genHelical(startphi,endphi,stepphi,left_xyz,right_xyz,beamsize,exptime,distance)
	def genHelical(self,startphi,endphi,stepphi,left_xyz,right_xyz,beamsize,exptime,distance):
		gv=GonioVec.GonioVec()
		# Total oscillation width
		total_osc=endphi-startphi
		# Number of frames
		nframe=int(total_osc/stepphi)
		### From KUMA code 2015/12/18
		scanvec=gv.makeLineVec(left_xyz,right_xyz)
		# Distance of this vector [mm]
		dist_vec=gv.calcDist(scanvec)
		nframes_per_point=1
		while(1):
			# number of irradiation points
			n_irrad=int(float(nframe)/float(nframes_per_point))
			# Scan vector length is divided by number of frames
			# [mm]
			step_length=dist_vec/float(n_irrad)
			# ideal_step_length < 0.5um
			# increase number of frames per irradiation point
			dist_um=dist_vec*1000.0
			if dist_um < 0.5:
				nframes_per_point+=1
			else:
				break

		print "Number of irraddiation points: %5d"%n_irrad
		print "Scan vector length: %8.5f"%step_length

		# step [um]
		astep_um=step_length*1000.0

		# RDpropagation 111030 coded
		# Get beam sizes
		rdp=RDprop.RDprop(beamsize,astep_um)
		# ard: Maximum accumulated radiation compared to FullFlux 1.0sec
		# trans: suitable transmission for this scan
		# thickness: estimated Al thickness at this energy
		ard,trans,thickness=rdp.getAttFac(1.0,nframes_per_point,self.wavelength)
		print ard,trans,thickness
		transstr="%5.3f(%4.1f)"%(trans,ard)
		#ardstr="%4.1f"%ard
		thickstr="%4.0f"%thickness
