import os,sys,glob
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import MXserver
import Zoo
import Device

# 150722 AM4:00
# Debug: when SPACE has some troubles Zoo stops immediately

bss_srv="192.168.163.2"
bss_port=5555



if __name__ == "__main__":
        ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ms.connect(("172.24.242.41", 10101))

	zoo=Zoo.Zoo()
	zoo.connect()
	zoo.getSampleInformation()
        dev=Device.Device(ms)
	dev.init()

	while(1):
		try:
			zoo.mountSample("2501",1)
			zoo.waitTillReady()
		except MyException, ttt:
			print "Sample mounting failed. Contact BL staff!"
			sys.exit(1)

		dev.prepCentering()
		dev.gonio.rotatePhi(90.0)
		dev.gonio.rotatePhi(-90.0)
		dev.gonio.rotatePhi(90.0)
		dev.gonio.rotatePhi(-90.0)
		time.sleep(20)
		dev.light.off()
		zoo.dismountCurrentPin()
		zoo.waitTillReady()

		try:
			zoo.mountSample("2501",2)
			zoo.waitTillReady()
		except MyException, ttt:
			print "Sample mounting failed. Contact BL staff!"
			sys.exit(1)
		dev.prepCentering()
		dev.gonio.rotatePhi(90.0)
		dev.gonio.rotatePhi(-90.0)
		dev.gonio.rotatePhi(90.0)
		dev.gonio.rotatePhi(-90.0)
		time.sleep(20)
		dev.light.off()
		zoo.dismountCurrentPin()
		zoo.waitTillReady()
	#zoo.capture("pppp.ppm")
	#zoo.ZoomUp()
	#zoo.ZoomDown()
	#schfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/08.Hirata/ike.sch"
	#schfile="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
	#schfile="/isilon/users/target/target/Staff/ZooTest//lys07/data///lys07.sch"
	#zoo.setPhi(140.0)
	#schfile_hirata="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
	#schfile_yaruzo="/isilon/users/target/target/Staff/ZooTest/Schedule/yaruzo.sch"
	#time.sleep(10.0)
	#zoo.doRaster("/isilon/users/target/target/Staff/kuntaro/160707/Auto//test-CPS0293-13/scan/lface//lface.sch")
	#zoo.doRaster(sys.argv[1])
	#zoo.doRaster("/isilon/users/target/target/AutoUsers/160509/Xiangyu/Xi-KLaT005-01/scan/Xi-KLaT005-01.sch")
	#zoo.doDataCollection("/isilon/users/target/target/Staff/2016A/160612/lyshel/1st//lysh2-lys-01/data///helical.sch")
	#zoo.doDataCollection("/isilon/users/target/target/Staff/kuntaro/160715/Auto/KUN10-CPS1013-07/data/cry01.sch")
	#zoo.doDataCollection("/isilon/users/target/target/Staff/kuntaro/160926/Navi-test//test09-CPS1018-08/data//multi.sch")
	#zoo.doDataCollection("/isilon/users/target/target/AutoUsers/kuntaro/161218/RR-test//mbeam09-CPS1716-02/data//multi.sch")
	zoo.disconnect()
