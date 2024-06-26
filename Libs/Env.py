import sys,os
import Device

sys.path.append("/isilon/BL41XU/BLsoft/PPPP/")

class Env():
    def __init__(self):
        self.beamline = "BL41XU"
        self.beamline_lower = self.beamline.lower()
        self.blconfig_path = os.environ["BLCONFIG"]
        self.bssconfig_path = os.path.join(self.blconfig_path, "bss/bss.config")
        self.camerainf_path = os.path.join(self.blconfig_path, "video/camera.inf")

        if os.path.exists(self.camerainf_path): print("OKAY")
        if os.path.exists(self.bssconfig_path): print("OKAY")

