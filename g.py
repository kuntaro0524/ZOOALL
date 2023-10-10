import sys,os,math,socket
import datetime
import BLFactory

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()

    gonio = blf.getGoniometer()
    gonio.rotatePhi(180.0)
    #blf.device.prepCentering(zoom_out=False)
