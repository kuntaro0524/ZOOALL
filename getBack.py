import socket,os,sys,datetime,cv2,time,numpy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC

if __name__ == "__main__":
	import Gonio
	blanc = '172.24.242.41'
	b_blanc = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((blanc,b_blanc))
	
	dev=Device.Device(s)
	dev.init()
	inocc=IboINOCC.IboINOCC(dev.gonio)

	# preparation
	dev.prepCenteringLargeHolderCam2()
        inocc.getCam2Image("bson_back.png")
	
	#for phi in range(0,360,10):
		#dev.gonio.rotatePhi(phi)
        	#inocc.getCam2Image("holder_%f.png"%phi)
