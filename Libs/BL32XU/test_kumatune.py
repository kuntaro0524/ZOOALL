import socket
import time
import datetime
import sys,os
import Device

# Change wavelegnt
host = '172.24.242.41'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

devctr=Device.Device(s)
devctr.mono.changeE(12.3984)
