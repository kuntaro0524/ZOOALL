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
        inocc.getCam2Image("bs_off_cam2_image.png")
