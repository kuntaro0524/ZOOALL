import socket,os,sys,datetime,cv2,time,numpy

sys.path.append("/isilon/BL41XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import Capture
import CryImageProc

if __name__ == "__main__":
        blanc = '172.24.242.54'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))
        backimg = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/220411_back.ppm"

        dev=Device.Device(s)
        dev.init()

        step=100.0
        logfile="gonio.dat"
        of = open(logfile,"w")
        for i in range(0,20):
            dev.gonio.getXYZmm()
            dev.gonio.moveTrans(step)
            filename = os.path.join(os.getcwd(), "%02d_cap.ppm" % i)
            dev.capture.capture(filename)

            # This instance is for this centering process only
            cip = CryImageProc.CryImageProc(logdir="./")
            cip.setImages(filename, backimg)
            # This generates exception if it could not find any centering information
            xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size=600, option="top")
            accumulated_trans = i * step
            of.write("%8.2f (%5d, %5d) HAMIDASHI = %s\n" % (accumulated_trans, xtarget, ytarget, hamidashi_flag))
