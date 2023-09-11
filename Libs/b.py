import os,sys,math,numpy

def makeIrradPoints(left_edge,right_edge,y_step):
        lx,ly,lz=left_edge
        rx,ry,rz=right_edge

        # Vector calculation
        lvec=numpy.array((lx,ly,lz))
        rvec=numpy.array((rx,ry,rz))
        # lr vector
        lrvec=rvec-lvec
        # length of LR vector
        lr_len=numpy.linalg.norm(lrvec) # in [mm]
        # unit vector
        unit_vec=lrvec/lr_len

        # distance of y direction [mm]
        y_length=math.fabs(ly-ry)
        # ratio 
        ratio=math.fabs((y_step/1000.0)/y_length)

	print(y_length,ratio)

	# step length along with 3D vector of LR
	stepVec=lr_len*ratio
	print(stepVec)

        # number of irradiation points on this helical vector
        step_mm=y_step/1000.0
        npoints=int(y_length/step_mm)+1
	print(npoints)

        # step in mm
        for i in range(0,npoints):
		vec=lvec+i*stepVec*unit_vec
		print("%8.5f %8.5f %8.5f"%(vec[0],vec[1],vec[2]))

gx=0.0000
gy=1.5000
gz=0.0000

fx=1.0000
fy=2.0000
fz=1.0000

step_y=20.0

g=gx,gy,gz
f=fx,fy,fz

makeIrradPoints(g,f,step_y)
