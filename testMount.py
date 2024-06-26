import os,sys,math,numpy,socket,datetime
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS
import Device

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

        # preparation
	dev=Device.Device(s)
	dev.init()

	zoo.dismountCurrentPin()
	zoo.waitTillReady()

       	dev.prepCenteringLargeHolderCam1()
        inocc.getImage("back1.png")

        # preparation
        dev.prepCenteringLargeHolderCam2()
        inocc.getCam2Image("back2.png")

	zoo.mountSample("HRC1010",2)
	zoo.waitTillReady()

        starttime=datetime.datetime.now()
        # Recover Face angle
        bs.evacLargeHolder()
        inocc.recoverFaceAngle()
        inocc.recoverFaceAngle()

        # Precise facing
        inocc.rotateToFace()

       	cx=0.7757
       	cy=-11.5582
       	cz=0.3020

	for i in range(0,3):
        	dev.prepCenteringLargeHolderCam1()
        	ix,iy,iz=dev.gonio.getXYZmm()

        	# Max value= 1.0 TOP_LEFT= (238, 275)
        	# horizontal resolution -0.00684848
        	# vertical resolution -0.00915152
                h_diff_um,v_diff_um,max_2d=inocc.moveToCenter()
		print "2D=",max_2d

        	# preparation
        	#dev.prepCenteringLargeHolderCam2()

        	#((316, 143), 0.97274786233901978)
        	# um/pixel=0.0135
        	#move_um,max_pint= inocc.moveToOtehonPint()
		#print "PINT=",max_pint

        x,y,z=dev.gonio.getXYZmm()
        dx=x-cx
        dy=y-cy
        dz=z-cz
        diff=math.sqrt(dx*dx+dy*dy+dz*dz)
        print "Distance=%8.3f mm\n"%diff

        endtime=datetime.datetime.now()
        time_sec= (endtime-starttime).seconds

	print time_sec
