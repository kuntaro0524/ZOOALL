import sys
import socket
import time

# My library
import BaseAxis

#
class BM:
    def __init__(self, server):
        #bm_x_class = BaseAxis.BaseAxis(server, "beammonitor_x", "pulse")
        bm_y_class = BaseAxis.BaseAxis(server, "beammonitor_y", "pulse")
        bm_z_class = BaseAxis.BaseAxis(server, "beammonitor_z", "pulse")

        self.moni_x = bm_x_class.motor
        self.moni_y = bm_y_class.motor
        self.moni_z = bm_z_class.motor

        self.z_on_pos = 0  # pulse
        self.z_off_pos = -84500  # pulse

        self.x_on_pos = 0  # pulse
        self.x_off_pos = 8500  # pulse

    def go(self, position):
        self.moni_z.nageppa(position)

    def relmove(self, value):
        self.moni_z.relmove(value)

    def offXYZ(self):
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
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    print("Moving Scintillator Monitor")
    moni = BM(s)
    # moni.onPika()
    moni.offXYZ()

    s.close()
