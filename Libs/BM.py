import sys
import socket
import time

# My library
<<<<<<< HEAD
from Motor import *


#
class BM:
    def __init__(self, server):
        self.s = server
        self.moni_y = Motor(self.s, "bl_32in_st2_monitor_1_y", "pulse")
        self.moni_z = Motor(self.s, "bl_32in_st2_monitor_1_z", "pulse")
        self.moni_x = Motor(self.s, "bl_32in_st2_monitor_1_x", "pulse")

        self.z_on_pos = 0  # pulse
        self.z_off_pos = -84500  # pulse

        self.x_on_pos = 0  # pulse
        self.x_off_pos = 8500  # pulse
=======
import Motor

class BM:
    def __init__(self, server):
        self.s = server
        self.moni_z = Motor.Motor(self.s, "bl_45in_st2_monitor_1_z", "pulse")

        self.sense = -1
        self.z_on_pos = 0  # pulse
        self.z_off_pos = -19000  # pulse
>>>>>>> zoo45xu/main

    def go(self, position):
        self.moni_z.nageppa(position)

    def relmove(self, value):
        self.moni_z.relmove(value)

    def offXYZ(self):
<<<<<<< HEAD
        self.moni_z.move(self.z_off_pos)
        self.moni_x.move(self.x_off_pos)

    def onPika(self):
        # self.moni_x.move(-4318)
        # self.moni_z.move(-39850)
        # From 160408
        self.moni_x.move(self.x_on_pos)
        self.moni_z.move(self.z_on_pos)

    def getPos(self):
        z_pulse = int(self.moni_z.getPosition()[0])
        x_pulse = int(self.moni_x.getPosition()[0])
        print(x_pulse, z_pulse)

    def isMoved(self):
        isY = self.moni_y.isMoved()
        isZ = self.moni_z.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.41'
=======
        #self.moni_z.move(self.z_off_pos)
        #self.moni_x.move(self.x_off_pos)
        print "NO at BL45XU"

    def on(self):
        self.moni_z.move(self.z_on_pos)

    def off(self):
        self.moni_z.move(self.sense * self.z_off_pos)

    def getPos(self):
        z_pulse = int(self.moni_z.getPosition()[0])
        return z_pulse

    def isMoved(self):
        isZ = self.moni_z.isMoved()

        if isZ == 0:
            return True
        else:
            return False

if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

<<<<<<< HEAD
    print("Moving Scintillator Monitor")
    moni = BM(s)
    # moni.onPika()
    moni.offXYZ()
=======
    moni = BM(s)
    print moni.getPos()
    moni.on()
    moni.off()
>>>>>>> zoo45xu/main

    s.close()
