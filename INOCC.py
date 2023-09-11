import sys, os, math, cv2, socket
import datetime
import numpy as np

beamline = "BL32XU"

from File import *
import matplotlib
import matplotlib.pyplot as plt
from MyException import *
import CryImageProc
import CoaxImage
import BSSconfig
import DirectoryProc
import FittingForFacing
import logging
import logging.config
from configparser import ConfigParser, ExtendedInterpolation

class INOCC:
    def __init__(self, ms, root_dir, sample_name="sample"):
        self.coi = CoaxImage.CoaxImage(ms)
        self.isInit = False
        self.debug = True

        # Get information from beamline.ini file.
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path="%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        config.read(config_path)

        # beamline name is read from 'beamline.ini'
        beamline = config.get("beamline", "beamline")
        # zoom ratio is read from 'beamline.ini'
        # section: inocc, option: zoom
        self.zoom = config.getfloat("inocc", "zoom")

        # back ground image
        self.backimg = config.get("files", "backimg")

        self.logdir=config.get("dirs", "logdir")
        self.fname = config.get("files", "inocc_image")

        # Directory for saving the INOCC result for each data
        self.sample_name = sample_name
        self.root_dir = root_dir

        # Yamagiwa threshold
        # Longest distance threshold from Cmount position during Centering
        self.ddist_thresh = 4.5  # [mm]
        # Raster image for each data directory
        self.isRasterPic = False

        # For facing loop
        self.phi_list = []
        self.area_list = []

        # ROI counter
        self.roi_counter = 1

        # My logger
        self.logger = logging.getLogger('ZOO').getChild("INOCC")

        # Dark experiment
        # beamline.ini has a flag for dark experiment
        # If it is True, the default bright and gain values are changed
        # section: "special_setting", option: "isDark", value type: boolean
        self.isDark = config.getboolean("special_setting", "isDark")

    # INOCC is called from Loopmeasurement
    # Basically each loop has an instance of LoopMeasurement
    # Then, INOCC instance is also one for each loop
    def init(self):
        # Log directory is making for Today
        tds = "%s" % (datetime.datetime.now().strftime("%y%m%d"))
        self.todaydir = "%s/%s" % (self.logdir, tds)

        # Making today's directory
        if os.path.exists(self.todaydir):
            print("%s already exists" % self.todaydir)
        else:
            os.makedirs(self.todaydir)
            os.system("chmod a+rw %s" % self.todaydir)

        # Loop directory
        dp = DirectoryProc.DirectoryProc(self.todaydir)
        # Get the newest number in 4 digits: like "0001","0099"
        num_prefix = dp.getRoundHeadPrefix(ndigit=4)
        self.loop_dir = "%s/%s_%s" % (self.todaydir, num_prefix, self.sample_name)
        print("SELF=", self.loop_dir)

        # Making today's directory
        if os.path.exists(self.loop_dir):
            print("%s already exists" % self.loop_dir)
        else:
            os.makedirs(self.loop_dir)
            os.system("chmod a+rw %s" % self.loop_dir)

        # self.raster_picpath = self.todaydir
        print("Coax camera information will be acquired!")

        self.cip = CryImageProc.CryImageProc()

        # Log file for centering
        self.logfile = open("%s/inocc.log" % self.loop_dir, "a")

        self.coi.set_zoom(self.zoom)
        self.cenx, self.ceny = self.coi.get_cross_pix()
        # 170425-Yamagiwa safety
        # Configure file for reading gonio mount position
        self.bssconfig = BSSconfig.BSSconfig()
        # Read Cmount position from configure file
        self.mx, self.my, self.mz = self.bssconfig.getCmount()

        # File name for each directory
        self.ff = File(self.loop_dir)
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/%03d_test.ppm" % (self.loop_dir, new_idx)

        # Force to remove the existing "test.ppm"
        """
        try:
            os.system("\\rm -Rf %s"%self.fname)
        except MyException,ttt:
            raise MyException("Centering:init fails to remove the previous 'test.ppm'")
        return
        """
        self.isInit = True

    def setRasterPicture(self, raster_picpath):
        if self.isInit == False:
            self.init()
        self.isRasterPic = True
        self.raster_picpath = raster_picpath
        self.logfile.write("Picpath = %s\n" % self.raster_picpath)
        # print self.raster_picpath

    def setYamagiwaSafety(self, largest_movement):
        self.ddist_thresho = largest_movement

    def setBack(self, backimg):
        if self.isInit == False:
            self.init()
        self.logfile.write("setting back ground image to %s\n" % backimg)
        self.backimg = backimg

    def capture(self, image_name_abs_path):
        self.coi.get_coax_image(image_name_abs_path)

    def closeCapture(self):
        self.coi.closeCapture()

    def getGXYZphi(self):
        return self.coi.getGXYZphi()

    def moveGXYZphi(self, x, y, z, phi):
        self.coi.moveGXYZphi(x, y, z, phi)

    # 190514 coded by K.Hirata
    def fitAndFace(self, phi_area_list):
        fit_log = open("%s/fit_face.log" % self.loop_dir, "w")
        # fit_log = open("fit_face.log", "w")
        phi_list = []
        area_list = []
        # Dividing phi & area list
        for phi, area in phi_area_list:
            phi_list.append(phi)
            area_list.append(area)
            fit_log.write("%5.2f %8.1f\n" % (phi, area))
        # Fitting
        fff = FittingForFacing.FittingForFacing(phi_list, area_list, logpath=self.loop_dir)
        face_angle = fff.findFaceAngle()
        return float(face_angle)

    # roi_len: length from the top in [um]
    def capture_and_center(self, option="top", roi_len=300.0):
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/%03d_test.ppm" % (self.loop_dir, new_idx)
        self.capture(self.fname)
        cip = CryImageProc.CryImageProc()
        cip.setImages(self.fname, self.backimg)

        cx, cy, cz, phi = self.coi.getGXYZphi()
        if self.isInit == False:
            self.init()

        cont = cip.getContour()

        # getContour failed
        if len(cont) == 0:
            return 0.0

        top_xy = cip.find_top_x(cont)
        roi_pix_len = cip.calcPixLen(roi_len)
        roi_cont = cip.selectHoriROI(cont, top_xy, roi_pix_len)

        # Current goniometer position
        # Found!
        if len(cont) != 0:
            # Top centering
            if option == "top":
                xedge, yedge = top_xy
            else:
                # ROI vertical center centering
                xedge, yedge = cip.findCenteringPoint(roi_cont, roi_pix_len, top_xy)
            x, y, z = self.coi.calc_gxyz_of_pix_at(xedge, yedge, cx, cy, cz, phi)
            # Calculate vertical movement at this centering step
            dx = x - cx
            dz = z - cz
            # print "DX, DZ = ", dx,dz
            ## self.cenx,self.ceny=self.coi.get_cross_pix()
            d_vertpix = top_xy[1] - self.ceny
            print("DDDDDDDDDDD", d_vertpix)

            if d_vertpix > 0:
                move_direction = 1.0
            else:
                move_direction = -1.0

            # movement distance [um]
            vmove = move_direction * math.sqrt((dx * dx + dz * dz)) * 1000.0  # [um]
            self.coi.moveGXYZphi(x, y, z, phi)
            if self.debug == True:
                cip.drawContourTop(cont, (xedge, yedge), "./cccc.png")

            # is a loop ROI touched to the edge of OAV scene?
            left_flag, right_flag, lower_flag, upper_flag, n_true = cip.isTouchedToEdge(roi_cont)
            edge_flags = left_flag, right_flag, lower_flag, upper_flag, n_true

            print("N_TRUE=", n_true)

            if n_true == 1 and right_flag == True:
                isArea = True
            else:
                isArea = False
            if n_true == 0:
                isFound = False
            else:
                isFound = True

            # Calculate area of the image
            area = cv2.contourArea(cont)
            return vmove, area, isFound, isArea, edge_flags
        else:
            return 0.0, 0.0

    def rotatePhiAndGetArea(self, phi, loop_size):
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/%03d_area.ppm" % (self.loop_dir, new_idx)
        self.coi.rotatePhi(phi)
        cip = CryImageProc.CryImageProc(logdir=self.loop_dir)
        self.coi.get_coax_image(self.fname)
        cip.setImages(self.fname, self.backimg)
        roi_cont = cip.getROIcontour(loop_size)
        area = cv2.contourArea(roi_cont)

        self.logfile.write("PHI = %5.2f Area = %5.2f\n" % (phi, area))

        return area

    def getArea(self, isLogImage=False):
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/%03d_area.ppm" % (self.loop_dir, new_idx)
        self.capture(self.fname)
        cip = CryImageProc.CryImageProc(logdir=self.loop_dir)
        cip.setImages(self.fname, self.backimg)

        if isLogImage == True:
            # log image
            log_dir = "%s/" % (self.loop_dir)
            dp = DirectoryProc.DirectoryProc(log_dir)
            prefix = dp.getRoundHeadPrefix(dir_prefix, "png", ndigit=4)

        contour = cip.getContour()
        area = cv2.contourArea(contour, prefix)
        print("AREA = ", area)
        return area

    # 2019/05/08 22:30 K.Hirata coded
    # 2019/05/14 01:45 K.Hirata modified
    # Small step centering has no meanings
    def findLoop(self, roi_len=300.0):
        ok_flag = False
        self.area_list = []  # includes (angle, area) list

        for phi in [0, 45, 90, 135]:
            self.coi.rotatePhi(phi)
            vmove, area, isFound, isArea, edge_flags = self.capture_and_center(option="roi", roi_len=roi_len)
            if isFound == False:
                self.logfile.write("No loop was detected. Next phi...\n")
                continue
            else:
                ok_flag = True

            print("Area (flag = %s) : %8.2f at %8.2f" % (isArea, area, phi))
            # when the loop was found
            if isArea == True:
                self.area_list.append((phi, area))

            # which direction does the loop move to if it is rotated by 10deg
            if len(self.area_list) == 1:
                phi += 10.0
                self.coi.rotatePhi(phi)
                vmove, area, isFound, isArea, edge_flags = self.capture_and_center(option="roi", roi_len=roi_len)
                print("VMOOOOOOOOOOOOOOOOVE=", vmove)
                if vmove > 0.0:
                    direction = 1.0
                else:
                    direction = -1.0

        if ok_flag == False:
            self.logger.info("Moving Y 2mm")
            gx, gy, gz, phi = self.coi.getGXYZphi()
            newgy = gy + self.cip.calcYdistAgainstGoniometer(2.0)

            # Check a distance from mount position
            if self.isYamagiwaSafe(gx, newgy, gz) == False:
                raise MyException("Movement was larger than limited value (Yamagiwa safety)")
            else:
                self.coi.moveGXYZphi(gx, newgy, gz, phi)
            return False
        else:
            return True

    # Investigating 10 deg step centering
    # 2019/05/08 22:30 K.Hirata coded
    def investigateCentering(self):
        ok_flag = False
        ofile = open("step30deg_centering.dat", "w")
        for phi in range(-720, 720, 30):
            self.coi.rotatePhi(phi)
            vmove, area = self.capture_and_center(option="roi", roi_len=300)
            # when the loop was found
            gx, gy, gz, phi = self.coi.getGXYZphi()
            ofile.write("%5.2f deg %9.4f %9.4f %9.4f\n" % (phi, gx, gy, gz))

    def simpleCenter(self, phi, loop_size=600.0, option='top'):
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/%03d_center.ppm" % (self.loop_dir, new_idx)
        self.logger.info("##################### TOP CENTERING %5.2f deg.\n" % phi)
        self.logger.info("INOCC.coreCentering captures %s\n" % self.fname)
        self.coi.rotatePhi(phi)
        cx, cy, cz, phi = self.coi.getGXYZphi()
        self.coi.get_coax_image(self.fname)
        # This instance is for this centering process only
        cip = CryImageProc.CryImageProc(logdir=self.loop_dir)
        cip.setImages(self.fname, self.backimg)
        roi_image = os.path.join(self.loop_dir, "%03d_roi.png" % self.ff.getNewIdx3())
        cip.setROIpic(roi_image)
        self.roi_counter += 1
        # This generates exception if it could not find any centering information
        xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size=loop_size, option=option)
        self.logger.info("PHI: %5.2f deg Option=%s Centering: (Xtarget, Ytarget) = (%5d, %5d) HAMIDASHI = %s\n"
                         % (phi, option, xtarget, ytarget, hamidashi_flag))
        x, y, z = self.coi.calc_gxyz_of_pix_at(xtarget, ytarget, cx, cy, cz, phi)
        self.coi.moveGXYZphi(x, y, z, phi)

        self.logger.info(">>>>>> FILE=%s Area=%8.3f at %8.3f" % (self.fname, area, phi))

        return area, hamidashi_flag

    def suribachiCentering(self, phi_center, loop_size=600.0):
        self.logger.info("OOOOOOOOOOOOOOOOOO  SURIBACHI STARTS center: %5.2f OOOOOOOOOOOOOO\n" % phi_center)
        phi_range = 90.0
        phi_step = 10.0
        phi_min = phi_center - phi_range / 2.0
        phi_max = phi_center + phi_range / 2.0

        ok_min = False
        ok_max = False
        area_array = []
        for i in range(0, 5):
            # At around phi_min
            if ok_min == False:
                for phi in np.arange(phi_min, phi_center, phi_step):
                    self.logfile.write("Around minimum angle\n")
                    self.logger.info("Around minimum angle\n")
                    try:
                        self.logger.info("move to simpleCenter function.")
                        area, hamidashi_flag = self.simpleCenter(phi, option="top")
                        self.logger.info("if this line does not appear if the simpleCenter fails")
                        # When the edge can be detected
                        if hamidashi_flag == True:
                            area, hamidashi_flag = self.simpleCenter(phi, option="top")
                        if phi == phi_min:
                            area_array.append((phi, area))
                            ok_min = True
                        found_phi_around_min = phi
                        break
                    except:
                        self.logger.info("PHI=%5.2f failed." % phi)
                        self.logfile.write("PHI=%5.2f failed." % phi)
                        continue

            phi_max = found_phi_around_min + 90.0
            if ok_max == False:
                # At around phi_max
                for phi in np.arange(phi_max, found_phi_around_min, -phi_step):
                    self.logfile.write("Around maximum angle= %5.2f\n" % phi)
                    try:
                        area, hamidashi_flag = self.simpleCenter(phi, option="top")
                        # When the +45 deg centering achieves
                        if hamidashi_flag == True:
                            area, hamidashi_flag = self.simpleCenter(phi, option="top")
                        # When the centering fails, this code is skipped.
                        if phi == phi_max:
                            area_array.append((phi, area))
                            ok_max = True
                        found_phi_around_max = phi
                        break
                    except:
                        self.logfile.write("PHI=%5.2f failed.\n" % phi)
                        continue

            diff_min_max = found_phi_around_max - found_phi_around_min
            if diff_min_max != 90.0:
                ok_min = False
                ok_max = False
            # print "#####################################"
            # print "DIFF_PHI=", (found_phi_around_max - found_phi_around_min)
            # print "#####################################"

        # Finally at the phi_center
        try:
            area, hamidashi_flag = self.simpleCenter(phi_center, option="top")
            area_array.append((phi_center, area))
        except:
            raise MyException("suribachiCentering failed")

        self.logfile.write("AAAAAAAAAAAREEE %s AREAERRE\n" % area_array)
        self.logfile.write("EEEEEEEEEEEEEEEEEE  SURIBACHI ENDS EEEEEEEEEEEEEEEEEE\n")
        return area, hamidashi_flag

    # Suribachi centering new code 190517
    def coreCentering(self, phi_list, loop_size=600.0):
        self.isFoundEdge = False
        isRoughCenter = False

        if self.isInit == False:
            self.init()
        phi_area_list = []
        n_good = 0
        # Loop for rough centering
        for phi in phi_list:
            self.coi.rotatePhi(phi)
            # Gonio current coordinate
            # Try centering
            if isRoughCenter == False:
                try:
                    # If this trial fails, exception will be detected
                    junk, hamidashi_flag = self.simpleCenter(phi, loop_size=loop_size, option='top')
                    # When the first centering succeeds, suribachi centering will start
                    area, hamidashi_flag = self.suribachiCentering(phi, loop_size=loop_size)
                    # area of ROI for facing
                    # Comment out : 2021/05/31
                    # phi_area_list.append((phi, area))
                    # area_180 = area
                    # If all okay in suribachi centering
                    phi_vert = phi + 90.0
                    area, hamidashi_flag = self.simpleCenter(phi + 90.0, loop_size=loop_size, option='top')
                    phi_area_list.append((phi_vert, area))
                    self.logfile.write("coreCentering. Rough centering was finished\n")
                    isRoughCenter = True
                    # phi + 45.0
                    phi2 = phi + 45.0
                    area = self.rotatePhiAndGetArea(phi2, loop_size)
                    phi_area_list.append((phi2, area))
                    # PHI Middle
                    phi3 = phi + 135.0
                    area = self.rotatePhiAndGetArea(phi3, loop_size)
                    phi_area_list.append((phi3, area))
                    # PHI Middle
                    phi4 = phi + 180.0
                    area = self.rotatePhiAndGetArea(phi4, loop_size)
                    phi_area_list.append((phi4, area))
                    # 0.0 an 180.0 deg would be same area
                    phi_area_list.append((phi, area))
                    n_good = 4

                    break
                # Case when the loop was not found in the trial section
                except MyException as ttt:
                    # raise MyException("INOCC.coreCentering failed"
                    self.logfile.write("Go to next phi from %5.2f deg\n" % phi)
                    continue
            else:
                self.logfile.write("Rough centering was already completed. Just for PHI= %5.2f deg. centering\n" % phi)
                area, hamidashi_flag = self.simpleCenter(phi, loop_size=loop_size, option='top')

        if n_good == 0:
            raise MyException("coreCentering failed")

        return n_good, phi_area_list

    def isYamagiwaSafe(self, gx, gy, gz):
        # Distance from mount position
        # print gx,gy,gz
        # print self.mx,self.my,self.mz
        dista = math.sqrt(pow((gx - self.mx), 2.0) + pow((gy - self.my), 2.0) + pow(gz - self.mz, 2.0))
        if dista > self.ddist_thresh:
            print("deltaDistance=%5.2f mm" % dista)
            return False
        else:
            return True

    # Modified along with the update of CryImageProc
    def edgeCentering(self, phi_list, ntimes, challenge=False, loop_size=600.0):
        if self.isInit == False:
            self.init()
        self.logger.info("################### EDGE CENTERING ######################")
        n_good = 0
        for i in range(0, ntimes):
            try:
                n_good, phi_area_list = self.coreCentering(phi_list, loop_size=loop_size)
                print("NGOOD=", n_good)
                # Added 160514     
                # A little bit dangerous modification
                # 190514 I cannot understand this code
                if challenge == True and n_good == len(phi_list):
                    break
            except MyException as tttt:
                self.logger.info("INOCC.edgeCentering moves Y 2000um")
                gx, gy, gz, phi = self.coi.getGXYZphi()
                move_ymm = self.cip.calcYdistAgainstGoniometer(2.0)
                newgy = gy + move_ymm
                if self.isYamagiwaSafe(gx, newgy, gz) == False:
                    raise MyException("Movement was larger than threshold (Yamagiwa safety)")
                self.coi.moveGXYZphi(gx, newgy, gz, phi)
        if n_good == 0:
            raise MyException("edgeCentering failed")

        print("################### EDGE CENTERING ENDED ######################")
        return n_good, phi_area_list

    def facing(self, phi_list):
        if self.isInit == False:
            self.init()
        n_good = 0
        min_area = 9999999999.0
        for phi in phi_list:
            self.coi.rotatePhi(phi)
            ## self.coi.get_coax_image(self.fname, 200)
            new_idx = self.ff.getNewIdx3()
            self.fname = "%s/%03d_facing.ppm" % (self.loop_dir, new_idx)
            self.coi.get_coax_image(self.fname, 40)  # for DFK72 YK@190315
            # Gonio current coordinate
            cx, cy, cz, phi = self.coi.getGXYZphi()
            # This background captured with speed=200 for ARTRAY
            # This background captured with speed=40 for DFK72 YK@190315
            # 4x4 binning zoom -48000pls
            try:
                grav_x, grav_y, xwidth, ywidth, area, xedge, yedge = \
                    self.cip.getCenterInfo(self.fname, debug=False)
                print("PHI AREA=", phi, area)
            except MyException as ttt:
                # print ttt.args[1]
                continue
            if min_area > area:
                min_area = area
                saved_phi = phi
        phi_face = saved_phi + 90.0
        self.coi.rotatePhi(phi_face)
        return phi_face

    # Largely modified on 190514 by K.Hirata
    # loop_size should have unit of "um"
    def cap4width(self, loop_size=600.0):
        if self.isInit == False:
            self.init()

        # Capture 
        new_idx = self.ff.getNewIdx3()
        self.fname = "%s/cap4width_%03d.ppm" % (self.loop_dir, new_idx)
        self.coi.get_coax_image(self.fname)
        cip = CryImageProc.CryImageProc(logdir=self.loop_dir)
        cip.setImages(self.fname, self.backimg)

        # For small loop
        roi_cont = cip.getROIcontour(loop_size)
        # raster_pic = "%s/raster.png" % (self.loop_dir)
        print("cap4width captures", self.raster_picpath)
        roi_xmin, roi_xmax, roi_ymin, roi_ymax, roi_cenx, roi_ceny = cip.getRasterArea(roi_cont, self.raster_picpath)
        log_pic = "%s/raster.png" % (self.loop_dir)
        print(log_pic)
        roi_xmin, roi_xmax, roi_ymin, roi_ymax, roi_cenx, roi_ceny = cip.getRasterArea(roi_cont, log_pic)

        # Raster width
        xwidth = roi_xmax - roi_xmin
        ywidth = roi_ymax - roi_ymin

        return xwidth, ywidth, roi_cenx, roi_ceny

    # Largely modified on 190514 by K.Hirata
    # loop_size should have unit of 'um'
    def doAll(self, ntimes=3, skip=False, loop_size=600.0, offset_angle=0.0):
        if self.isInit == False:
            self.init()

        phi_face = 0.0

        # Initial goniometer coordinate
        ix, iy, iz, iphi = self.coi.getGXYZphi()

        # Main loop
        if skip == False:
            # First centering
            phi_list = [0, 45, 90, 135]
            # Loop centering for initial stages
            # ROI should be wider 
            try:
                self.logger.debug("The first edge centering..")
                n_good, phi_area_list = self.edgeCentering(phi_list, 2, challenge=True, loop_size=loop_size)
            except MyException as ttt:
                self.logger.debug("The first edge centering failed..")
                try:
                    self.logger.debug("The second edge centering..")
                    n_good, phi_area_list = self.edgeCentering(phi_list, 2, challenge=True, loop_size=loop_size)
                except MyException as tttt:
                    self.logger.debug("The second edge centering failed. Raise exception")
                    self.logger.debug("%s" % tttt)
                    raise MyException("Loop cannot be found after edgeCentering x 2 times. %s " % tttt)

            phi_face = self.fitAndFace(phi_area_list)
            self.logger.info(f"face_angle = {phi_face}deg")

            # adds offset angles for plate-like crystals
            self.logger.info(">>>> offset angle setting <<<<<")
            phi_face = phi_face + offset_angle
            phi_small = phi_face + 90.0
            self.logger.info(">>>> Simple centering <<<<<")
            self.simpleCenter(phi_small, loop_size, option="gravity")
            area, hamidashi_flag = self.simpleCenter(phi_face, loop_size, option="gravity")
            self.logger.info("Hamidashi_flag = %s" % hamidashi_flag)
            print(("HAMIDASHI=", hamidashi_flag))
            # Re-centering if hamidashi_flag = True
            if hamidashi_flag == True:
                self.simpleCenter(phi_face, loop_size, option="gravity")

        # Final centering
        cx, cy, cz, phi = self.coi.getGXYZphi()
        # Raster area definition
        xwidth, ywidth, r_cenx, r_ceny = self.cap4width(loop_size)

        gonio_info = cx, cy, cz, phi
        pix_size_um = self.coi.get_pixel_size()
        raster_width = pix_size_um * float(xwidth)
        raster_height = pix_size_um * float(ywidth)

        print("Width  = %8.1f[um]" % raster_width)
        print("Height = %8.1f[um]" % raster_height)
        print("Centering.doAll finished.")

        return raster_width, raster_height, phi_face, gonio_info


if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    # read configure file(beamline.init)
    config = ConfigParser(interpolation=ExtendedInterpolation())
    ini_file = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(ini_file)
    zooroot = config.get('dirs', 'zooroot')

    logname = "./inocc.log"
    logging.config.fileConfig('%s/Libs/logging.conf' % (zooroot), defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0o666)

    test_dir = "/staff/bl32xu/BLsoft/NewZoo/BackImages/"

    inocc = INOCC(ms, test_dir)
    phi_face = 90

    start_time = datetime.datetime.now()

    # back image path read from 'beamline.ini'
    backimg = config.get('files', 'backimg')
    inocc.setBack(backimg)
    # For each sample raster.png
    raster_picpath = "%s/raster.png" % test_dir
    inocc.setRasterPicture(raster_picpath)

    # def doAll(self, ntimes=3, skip=False, loop_size=600.0, offset_angle=0.0):
    rwidth, rheight, phi_face, gonio_info = inocc.doAll(ntimes=2, skip=False, loop_size=600.0)

    print(("Loop width/height=", rwidth, rheight))

    ms.close()