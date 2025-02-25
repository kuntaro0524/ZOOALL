import sys,os,math,cv2,socket,time
import numpy as np
import LoopMeasurement

if __name__ == "__main__":
        ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #ms.connect(("192.168.163.1", 10101))
        ms.connect(("172.24.242.41", 10101))
        skip=True

        root_dir="/isilon/users/target/target/Staff/ZooTest/"
        prefix="lys07"
        trayid=1
        pinid=1
        beamsize=10.0

        lm=LoopMeasurement(ms,root_dir,prefix)

        lm.prepCentering()
        lm.prepDataCollection()
        # Centering
        zoo=Zoo.Zoo()
        zoo.connect()
        zoo.getSampleInformation()
        lm.centering()

        raster_schedule=lm.prepRaster()
        lm.setBeamsize(beamsize)

        zoo.doRaster(raster_schedule)
        zoo.waitTillReady()

        glist,phi_mid=lm.shikaTalk()

        osc_width=1.0
        total_osc=10.0
        exp_henderson=0.5
        exp_time=0.15
        distance=200.0

        multi_sch=lm.genMultiSchedule(phi_mid,glist,osc_width,total_osc,exp_henderson,exp_time,distance)
        time.sleep(5.0)

        zoo.doDataCollection(multi_sch)
        zoo.waitTillReady()
        zoo.disconnect()

