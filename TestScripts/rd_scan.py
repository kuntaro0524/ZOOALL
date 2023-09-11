import os,sys
from MultiPointRD import *
from numpy import *
from Gonio import *

def moveHeight(inixyz,phi,height):
	finxyz=[1,2,3]
        # Up-down from current phi
        curr_phi=math.radians(phi)

        # unit [mm]
        move_x=-height*math.sin(curr_phi)
        move_z=height*math.cos(curr_phi)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)

	finxyz[0]=inixyz[0]+move_x
	finxyz[1]=inixyz[1]
	finxyz[2]=inixyz[2]+move_z

	return finxyz

def moveTrans(inixyz,trans):
	finxyz=[1,2,3]

        # marume[um]
        move_y=round(trans,5)

	finxyz[0]=inixyz[0]
	finxyz[1]=inixyz[1]+move_y
	finxyz[2]=inixyz[2]

	return finxyz

def moveHV(inixyz,h,v,phi):
	tmp=moveTrans(inixyz,h)
	tmp2=moveHeight(tmp,phi,v)

	return tmp2

if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        mpr=MultiPointRD()
	gonio=Gonio(s)
        curr_dir=os.environ['PWD']

	# Current status
	cen=gonio.getXYZmm()
	phi=gonio.getPhi()

	# Condition
	offset_list=[(0.0,0.0)]
	startphi=phi
	stepphi=0.1
	endphi=phi+stepphi
	step=0.0005
	############
	## 1.8A edge
	############
	dist=282.0 # 18.0keV
	#dist=182.0 # 12.4keV
	#dist=105.0 # 8.5keV

	# 8.5keV
	#att=200
	#wl=1.45863
	#ntimes=50

	# 12.4keV
	#att=700
	#wl=1.0
	#ntimes=50

	# 18.0keV
	att=1500
	wl=0.6888
	ntimes=50

	idx=0
	for offset in offset_list:
		h_off=offset[0]
		v_off=offset[1]
		newxyz=moveHV(cen,h_off,v_off,phi)
		print(idx,newxyz)
		idx+=1
		prefix="%03d"%idx
		#dire="%s/%03d/"%(curr_dir,idx)
		dire="%s/"%(curr_dir)
        	# condition setting
        	mpr.setCenter(newxyz)
        	mpr.setScanCondition(startphi,endphi,stepphi)
        	mpr.setDist(dist)
        	mpr.setAl(att)
        	mpr.setWL(wl)
        	mpr.setNtime(ntimes)
        	mpr.genRDscan(dire,prefix)
