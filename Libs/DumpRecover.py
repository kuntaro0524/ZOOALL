import sys
import socket
import time
import Device
import Singleton

class DumpRecover(Singleton.Singleton):
    def __init__(self,device_class):
        self.dev=device_class

    def isDump(self):
        # MBS check
        status_mbs=self.dev.mbs.getStatus()
        status_dss=self.dev.dss.getStatus()
        print(status_mbs,status_dss)

        if status_mbs!="open":
            return True
        if status_dss!="open":
            return True
        if self.dev.checkRingCurrent(current_threshold=5.0)==False:
            return True
        return False

    def recover(self,wavelength):
        en=12.3984/wavelength
        gap=self.dev.id.getE(en)

        status_id=self.dev.id.getGap()
        # Waiting for the initial phase of dump sequence
        wait_time = 15 * 60 # sec : 15 minutes

        #time.sleep(wait_time)

        if self.dev.mbs.openTillOpen(wait_interval=60,ntrial=10000)==False:
            print("MBS failed")
            return False
        if self.dev.id.moveTillMove(gap,wait_interval=60,ntrial=10000)==False:
            print("ID change failed")
            return False
        if self.dev.dss.openTillOpen(wait_interval=60,ntrial=10000)==False:
            print("DSS open failed")
            return False

        # Tune dtheta1
        prefix="temporal"
        self.dev.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.dev.tcs)
        return True

    # This routine returns "False" when recover was applied.
    def checkAndRecover(self,wavelength):
        if self.isDump()==True:
            self.recover(wavelength)
            return False
        else:
            print("Ring status might be normal.")
            print("Data collection continues...")
            return True

if __name__=="__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    dev=Device.Device(s)
    dev.init()

    dr=DumpRecover(dev)
    if dr.isDump()==True:
        print("OKAY")
        dr.recover(1.0)
