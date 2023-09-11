import os,sys,math,numpy,socket,datetime,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS
import Device
import LoopMeasurement
import StopWatch
import MyException

if __name__ == "__main__":
        blanc = '172.24.242.41'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))

        gonio=Gonio.Gonio(s)
        bs=BS.BS(s)
        inocc=IboINOCC.IboINOCC(gonio)

        zoo=Zoo.Zoo()
        zoo.connect()
        zoo.getSampleInformation()

	# ROOT DIRECTORY
	root_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TEST/"

	# Zoo progress report
        zooprog=open("%s/zoo_large.log"%root_dir, "a")

        # preparation
	dev=Device.Device(s)
	dev.init()
	dev.colli.off()
       	dev.prepCenteringLargeHolderCam2()
        sx,sy,sz=dev.gonio.getXYZmm()
	sphi=dev.gonio.getPhi()

        dev.prepCenteringLargeHolderCam1()
        ix,iy,iz=dev.gonio.getXYZmm()

        # Max value= 1.0 TOP_LEFT= (238, 275)
        # horizontal resolution -0.00684848
        # vertical resolution -0.00915152
        h_diff_um,v_diff_um,max_2d=inocc.moveToCenter()
        print("2D=",max_2d)
        h_diff_um,v_diff_um,max_2d=inocc.moveToCenter()
        print("2D=",max_2d)

       	# preparation
       	dev.prepCenteringLargeHolderCam2()
       	#((316, 143), 0.97274786233901978)
       	# um/pixel=0.0135
       	move_um,max_pint= inocc.moveToCenterPint()
	print("PINT=",max_pint)
	print("Moving=",move_um)
       	#move_um,max_pint= inocc.moveToCenterPint()
	#print "PINT=",max_pint
	#print "Moving=",move_um

        x,y,z=dev.gonio.getXYZmm()
	print("GONIO=",x,y,z)
        #dev.gonio.moveXYZmm(sx,sy,sz)
