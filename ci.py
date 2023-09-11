import sys,os,math,numpy,socket,time,cv2
import re
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from Gonio import *
from Capture import *
import Zoom
import CoaxPint
import CoaxImage
#import CryImageProc as CIP

if __name__ == "__main__":
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	#ms.connect(("192.168.163.1", 10101))
	ms.connect(("172.24.242.41", 10101))
	coax=CoaxImage.CoaxImage(ms)
	coax.checkConnection()

	#coax.set_binning(2)
	filename="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/test001.ppm"
	coax.get_coax_image(filename, 200)
