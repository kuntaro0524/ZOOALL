import sys
import socket
import time
import Device

if __name__=="__main__":
        #host = '192.168.163.1'
        host = '172.24.242.41'
	dev=Device.Device(host)
	dev.init()
	gap=10.05
        dev.mbs.openTillOpen(wait_interval=10,ntrial=10)
	dev.id.moveTillMove(gap,wait_interval=10,ntrial=10)
