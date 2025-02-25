import sys,os,math,cv2,socket,time
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import Zoo
import LoopMeasurement

if __name__ == "__main__":
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ms.connect(("192.168.163.1", 10101))

	zoo=Zoo.Zoo()
	zoo.connect()

	zoo.getSampleInformation()
	#zoo.cleaning()

	root_dir="/isilon/users/target/target/Staff/ZooTest/"
	beamsize=10.0
	prefix="test"

	lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
	lm.prepCentering()
	lm.centering()

	zoo.disconnect()
