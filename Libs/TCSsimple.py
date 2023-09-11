import time
from Motor import *


class TCSsimple:
    def __init__(self, server):
        self.s = server
        self.tcs_height = Motor(self.s, "bl_32in_tc1_slit_1_height", "mm")
        self.tcs_width = Motor(self.s, "bl_32in_tc1_slit_1_width", "mm")
        self.tcs_vert = Motor(self.s, "bl_32in_tc1_slit_1_vertical", "mm")
        self.tcs_hori = Motor(self.s, "bl_32in_tc1_slit_1_horizontal", "mm")

    def getApert(self):
        # get values
        self.ini_height = self.tcs_height.getApert()
        self.ini_width = self.tcs_width.getApert()
        return float(self.ini_height[0]), float(self.ini_width[0])

    def setApert(self, height, width):
        self.tcs_height.move(height)
        self.tcs_width.move(width)
        print("current tcs aperture : %8.5f %8.5f\n" % (height, width))
