import os

class InoccConfig():
    def __init__(self):
        self.dataPath = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/TestImages_20200402/"
        self.bright=[6000, 7000,8000,9000, 10000, 12000, 14000]
        self.contrast=[15000, 20000,25000,30000,35000,40000]
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)

        ##  parameter is defined in INOCC.py , Libs/Capture.py
        self.defautBrigt = 8000
        self.defaultContrast = 40000
        self.defaultBackimage = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/BackImages/back_20200402.ppm"
