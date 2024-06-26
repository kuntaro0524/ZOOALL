import sys
import os
import socket
import time
import datetime

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import Device
host = '172.24.242.59'
port = 10101

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

dev = Device.Device(s,bl="bl45xu")
dev.init()

phosec = dev.measureFlux()
print phosec *2.0
