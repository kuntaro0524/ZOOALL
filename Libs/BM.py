import sys
import socket
import time

# My library
import Motor

class BM:
    def __init__(self, server):
        self.s = server
        self.moni_z = Motor.Motor(self.s, "bl_45in_st2_monitor_1_z", "pulse")

        self.sense = -1
        self.z_on_pos = 0  # pulse
        self.z_off_pos = -19000  # pulse

    def go(self, position):
        self.moni_z.nageppa(position)

    def relmove(self, value):
        self.moni_z.relmove(value)

    def offXYZ(self):
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
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    moni = BM(s)
    print moni.getPos()
    moni.on()
    moni.off()

    s.close()
