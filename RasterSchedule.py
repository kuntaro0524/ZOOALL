import sys, os

beamline = "BL32XU"

# This was coded for PILATUS 3 6M at BL45XU
# modified for versatile code
# Version 2.0.0 coded on 2019/07/04 K.Hirata

class RasterSchedule:
    def __init__(self):
        print("Raster schedule class is called")
        self.beamsizeIndex = 0
        self.imgdir = "/staff/bl32xu/Test/"
        self.prefix = "raster_test"
        self.exptime = 0.02
        self.wavelength = 1.0
        self.distance = 300.0
        self.binning = 1  # For EIGER9M K.Hirata 160412
        self.att_idx = 10
        # Scan step in [mm]
        self.v_step_mm = 0.01
        self.h_step_mm = 0.01
        # Crystal ID for automatic data processing
        self.crystal_id = "unknown"
        # Raster scan points
        self.v_points = 10
        self.h_points = 10
        # Scan start phi [deg.]
        # ONLY the startphi is important for 'Raster scan' schedule file
        self.startphi = 0.0
        self.endphi = 1.0
        self.stepphi = 1.0
        # Scan mode
        self.scan_mode = "2D"  # "2D" or "Vert" or "Hori"
        # Shutterless flag 1:Yes 0:No
        self.isShutteless = 1
        # Rotation raster flag
        self.rot_flag = 0
        self.rot_angle = 0.0
        # ROI index
        # BL32XU/BL41XU 1: 4M mode
        # BL45XU 1: 2M mode
        self.roi_index = 1

        # for PILATUS BL45XU
        if beamline == "BL45XU":
            self.img_suffix = "cbf"
        if beamline == "BL41XU" or beamline == "BL32XU":
            self.img_suffix = "h5"

        self.isSSROX = False

    def setExpTime(self, exptime):
        self.exptime = exptime

    def setBeamsizeIndex(self, beamsize_index):
        self.beamsizeIndex = beamsize_index

    # Check function required
    def setTrans(self, transmission):
        self.trans = transmission / 100.0

    def setCrystalID(self, crystal_id):
        self.crystal_id = crystal_id

    def setBinning(self, binning):
        self.binning = binning

    def setWL(self, wavelength):
        self.wavelength = wavelength

    def setSSROX(self):
        self.isSSROX = True

    def makeSchedule(self, name):
        schfile = open(name, "w")
        schestr = self.getSchestr()
        for line in schestr:
            schfile.write("%s\n" % line)

    def makeMulti(self, schedule_file, prefix, gonio_list):
        ofile = open(schedule_file, "w")
        strs = self.getSchstr(gonio_list)
        for line in strs:
            ofile.write("%s" % line)
        ofile.close()

    def setROIindex(self, roi_index):
        self.roi_index = roi_index

    def setWithShutter(self):
        self.isShutteless = 0

    def setAttIndex(self, att_idx):
        self.att_idx = att_idx

    def setStartPhi(self, startphi, stepphi=1.0):
        self.stepphi = stepphi
        self.startphi = startphi
        self.endphi = startphi + stepphi

    def setCL(self, distance):
        self.distance = distance

    def setVpoints(self, n_vpoints):
        self.v_points = n_vpoints

    def setHpoints(self, n_hpoints):
        self.h_points = n_hpoints

    def setPrefix(self, prefix):
        self.prefix = prefix

    def setImgDire(self, imgdir):
        self.imgdir = imgdir

    def setMode(self, mode):
        if mode == "2D":
            print("2D was selected")
        elif mode == "Vert":
            self.h_points = 1
        elif mode == "Hori":
            self.v_points = 1

        self.scan_mode = mode

    def setVertical(self):
        self.scan_mode = "Vert"

    def setHorizontal(self):
        self.scan_mode = "Hori"

    def setVstep(self, step_mm):
        self.v_step_mm = step_mm

    def setHstep(self, step_mm):
        self.h_step_mm = step_mm

    def setWithShutterVertical(self):
        self.setVertical()

    def enableRotation(self, rot=45.0):
        self.rot_angle = rot
        self.rot_flag = 1

    def getSchestr(self):
        schstr = []
        schstr.append("Job ID: 1")
        schstr.append(
            "Status: 0 # -1:Undefined  0:Waiting  1:Processing  2:Success  3:Killed  4:Failure  5:Stopped  6:Skip  7:Pause")
        schstr.append("Job Mode: 4 # 0:Check  1:XAFS  2:Single  3:Multi  4:Raster")
        schstr.append("Crystal ID: %s" % self.crystal_id)
        schstr.append("Tray ID: Not Used")
        schstr.append("Well ID: 0 # 0:Not Used")
        schstr.append("Cleaning after mount: 0 # 0:no clean, 1:clean")
        schstr.append("Not dismount: 0 # 0:dismount, 1:not dismount")
        schstr.append("Data Directory: %s" % self.imgdir)
        schstr.append("Sample Name: %s" % self.prefix)
        schstr.append("File Name Suffix: %s" % self.img_suffix)
        schstr.append("Serial Offset: 0")
        schstr.append("Beam Size: %d" % self.beamsizeIndex)
        schstr.append("Number of Wavelengths: 1")
        schstr.append("Shutterless measurement: %d # 0:no, 1:yes" % self.isShutteless)
        schstr.append("Exposure Time: %9.6f 4.000000 4.000000 4.000000 # [sec]" % self.exptime)
        schstr.append("Linearly variable exposure: 0")
        schstr.append("Number of pulses: 1")
        schstr.append("Exposure Time2: 4.000000 4.000000 4.000000 4.000000 # [sec]")
        schstr.append("Direct XY: 2000.000000 2000.000000 # [pixel]")
        schstr.append("Wavelength: %8.4f 1.020000 1.040000 1.060000 # [Angstrom]" % self.wavelength)
        schstr.append("Centering: 3 # 0:Database  1:Manual  2:Auto  3:None")
        schstr.append("Detector: 0 # 0:CCD  1:IP")
        schstr.append(
            "Scan Condition: %8.4f %8.4f %8.4f  # from to step [deg]" % (self.startphi, self.endphi, self.stepphi))
        schstr.append("Scan interval: 1  # [points]")
        schstr.append("Wedge number: 10  # [points]")
        schstr.append("Wedged MAD: 1  #0: No   1:Yes")
        schstr.append("Start Image Number: 1")
        schstr.append("Goniometer: 0.00000 0.00000 0.00000 0.00000 0.00000 #Phi Kappa [deg], X Y Z [mm]")
        schstr.append("CCD 2theta: 0.000000  # [deg]")
        schstr.append("Detector offset: 0.0 0.0  # [mm] Ver. Hor.")
        schstr.append("Camera Length: %6.2f  # [mm]" % self.distance)
        schstr.append("Beamstop position: 20.000000  # [mm]")
        schstr.append("IP read mode: 1  # 0:Single  1:Twin")
        schstr.append("DIP readout diameter: 400.000000  # [mm]")
        schstr.append("CMOS frame rate: %8.5f -1.000000 -1.000000 -1.000000 # [frame/s]" % (1.0 / self.exptime))
        schstr.append("CCD Binning: %d  # 1:1x1  2:2x2" % self.binning)
        schstr.append("CCD Bin Type: 1  # 0:software 1:hardware")
        schstr.append("CCD Adc: 0  # 0:Slow  1:Fast ")
        schstr.append("CCD Transform: 1  # 0:None  1:Do")
        schstr.append("CCD Dark: 1  # 0:None  1:Measure")
        schstr.append("CCD Trigger: 0  # 0:No  1:Yes")
        schstr.append("CCD Dezinger: 0  # 0:No  1:Yes")
        schstr.append("CCD Subtract: 1  # 0:No  1:Yes")
        schstr.append("CCD Thumbnail: 0  # 0:No  1:Yes")
        schstr.append("CCD Data Format: 0  # 0:d*DTRK  1:RAXIS")
        schstr.append("ROI Limitation Flag:%d  # 0:9M  1:2M" % self.roi_index)
        schstr.append("Oscillation delay: 100.000000  # [msec]")
        schstr.append("Anomalous Nuclei: Mn  # Mn-K")
        schstr.append("XAFS Mode: 0  # 0:Final  1:Fine  2:Coarse  3:Manual")
        if beamline == "BL41XU" or beamline == "BL32XU":
            schstr.append("Attenuator transmission: %8.4f\n" % self.trans)
        elif beamline == "BL45XU":
            schstr.append("Attenuator: %d  # None" % self.att_idx)
        schstr.append("XAFS Condition: 1.891430 1.901430 0.000100  # from to step [A]")
        schstr.append("XAFS Count time: 1.000000  # [sec]")
        schstr.append("XAFS Wait time: 30  # [msec]")
        schstr.append("Transfer HTPFDB: 0  # 0:No, 1:Yes")
        schstr.append("Number of Save PPM: 0")
        schstr.append("Number of Load PPM: 0")
        # schstr.append("Raster Zig-Zag Flag:1")
        schstr.append("PPM save directory: /staff/bl32xu/")
        schstr.append("PPM load directory: /staff/bl32xu/")

        # Mode is vertical
        if self.scan_mode == "Vert":
            schstr.append("Raster Scan Type: 0 # 0:vertical, 1:horizontal, 2: 2D")
        # Mode is vertical
        elif self.scan_mode == "Hori":
            schstr.append("Raster Scan Type: 1 # 0:vertical, 1:horizontal, 2: 2D")
        # Mode is vertical
        else:
            schstr.append("Raster Scan Type: 2 # 0:vertical, 1:horizontal, 2: 2D")
        schstr.append("Raster Vertical Points: %d" % self.v_points)
        schstr.append("Raster Horizontal Points: %d" % self.h_points)
        schstr.append("Raster Vertical Step: %8.4f # [mm]" % self.v_step_mm)
        schstr.append("Raster Horizontal Step: %8.4f # [mm]" % self.h_step_mm)
        schstr.append("Raster Rotation Flag: %d # 0:not rotate, 1:rotate" % self.rot_flag)
        schstr.append("Raster Rotation Range: %8.2f # [deg] rotation range" % self.rot_angle)
        # Zig-zag raster scan is now default 2019/04/12 K.Hirata
        schstr.append("Raster Zig-Zag Flag: 1 # 0: off, 1:on")
        schstr.append("Comment:  ")
        return schstr

if __name__ == "__main__":
    rs = RasterSchedule()

    """
    # Conditions for with Shutter vertical scan
    sc_name="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/raster-test.sch"
    rs.setPrefix("TEST")
    rs.setCL(300.0)
    rs.setImgDire("/isilon/users/target/target/Staff/2015B/151125/08.ZooMod/")
    rs.setStartPhi(0.0,stepphi=0.1)
    rs.setVertical()
    rs.setVpoints(10)
    rs.setHpoints(1)
    rs.setWithShutter()
    rs.setExpTime(0.1)
    rs.makeSchedule(sc_name)
    """
    # Conditions for Shutterless vertical scan
    sc_name = "./raster-test.sch"
    rs.setPrefix("test01")
    rs.setCL(300.0)
    rs.setImgDire("/isilon/users/target/target/Staff/2015B/151211/01.BSS-console-SHIKA-Zoo/")
    rs.setStartPhi(0.0, stepphi=0.1)
    rs.setVertical()
    rs.setVstep(0.005)
    rs.setVpoints(10)
    rs.setHpoints(1)
    rs.setExpTime(0.02)
    rs.makeSchedule(sc_name)
