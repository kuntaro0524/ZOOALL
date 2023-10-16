import sys,os,math,socket
import datetime
import BLFactory

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()
    gonio = blf.getGoniometer()
    move = float(sys.argv[1])
    gonio.moveUpDown(move)