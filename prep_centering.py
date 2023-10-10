import sys,os,math,socket
import datetime
import BLFactory

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()
    blf.device.prepCentering(zoom_out=False)
