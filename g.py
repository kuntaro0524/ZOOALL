import sys,os,math,socket
import datetime
import BLFactory

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()

    gonio = blf.getGoniometer()
    rot_angle = float(sys.argv[1])
    gonio.rotatePhi(rot_angle)
    #blf.device.prepCentering(zoom_out=False)
