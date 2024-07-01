import sys,os,math,cv2,socket
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import Centering
import RasterSchedule
import SummarySHIKA
import Zoo
import Light
import MultiCrystal
import AttFactor

if __name__ == "__main__":
	zoo=Zoo.Zoo()
	zoo.connect()
	#multi_sch="/isilon/users/target/target/Staff/ZooTest/data1/data/multi.sch"
	multi_sch="/isilon/users/target/target/Staff/ZooTest/lys01/data/multi.sch"
	zoo.doDataCollection(multi_sch)
	zoo.waitTillReady()
	zoo.disconnect()
