import sys,os,math,cv2,socket
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import CryImageProc 
import CoaxImage

if __name__ == "__main__":
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#ms.connect(("192.168.163.1", 10101))
	ms.connect(("172.24.242.41", 10101))

	coi=CoaxImage.CoaxImage(ms)
        filename="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/test.ppm"
	cip=CryImageProc.CryImageProc("test.ppm")
	coi.set_zoom(-48000)

	cenx,ceny=coi.get_cross_pix()

	phi_area_list=[]
	def oneCycle(phi_list):
		n_good=0
		for phi in phi_list:
			coi.rotatePhi(phi)
			coi.get_coax_image(filename, 200)
			# Gonio current coordinate
			cx,cy,cz,phi=coi.getGXYZphi()
			# This background captured with speed=200
			# 4x4 binning zoom -48000pls
			backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_c1_z0_b4.ppm"
			try:
				grav_x,grav_y,xwidth,ywidth,area,xedge=cip.getCenterInfo(filename,debug=False)
				print "EDGE",xedge
			except MyException,ttt:
				#print ttt.args[1]
				continue
	
			if grav_x > cenx:
				grav_x=cenx
			print grav_x,grav_y
			x,y,z=coi.calc_gxyz_of_pix_at(grav_x,grav_y,cx,cy,cz,phi)
			coi.moveGXYZphi(x,y,z,phi)
			l=phi,area
			phi_area_list.append(l)
			n_good+=1
			#print x,y,z
		return n_good

	def facing(phi_list):
		n_good=0
		min_area=9999999999.0
		for phi in phi_list:
			coi.rotatePhi(phi)
			coi.get_coax_image(filename, 200)
			# Gonio current coordinate
			cx,cy,cz,phi=coi.getGXYZphi()
			# This background captured with speed=200
			# 4x4 binning zoom -48000pls
			backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_c1_z0_b4.ppm"
			try:
				grav_x,grav_y,xwidth,ywidth,area,xedge=cip.getCenterInfo(filename,debug=False)
				print "AREA",area
			except MyException,ttt:
				#print ttt.args[1]
				continue
			if min_area > area:
				min_area=area
				saved_phi=phi
		return saved_phi+90.0

	#phi_list=[0,45,90,135,180]
	#n_good=oneCycle(phi_list)

	#if n_good==0:
		## Y translation to (+) direction
		#gx,gy,gz,phi=coi.getGXYZphi()
		#newgy=gy-0.5
		#coi.moveGXYZphi(gx,newgy,gz,phi)

	phi_list=[0,30,60,90,120,150]
	phi_face=facing(phi_list)
	coi.rotatePhi(phi_face)

	phi_list=[phi_face,phi_face-90.0]
	oneCycle([phi_face])

	# Facing
