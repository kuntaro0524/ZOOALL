import sys, os, math, socket, time
import numpy as np
import datetime

from MyException import *
import INOCC
import RasterSchedule
import Light
import Colli
import MultiCrystal
import AttFactor
import Beamsize
import BeamsizeConfig
import GonioVec
import ScheduleBSS
# import AnaShika
import CrystalSpot
import KUMA
import DirectoryProc
import logging
import logging.config

beamline = "BL32XU"

# version 2.0.0 modified on 2019/07/04 K.Hirata

class LoopMeasurement:
    def __init__(self, ms, root_dir, prefix):
        self.ms = ms
        self.root_dir = root_dir
        self.prefix = prefix
        self.inocc = INOCC.INOCC(ms, root_dir, sample_name=prefix)
        self.inocc.init()

        self.h_beam = 10.0  # [um]
        self.v_beam = 10.0  # [um]
        self.max_framerate = 200.0  # [Hz]
        # Gonio center for the loop centering
        # for BL45XU
        self.x = -1.119
        self.y = 7.9494
        self.z = 0.4925
        # wavelength
        self.wavelength = 1.0000  # [angstrome]
        # Back light
        self.raster_n_height = 10
        self.raster_n_width = 10

        self.light = Light.Light(self.ms)
        self.colli = Colli.Colli(self.ms)

        self.beamsizeconf = BeamsizeConfig.BeamsizeConfig()
        self.multi_dir = "/foo/bar"

        # Raster scan setting: additional grids
        self.raster_n_add = 3
        # True for including beamsize index in 'schedule file'
        self.isBeamsizeIndexOnScheduleFile = True

        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("LoopMeasurement")

        # 10um step raster scan
        self.beamsize_thresh_10um = 20.0 #[um]
        self.flag10um = False

    # 2015/11/21 horizontal, vertical beamsize
    def setPhotonDensityLimit(self, photon_density_limit):
        self.photon_density_limit = photon_density_limit

    def setMinBeamsize10umRaster(self, beamsize_thresh):
        self.flag10um = True
        self.beamsize_thresh_10um = beamsize_thresh

    # 2015/11/21 horizontal, vertical beamsize
    # Penging 2019/04/20 at BL45XU K.Hirata
    def setBeamsize(self, h_beam, v_beam):
        # print h_beam, v_beam
        # This is not required -> BSS can do that probablly.
        # self.bsc.changeBeamsizeHV(h_beam,v_beam)
        self.h_beam = h_beam
        self.v_beam = v_beam

    def setWavelength(self, wavelength):
        self.wavelength = wavelength

    def prepCentering(self):
        self.colli.off()
        self.light.on()

    def saveGXYZphi(self):
        return self.inocc.getGXYZphi()

    def moveGXYZphi(self, x, y, z, phi):
        return self.inocc.moveGXYZphi(x, y, z, phi)

    def captureImage(self, capture_name):
        self.prepCentering()
        filename_abs = "%s/%s/%s" % (self.root_dir, self.prefix, capture_name)
        self.inocc.capture(filename_abs)

    def closeCapture(self):
        self.logger.info("closing Capture port of INOCC")
        self.inocc.closeCapture()
        self.logger.info("closing Capture succeeded")

    def prepDirectory(self, dirname):
        if os.path.exists(dirname) == False:
            os.mkdir(dirname)

    # 2015/12/11 K.Hirata 
    # Tests for one action to make directory tree
    def prepPath(self, pathname):
        if os.path.exists(pathname) == False:
            os.makedirs(pathname)

    # 2018/04/13 'n_mount' parameter was added 
    # 2019/05/19 K. Hirata
    def prepDataCollection(self):
        self.logger.info("prepDataCollection started.")
        # Image directory
        self.sample_dir = "%s/%s" % (self.root_dir, self.prefix)

        # Making a round directory
        dp = DirectoryProc.DirectoryProc(self.sample_dir)
        raster_prefix = "scan"
        dir_for_this_time, dindex = dp.makeRoundDir(raster_prefix, isMake=False, ndigit=2)

        self.raster_dir = "%s/scan%02d/" % (self.sample_dir, dindex)
        self.multi_dir = "%s/data%02d/" % (self.sample_dir, dindex)

        # Making directory Making
        self.logger.info("Making directories....")
        if os.path.exists(self.sample_dir) == False:
            os.makedirs(self.sample_dir)
        if os.path.exists(self.root_dir) == False:
            os.makedirs(self.root_dir)
        if os.path.exists(self.raster_dir) == False:
            os.makedirs(self.raster_dir)
        if os.path.exists(self.multi_dir) == False:
            os.makedirs(self.multi_dir)
        return dindex

    # 2016/10/08 height_add was added. unit [um]
    def centering(self, backimg, loop_size="small", offset_angle=0.0, height_add=0.0, largest_movement=5.0):
        # Prep centering
        self.prepCentering()
        # setting background image
        self.logger.info("LM:centering background file is replaced by %s" % backimg)
        self.inocc.setBack(backimg)
        # For raster scan area jpg is output for each data directory
        raster_picpath = "%s/raster.jpg" % self.sample_dir
        self.logger.info("Capturing %s" % raster_picpath)
        self.inocc.setRasterPicture(raster_picpath)
        # Centering Crystal
        self.inocc.setYamagiwaSafety(largest_movement)
        self.logger.info("LM:centering Start: centering.doAll")
        try:
            rwidth, rheight, phi_face, gonio_info = self.inocc.doAll(skip=False, loop_size=loop_size,
                                                                 offset_angle=offset_angle)
            message = "%9.4f %9.4f %9.4f - (W,H) = (%8.2f, %8.2f)" % (gonio_info[0], gonio_info[1], gonio_info[2], rwidth, rheight)
            self.logger.info(message)
            self.logger.info("LM:centering Ends : centering.doAll")

            # self.cen_x,y,z is the center coordinate of this centering
            self.cen_x, self.cen_y, self.cen_z, self.raster_start_phi = gonio_info
            # number of grids in raster scan
            self.raster_n_width = int(rwidth / self.h_beam) + self.raster_n_add
            self.raster_n_height = int(rheight / self.v_beam + height_add) + self.raster_n_add
            # For SSROX centering
            self.rheight = rheight
            self.rwidth = rwidth

            return rwidth, rheight
        except:
            self.logger.warning("Exception detected.")
            raise MyException("Centering failed.")

    # 2016/10/08 height_add was added. unit [um]
    def roughCentering(self, backimg, loop_size=600, offset_angle=0.0, height_add=0.0, largest_movement=5.0):
        # Prep centering
        self.prepCentering()
        # setting background image
        self.logger.info("LM:centering background file is replaced by %s" % backimg)
        self.inocc.setBack(backimg)
        # For raster scan area jpg is output for each data directory
        self.logger.info("LM:path for sample %s" % self.sample_dir)
        raster_picpath = "%s/raster.jpg" % self.sample_dir
        # Centering Crystal
        self.inocc.setYamagiwaSafety(largest_movement)
        self.logger.info("LM: rough centering has started: centering.edgeCentering")
        try:
            n_good, phi_area_list = self.inocc.edgeCentering([0, 45, 90, 135], 1, False, loop_size)

            self.logger.info("LM: rough centering has been finished: centering.doAll")
            return True
        except:
            self.logger.warning("Rough centering failed.")
            return False

    # 2015/11/21 Exposure time can be set
    # To be obsoleted 2015/12/11 
    # New one is raster2D
    def prepRaster(self, dist=300.0, att_idx=10, exptime=0.02, crystal_id="unknown"):
        rss = RasterSchedule.RasterSchedule()
        # Set step size as same with the beam size
        rss.setVstep(self.v_beam / 1000.0)
        rss.setHstep(self.h_beam / 1000.0)

        raster_schedule = "%s/%s.sch" % (self.raster_dir, self.prefix)

        rss.setCrystalID(crystal_id)
        rss.setWL(self.wavelength)
        rss.setExpTime(exptime)
        rss.setPrefix(self.prefix)
        rss.setAttIndex(att_idx)
        rss.setStartPhi(self.raster_start_phi)
        rss.setCL(dist)
        rss.setVpoints(self.raster_n_height)
        rss.setHpoints(self.raster_n_width)
        rss.setImgDire(self.raster_dir)
        rss.makeSchedule(raster_schedule)

        # raster_path="%s/%s/"%(self.raster_dir,self.prefix)
        return raster_schedule, self.raster_dir

    # 2015/12/15 Rotation Raster 2D
    # For quick data collection from multiple-tiny crystals
    # 2016/05/16 Rotation Raster 2D on EIGER9M
    # MX225HS : binning=4 for default
    # 2019/07/19 SSROX
    # 2020/06/02 rename the function to prepSSROX
    def prepSSROX(self, scan_id, gxyz, sphi, cond, flux):

        self.logger.info("LM.SSROX starts...")
        rss = RasterSchedule.RasterSchedule()

        # 2020/01/31 For abe experiments: vertical step = 4.0 um
        # This is enough for almost sample (2019/12/05 results)
        # Loop size is around 450-500um in vertical direction.
        # vertical_step = 4.0 #[um]
        # 2020/06/02 For BL45XU SSORX implementation
        # 'cry_max_size_um' in CSV file is used as vertical_step
        vertical_step = cond['cry_max_size_um']

        # ROI is not set
        roi_index = 0
        # Step size calculation in [mm]
        rss.setVstep(vertical_step / 1000.0)
        rss.setHstep(cond['raster_hbeam'] / 1000.0)

        # output directory
        raster_path = "%s/%s/" % (self.raster_dir, scan_id)
        raster_schedule = "%s/%s.sch" % (raster_path, scan_id)
        self.prepPath(raster_path)

        # Number of grids
        self.raster_n_height = int(self.rheight / vertical_step)
        self.logger.info("The height of raster scan area = %8.3f um" % self.rheight)
        self.logger.info("The grids along the height in raster scan area = %8d" % self.raster_n_height)

        # Total oscillation should be read from CSV file also
        total_osc = cond['total_osc']
        osc_width = cond['osc_width']

        # Firstly it calculates the number of horizontal grids
        # from 'rotaion' conditions
        h_grids_from_rotation = int(total_osc / osc_width)
        h_length_from_rotation = float(h_grids_from_rotation) * cond['raster_hbeam'] #[um]

        self.logger.info("Horizontal loop length from INOCC is %8.2f um(max)" % self.rwidth)
        self.logger.info("Horizontal scan length from rotaion condition= %8.3f um" % h_length_from_rotation)

        # if the found loop size in horizontal direction is longer than 'h_length_desired'
        if self.rwidth > h_length_from_rotation:
            self.logger.info("Horizontal loop length from INOCC is %8.2f um(max)" % self.rwidth)
            self.logger.info("Horizontal scan length is set to %8.2f um" % h_length_from_rotation)
            self.rwidth = h_length_from_rotation
            h_grids = h_grids_from_rotation
            self.logger.info("Horizontal scan grids is set to %5d" % h_grids_from_rotation)
        else:
            h_grids = int(self.rwidth / cond['raster_hbeam'])
            total_osc = h_grids * cond['osc_width']

        # Total oscillation range should be replaced by the calculated one.
        cond['total_osc'] = total_osc
        self.logger.info("Total oscillation range is replaced by %8.3f[deg.]" % cond['total_osc'])
        self.logger.info("The final grids along with the horizontal axis %5d" % h_grids)
        # a horizontal length of SSROX area
        hori_len = float(h_grids) * cond['raster_hbeam'] / 1000.0 # [mm]

        # Dose estimation (2020/06/02 for BL45XU)
        self.logger.info("Exposure condition will be prepared by KUMA.")
        kuma = KUMA.KUMA()
        # the routine considers 'dose slicing' also
        self.logger.info("Estimate best conditions....")
        self.logger.info("Measured flux = %8.1e phs/sec" % flux)
        exp_time, best_transmission = kuma.getBestCondsHelical(cond, flux, hori_len)
        self.logger.info("LM: Best transmission = %9.6f" % best_transmission)
        self.logger.info("LM: Best exposure time from KUMA = %9.6f[sec]" % exp_time)
        ntimes = cond['ntimes']

        # Hot fix for abe data collection 2020/12/06
        # Hot fix for abe data collection 2021/02/10
        # Hot fix for shihoya data collection 2021/02/10
        exp_time=cond['exp_raster']
        best_transmission=100.0

        rss.setSSROX()
        rss.setWL(self.wavelength)
        rss.setExpTime(exp_time)
        rss.setPrefix(scan_id)

        # Attenuator raster is set by 'best_transmission' (0<= value<=1.0)
        if beamline == "BL32XU" or beamline == "BL41XU" or beamline=="BL45XU":
            rss.setTrans(best_transmission)
        else:
            # Attenuator index is calculated
            attfac = AttFactor.AttFactor()
            best_thick = attfac.getBestAtt(cond['wavelength'], best_transmission)
            self.logger.info("Best thick for this SSROX: Al=%8.2f[um]" % best_thick)
            att_idx = attfac.getAttIndexConfig(best_thick)
            self.logger.info("Attenuator index: index= %5d" % att_idx)
            rss.setAttIndex(att_idx)

        rss.setStartPhi(sphi)
        # NOTE! camera distance for 'data collection' is defined by 'dist_raster'
        rss.setCL(cond['dist_raster'])
        rss.setVpoints(self.raster_n_height)
        rss.setHpoints(h_grids)
        rss.setImgDire(raster_path)
        rss.enableRotation(rot=total_osc)
        self.logger.debug("HERE3")
        rss.setROIindex(roi_index)

        # Finally making a schedule file
        rss.makeSchedule(raster_schedule)

        return raster_schedule, raster_path

    # Swithced from prepRaster 2015/12/11
    def prepRaster2D(self, scan_id, gxyz, phi, dist=300.0, att_idx=10, exptime=0.02, crystal_id="unknown"):
        sx, sy, sz = gxyz
        self.moveGXYZphi(sx, sy, sz, phi)
        rss = RasterSchedule.RasterSchedule()

        # Set step size as same with the beam size
        rss.setVstep(self.v_beam / 1000.0)
        rss.setHstep(self.h_beam / 1000.0)

        raster_path = "%s/%s/" % (self.raster_dir, scan_id)
        raster_schedule = "%s/%s.sch" % (raster_path, scan_id)
        self.prepPath(raster_path)

        rss.setCrystalID(crystal_id)
        rss.setWL(self.wavelength)
        rss.setExpTime(exptime)
        rss.setPrefix(scan_id)
        rss.setAttIndex(att_idx)
        rss.setStartPhi(phi)
        rss.setCL(dist)
        rss.setVpoints(self.raster_n_height)
        rss.setHpoints(self.raster_n_width)
        rss.setImgDire(raster_path)
        rss.makeSchedule(raster_schedule)

        return raster_schedule, raster_path

        def make_shika_direction(self, scandir, min_score, min_dist, max_hits=100):
            ofs = open(os.path.join(scandir, "shika_auto.config"), "w")
            ofs.write("min_score= %.3f\n" % min_score)
            ofs.write("min_dist= %.3f\n" % min_dist)
            ofs.write("max_hits= %.3f\n" % max_hits)
            ofs.close()

    # 2016/06/11 Raster scan should be called from the same function
    # scan_mode="2D", "Vert", "Hori"
    # 2019/06/02 Code was modified for all beamlines
    # 2020/07/10 'isAdd' option is added. 'True' of this value activates 'add grid points to the defined scan length'.
    def rasterMaster(self, scan_id, scan_mode, gxyz, vscan_um, hscan_um, vstep_um, hstep_um, phi, cond, isHEBI=False, isAdd=True):
        # Flag for 'modifying' attenuator thickness and exposure time.
        flag_mod_exptime = False

        # Move to the defined goniometer coordinate and phi angle.
        sx, sy, sz = gxyz
        self.moveGXYZphi(sx, sy, sz, phi)
        tx, ty, tz, tphi = self.saveGXYZphi()

        dist_raster = cond['dist_raster']
        exp_raster = cond['exp_raster']
        # ROI index
        roi_index = cond['raster_roi']
        # Transmission
        if isHEBI == True:
            transmission = cond['hebi_att']
            # Experimental settings from 'cond'
            raster_vbeam = cond['ds_vbeam']
            raster_hbeam = cond['ds_hbeam']
        else:
            # Experimental settings from 'cond'
            raster_vbeam = cond['raster_vbeam']
            raster_hbeam = cond['raster_hbeam']
            transmission = cond['att_raster']

        # Beam size index
        beamsize_index = self.beamsizeconf.getBeamIndexHV(raster_hbeam, raster_vbeam)
        self.logger.info("Beamsize index in rasterMaster is %5d" % beamsize_index)

        # Prep class
        rss = RasterSchedule.RasterSchedule()

        # Attenuator index from 'att_fac' for BL32XU/BL45XU
        # Attenuator should be set in 'an index of attenuator defined in bss.config'
        if beamline == "BL32XU" or beamline == "BL41XU" or beamline == "BL45XU":
            # if you need to activate 'attenuator modification', put 'flag_mod_exptime' on at the top of this function
            if flag_mod_exptime:
                # Check transmission with 'thinnest attenuator'
                trans_ratio = transmission / 100.0  # convertion to 'ratio'
                attfac = AttFactor.AttFactor()
                mod_exp, mod_trans = attfac.checkThinnestAtt(cond['wavelength'], exp_raster, trans_ratio)
                tmp_trans = mod_trans * 100.0
                # Schedule setting (attenuator factor) [% is converted to ratio in RSS])
                rss.setTrans(tmp_trans)  # this is unit of [%]
                # case when the transmission is modified.
                if mod_trans != trans_ratio:
                    self.logger.info("Transmission is changed : %9.5f   -> %9.5f (Max 1.0 (=100 perc.))" % (
                    best_transmission, mod_trans))
                    self.logger.info("Exposure     is changed : %9.5f[s]-> %9.5f[s]" % (exp_time, mod_exp))
                exp_raster = mod_exp
            # normally: No modification on the input transmission.
            else:
                rss.setTrans(transmission)

        # case for the beamline with discrete attenuator thickness
        else:
            att_fact = AttFactor.AttFactor()
            trans = transmission / 100.0  # convertion to 'ratio'
            best_thick = att_fact.getBestAtt(cond['wavelength'], trans)
            self.att_idx = att_fact.getAttIndexConfig(best_thick)
            # Schedule setting (attenuator index)
            rss.setAttIndex(self.att_idx)

        # 2020/11/02 Coded for BL45XU
        # If this flag is 'True', raster scan is always conducted by using 10 um step.
        if raster_hbeam >= self.beamsize_thresh_10um or raster_vbeam >= self.beamsize_thresh_10um:
            if self.flag10um:
                vstep_um = 10.0
                hstep_um = 10.0
                exp_raster = 1/100.0 # 100 Hz is fixed now

        # Scan points for vertical and horizontal
        if scan_mode == "2D" or scan_mode=="2d":
            if isAdd == True:
                self.raster_n_height = int(vscan_um / vstep_um) + self.raster_n_add
                self.raster_n_width = int(hscan_um / hstep_um) + self.raster_n_add
            else:
                self.raster_n_height = int(vscan_um / vstep_um)
                self.raster_n_width = int(hscan_um / hstep_um)
        elif scan_mode == "Hori":
            if isAdd == True:
                self.raster_n_width = int(hscan_um / hstep_um) + self.raster_n_add
            else:
                self.raster_n_width = int(hscan_um / hstep_um)
            self.raster_n_height = 1
        elif scan_mode == "Vert":
            if isAdd == True:
                self.raster_n_height = int(vscan_um / vstep_um) + self.raster_n_add
            else:
                self.raster_n_height = int(vscan_um / vstep_um)
            self.raster_n_width = 1
        else:
            raise MyException("rasterMaster: scan setting failed")

        # Raster schedule file path
        raster_path = "%s/%s/" % (self.raster_dir, scan_id)
        self.logger.info("Raster path=%s" % raster_path)
        raster_schedule = "%s/%s.sch" % (raster_path, scan_id)
        self.prepPath(raster_path)

        # Schedule file
        if self.isBeamsizeIndexOnScheduleFile == True:
            rss.setBeamsizeIndex(beamsize_index)
        rss.setWL(self.wavelength)
        # ROI index setting for scan
        rss.setROIindex(roi_index)
        rss.setPrefix(scan_id)
        rss.setCL(dist_raster)
        # 2019/10/26 Detector cover scan for salt screening
        if beamline.lower() == "bl45xu" and cond['cover_scan_flag'] == 1:
            rss.setCoverScan()
        rss.setImgDire(raster_path)
        rss.setStartPhi(phi)
        rss.setMode(scan_mode)
        # Setting v step in [mm]
        vstep_mm = vstep_um / 1000.0
        rss.setVstep(vstep_mm)
        # Setting h step in [mm]
        hstep_mm = hstep_um / 1000.0
        rss.setHstep(hstep_mm)
        rss.setVpoints(self.raster_n_height)
        rss.setHpoints(self.raster_n_width)

        rss.setExpTime(exp_raster)
        rss.makeSchedule(raster_schedule)

        return raster_schedule, raster_path

    # 2015/12/05 Precise setting for centering raster
    # 2015/12/11 Precise setting for centering raster
    # More easy to be read by K.Hirata
    # scan_id: character buffer for making 'directory'
    # beam_h, beam_v : raster beamsize 
    def prepVrasterIn(self, scan_id, beam_h, beam_v, range_mm, step_mm, gxyz, phi, att_idx=10, distance=300.0,
                      exptime=0.02):
        print("DEBUG")
        sx, sy, sz = gxyz
        self.moveGXYZphi(sx, sy, sz, phi)
        tx, ty, tz, tphi = self.saveGXYZphi()

        print("DEBUG2")
        print("Target position:", sx, sy, sz, phi)
        print("Current position:", tx, ty, tz, tphi)

        print("DEBUG3")
        rss = RasterSchedule.RasterSchedule()
        # Raster beam size (temporal code 151204)
        self.setBeamsize(beam_h, beam_v)  # [um]

        # vertical scan length
        # (temporal code 151125)
        # 2.5 is tekitou

        # raster_vert_range=float(cond.shika_mindist)*2.5/1000.0 # [mm]
        raster_npoints = int(range_mm / step_mm)

        # Raster schedule file path
        raster_path = "%s/%s/" % (self.raster_dir, scan_id)
        raster_schedule = "%s/%s.sch" % (raster_path, scan_id)
        self.prepPath(raster_path)

        # Set SHIKA condition
        min_score = 0.0  # pick up all of pixels
        min_dist = 0.0  # [um] pick up all of pixels
        self.make_shika_direction(raster_path, min_score, min_dist)

        rss.setPrefix(scan_id)
        rss.setCL(distance)
        rss.setImgDire(raster_path)
        rss.setStartPhi(phi)
        rss.setVertical()
        rss.setVstep(step_mm)
        rss.setAttIndex(att_idx)
        rss.setVpoints(raster_npoints)
        rss.setHpoints(1)
        rss.setExpTime(exptime)
        rss.makeSchedule(raster_schedule)

        return raster_schedule, raster_path

    # 2015/12/05 Precise setting for centering raster
    # scan_id: character buffer for making 'directory'
    # beam_h, beam_v : raster beamsize 
    def prepVraster(self, scan_id, beam_h, beam_v, range_mm, step_mm, gxyz, phi, att_idx=10, distance=300.0,
                    exptime=0.02):
        rss = RasterSchedule.RasterSchedule()
        sx, sy, sz = gxyz
        self.moveGXYZphi(sx, sy, sz, phi)

        # Raster beam size (temporal code 151204)
        self.setBeamsize(beam_h, beam_v)  # [um]

        # vertical scan length
        # (temporal code 151125)
        # 2.5 is tekitou

        # raster_vert_range=float(cond.shika_mindist)*2.5/1000.0 # [mm]
        raster_npoints = int(range_mm / step_mm)

        # Conditions for Shutterless vertical scan
        this_directory = "%s/%s/" % (self.raster_dir, scan_id)
        self.prepDirectory(this_directory)
        this_schedule = "%s/vraster.sch" % (this_directory)

        print("Raster for this crystal in %s" % this_schedule)
        print("Schedule file is %s.sch" % scan_id)

        rss.setPrefix("vraster")
        rss.setCL(distance)
        rss.setImgDire(this_directory)
        rss.setStartPhi(phi)
        rss.setVertical()
        rss.setVstep(step_mm)
        rss.setVpoints(raster_npoints)
        rss.setHpoints(1)
        rss.setExpTime(exptime)
        rss.setAttIndex(att_idx)
        rss.makeSchedule(this_schedule)

        return this_schedule

    # 2015/12/15 K.Hirata coded
    # Notebook p.?? around 
    # Target: SHIKA _selected.dat
    # thresh_nspots = threshold to select 'existing crystal'
    # Mode : "grav" = gravity center (2 or more 
    def shikaEdges(self, raster_path, scan_id, thresh_nspots=30, margin=0.005):
        # SHIKA results
        sshika = SummarySHIKA.SummarySHIKA(raster_path, scan_id)
        sshika.waitingForSummary()
        try:
            glist = sshika.readSummary()
        except MyException as tttt:
            raise MyException("SHIKA could not get any good crystasl")

        left_xyz = [99.999, 99.999, 99.999]
        right_xyz = [99.999, 99.999, 99.999]

        xmin = 99.9999
        ymin = 99.9999
        zmin = 99.9999
        xmax = -99.9999
        ymax = -99.9999
        zmax = -99.9999

        for gxyz in glist:
            # unzip gonio xyz list from data selected by SHIKA
            x, y, z, phi, score = gxyz
            if ymin > y:
                xmin = x
                ymin = y
                zmin = z
            if ymax < y:
                xmax = x
                ymax = y
                zmax = z

        # Margin addition
        ymin = ymin + margin
        ymax = ymax - margin

        if xmin == 99.9999 or ymin == 99.9999 or zmin == 99.9999:
            print("shikaEdges:XMIN")
            raise MyException("Left edge of the crystal: Wrong")
        elif xmax == 99.9999 or ymax == 99.9999 or zmax == 99.9999:
            print("shikaEdges:XMAX")
            raise MyException("Right edge of the crystal: Wrong")
        else:
            left_code = xmin, ymin, zmin
            right_code = xmax, ymax, zmax
            return left_code, right_code

    # Relating to the summary.dat
    def readSummaryDat(self, raster_path, scan_id, cxyz, phi, thresh_nspots=30):
        # SHIKA analysis
        shika_dir = "%s/_spotfinder/" % raster_path
        ashika = AnaShika.AnaShika(shika_dir, cxyz, phi)
        ashika.setSummaryFile("summary.dat")
        # scan_id & prefix are different each other
        prefix = "%s_" % scan_id
        print("PREFIX=", prefix)
        print("SCAN_ID=", scan_id)
        # KUNIO setDiffscanLog(self,path):

        # N grids on the 2D raster scan
        ngrids = self.raster_n_height * self.raster_n_width
        comp_thresh = 0.95

        # SHIKA waiting for preaparation
        # 5 minutes
        try:
            ashika.readSummary(prefix, ngrids, comp_thresh=comp_thresh, timeout=600)
            print("LoopMeasurement.readSummaryDat succeeded.")

        except MyException as tttt:
            raise MyException("shikaSumSkipStrong failed to wait summary.dat")

        return ashika

    # coded on 2017.01.15
    # GXYZ is extracted from diffscan.log
    # max_ncry : max number of crystals for data collection
    # min_score : min spot number for picking up crystals
    # max_score : max spot number for picking up crystals

    def prepSmallWedge(self, cxyz, phi, raster_path, scan_id, min_score=10, max_score=1000, crysize=0.10, max_ncry=50,
                       mode="grav"):
        def compCryScore(x, y):
            a = x.score_total
            b = y.score_total
            # print "SCORE COMPARE",a,b
            if a == b: return 0
            if a < b: return 1
            return -1
            print(thresh_nspots, crysize)

        # Center of this scan
        cx, cy, cz = cxyz
        # SHIKA analysis
        ashika = self.readSummaryDat(raster_path, scan_id, cxyz, phi)

        # setting min/max values
        ashika.setMinMax(min_score, max_score)

        # Crystal finding
        print("Crystal size = %8.5f" % crysize)
        crystals = ashika.findCrystals(scan_id, dist_thresh=crysize)
        n_cry = len(crystals)
        print("Crystals %5d\n" % n_cry)

        # Sorting better crystals
        # The top of crystal is the best one
        # The bottom is the worst one
        crystals.sort(cmp=compCryScore)

        # Crystal size check
        gxyz_list = []
        n_cry = 0
        if mode == "grav":
            for crystal in crystals:
                n_cry += 1
                crystal.setDiffscanLog(raster_path)
                gx, gy, gz = crystal.getGrav()
                gxyz_list.append((gx, gy, gz))
                print(n_cry, gx, gy, gz)
                if n_cry >= max_ncry:
                    break
        elif mode == "peak":
            for crystal in crystals:
                n_cry += 1
                crystal.setDiffscanLog(raster_path)
                gx, gy, gz = crystal.getPeakCode()
                gxyz_list.append((gx, gy, gz))
                print(n_cry, gx, gy, gz)
                if n_cry >= max_ncry:
                    break

        return gxyz_list

    def isAbort(self):
        self.get_current_str = "get/bl_dbci_ringcurrent/present"
        self.ms.sendall(self.get_current_str)
        recbuf = self.ms.recv(8000)
        strs = recbuf.split("/")
        ring_current = float(strs[len(strs) - 2].replace("mA", ""))

        if ring_current > 50.0:
            print("Ring current %5.1f" % ring_current)
            return False
        else:
            print("Ring aborted.")
            print("Ring current %5.1f" % ring_current)
        return True

    # 2019/05/21 test coding
    # Recover original one (upper as _old)
    # 2019/05/22 Largely modified to use KUMA as external function to estimate 
    # exposure condition.
    # 2019/12/11 'same_point' option should be set to 'True' if dose slicing experiments are done
    # at the same crystal repeatedly. Schedule file for each crystal will be made.
    def genMultiSchedule(self, phi_mid, glist, cond, flux, prefix="multi", same_point=True):
        mc = MultiCrystal.MultiCrystal()
        multi_sch = "%s/multi.sch" % self.multi_dir

        # Multi conditions
        half_width = cond['total_osc'] / 2.0
        start_phi = phi_mid - half_width
        end_phi = phi_mid + half_width

        # Beam size setting
        beamsize_index = self.beamsizeconf.getBeamIndexHV(cond['ds_hbeam'], cond['ds_vbeam'])
        print("Beamsize index in rasterMaster is %5d" % beamsize_index)

        # Estimating dose and set suitable exposure condition
        # Exposure time will sometimes be modified when
        # an initial condition does not require any attenuation.
        kuma = KUMA.KUMA()
        exp_time, best_transmission = kuma.getBestCondsMulti(cond, flux)

        if beamline == "BL32XU" or beamline == "BL41XU" or beamline=="BL45XU":
            # Check transmission with 'thinnest attenuator'
            attfac = AttFactor.AttFactor()
            mod_exp, mod_trans = attfac.checkThinnestAtt(cond['wavelength'], exp_time, best_transmission)
            tmp_trans = mod_trans * 100.0
            mc.setTrans(tmp_trans)  # this is unit of [%]

            # case when the transmission is modified.
            if mod_trans != best_transmission:
                self.logger.info("Transmission is changed : %9.5f   -> %9.5f (Max 1.0 (=100 perc.))" % (best_transmission, mod_trans))
                self.logger.info("Exposure     is changed : %9.5f[s]-> %9.5f[s]" % (exp_time, mod_exp))

            exp_time = mod_exp
        else:
            # Definition of attenuator index
            attfac = AttFactor.AttFactor()
            best_thick = attfac.getBestAtt(cond['wavelength'], best_transmission)
            att_idx = attfac.getAttIndexConfig(best_thick)
            mc.setAttIdx(att_idx)

        # 160618 Added by K. Hirata
        mc.setPrefix(prefix)
        mc.setCrystalID(cond['sample_name'])
        mc.setWL(self.wavelength)
        if self.isBeamsizeIndexOnScheduleFile == True:
            mc.setBeamsizeIndex(beamsize_index)
        mc.setExpTime(exp_time)
        mc.setCameraLength(cond['dist_ds'])
        mc.setScanCondition(start_phi, end_phi, cond['osc_width'])
        mc.setDir(self.multi_dir)
        mc.setShutterlessOn()

        if same_point == False:
            mc.makeMultiDoseSlicing(multi_sch, glist, ntimes=cond['ntimes'])
        else:
            mc.makeMultiDoseSlicingAtSamePoint(multi_sch, glist, ntimes=cond['ntimes'])
        # mc.makeMulti(multi_sch,glist)

        return multi_sch


    # 2020/07/09 K.Hirata coded.
    # multi_sch = self.lm.genMultiSchedule(phi_start, phi_end, center_xyz, cond, self.phosec_meas, prefix=prefix)
    def genSingleSchedule(self, phi_start, phi_end, cenxyz, cond, flux, prefix="multi", same_point=True):
        mc = MultiCrystal.MultiCrystal()
        single_sch = "%s/single.sch" % self.multi_dir
        # glist for generating the schedule file
        glist = []
        glist.append(cenxyz)

        # Beam size setting
        beamsize_index = self.beamsizeconf.getBeamIndexHV(cond['ds_hbeam'], cond['ds_vbeam'])
        print("Beamsize index in rasterMaster is %5d" % beamsize_index)

        # Estimating dose and set suitable exposure condition
        # Exposure time will sometimes be modified when
        # an initial condition does not require any attenuation.
        total_osc = phi_end - phi_start
        # This line is very important for HITO
        cond['total_osc'] = total_osc
        kuma = KUMA.KUMA()
        exp_time, best_transmission = kuma.getBestCondsMulti(cond, flux)

        if beamline == "BL32XU" or beamline == "BL41XU" or beamline == "BL45XU":
            # Check transmission with 'thinnest attenuator'
            attfac = AttFactor.AttFactor()
            mod_exp, mod_trans = attfac.checkThinnestAtt(cond['wavelength'], exp_time, best_transmission)
            tmp_trans = mod_trans * 100.0
            mc.setTrans(tmp_trans)  # this is unit of [%]

            # case when the transmission is modified.
            if mod_trans != best_transmission:
                self.logger.info("Transmission is changed : %9.5f   -> %9.5f (Max 1.0 (=100 perc.))" % (best_transmission, mod_trans))
                self.logger.info("Exposure     is changed : %9.5f[s]-> %9.5f[s]" % (exp_time, mod_exp))

            # change the value
            exp_time = mod_exp

        else:
            # Definition of attenuator index
            attfac = AttFactor.AttFactor()
            best_thick = attfac.getBestAtt(cond['wavelength'], best_transmission)
            att_idx = attfac.getAttIndexConfig(best_thick)
            mc.setAttIdx(att_idx)

        # 160618 Added by K. Hirata
        mc.setPrefix(prefix)
        mc.setCrystalID(cond['sample_name'])
        mc.setWL(self.wavelength)
        if self.isBeamsizeIndexOnScheduleFile == True:
            mc.setBeamsizeIndex(beamsize_index)
        mc.setExpTime(exp_time)
        mc.setCameraLength(cond['dist_ds'])
        mc.setScanCondition(phi_start, phi_end, cond['osc_width'])
        mc.setDir(self.multi_dir)
        mc.setShutterlessOn()

        if same_point == False:
            mc.makeMultiDoseSlicing(single_sch, glist, ntimes=cond['ntimes'])
        else:
            mc.makeMultiDoseSlicingAtSamePoint(single_sch, glist, ntimes=cond['ntimes'])

        return single_sch

    # calcExpConds1
    # Important parameters: rot_speed, total_photons, flux_beam, exp_time
    # rot_speed [deg./sec.]
    # total_photons [phs] : total photons for data collection
    # flux_beam [phs/sec.]: photon flux 
    def calcExpConds1(self, wavelength, start_phi, end_phi, osc_width, rot_speed, total_photons, flux_beam):
        attfac = AttFactor.AttFactor()
        # total oscillation range
        total_osc = end_phi - start_phi

        # Multi conditions
        n_frames = int(total_osc / osc_width)
        print("Frame=", n_frames)

        # Total photons/frame
        phs_per_frame = total_photons / float(n_frames)
        print("Aimed flux(%5.2e)/frame: %5.2e" % (total_photons, phs_per_frame))

        # Exposure time for full flux
        ff_exptime = phs_per_frame / flux_beam
        print("Full flux exposure time for aimed photons per frame=%13.8f sec/frame" % ff_exptime)

        # Suitable exposure time range
        # 5 deg/frame FIXED
        exp_time = osc_width / rot_speed
        print("Exposure time = ", exp_time, "secs")
        print("Attenuation factor for this exposure time/frame=", ff_exptime / exp_time)

        trans_ideal = ff_exptime / exp_time

        # Suitable attenuation factor
        att_thick = attfac.getBestAtt(wavelength, trans_ideal)
        trans_real = attfac.calcAttFac(wavelength, att_thick)

        print("%8.1f[um] trans=%12.8f (Aimed trans=%12.8f)" \
              % (att_thick, trans_real, trans_ideal))

        # Final calculation
        exptime_final = ff_exptime / trans_real
        att_idx = attfac.getAttIndexConfig(att_thick)
        print("Initial exposure time = ", exp_time)
        print("Final   exposure time = ", exptime_final)
        print("round %8.5f sec" % (round(exptime_final, 3)))
        photons_real = exptime_final * trans_real * flux_beam * float(n_frames)
        print("Photons/data=%8.3e" % photons_real)

        return att_idx, exptime_final

        # calcExpConds2 2017/07/30 implemented

    # 1A wavelength transmission : observed values should be used for RR experiments
    # Important parameters: rot_speed, total_photons, flux_beam, exp_time
    # rot_speed [deg./sec.]
    # total_photons [phs] : total photons for data collection
    # flux_beam [phs/sec.]: photon flux 
    def calcExpConds2(self, wavelength, start_phi, end_phi, osc_width, rot_speed, total_photons, flux_beam):
        attfac = AttFactor.AttFactor()
        # total oscillation range
        total_osc = end_phi - start_phi

        # Multi conditions
        n_frames = int(total_osc / osc_width)
        print("Frame=", n_frames)

        # Total photons/frame
        phs_per_frame = total_photons / float(n_frames)
        print("Aimed flux(%5.2e)/frame: %5.2e" % (total_photons, phs_per_frame))

        # Exposure time for full flux
        ff_exptime = phs_per_frame / flux_beam
        print("Full flux exposure time for aimed photons per frame=%13.8f sec/frame" % ff_exptime)

        # Suitable exposure time range
        # 5 deg/frame FIXED
        exp_time = osc_width / rot_speed
        print("Exposure time = ", exp_time, "secs")
        print("Attenuation factor for this exposure time/frame=", ff_exptime / exp_time)

        trans_ideal = ff_exptime / exp_time

        # Suitable attenuation factor
        att_thick = attfac.getBestAtt(wavelength, trans_ideal)
        trans_real = attfac.getAttFacObs(wavelength, att_thick)

        print("%8.1f[um] trans=%12.8f (Aimed trans=%12.8f)" \
              % (att_thick, trans_real, trans_ideal))

        # Final calculation
        exptime_final = ff_exptime / trans_real
        att_idx = attfac.getAttIndexConfig(att_thick)
        print("Initial exposure time = ", exp_time)
        print("Final   exposure time = ", exptime_final)
        print("round %8.5f sec" % (round(exptime_final, 3)))
        photons_real = exptime_final * trans_real * flux_beam * float(n_frames)
        print("Photons/data=%8.3e" % photons_real)

        return att_idx, exptime_final

    # I would like to replace this function to calcExpConds series
    def calcExpCondition(self, wavelength, start_phi, end_phi, osc_width, total_photons, flux_beam, exp_time):
        attfac = AttFactor.AttFactor()
        # total oscillation range
        total_osc = end_phi - start_phi

        # Multi conditions
        n_frames = int(total_osc / osc_width)
        print("Frame=", n_frames)

        # Total photons/frame
        phs_per_frame = total_photons / float(n_frames)
        print("Aimed flux/frame: %5.2e" % (phs_per_frame))

        # Exposure time for full flux
        ff_exptime = phs_per_frame / flux_beam
        print("Full flux exposure time for aimed flux=%13.8f sec/frame" % ff_exptime)

        # Suitable exposure time range
        # 5 deg/frame FIXED
        # exptime=osc_width/5.0
        print("Attenuation factor for 1sec exposure/frame", ff_exptime / exp_time)
        transmission = ff_exptime / exp_time

        # Suitable attenuation factor
        att_thick = attfac.getBestAtt(wavelength, transmission)
        trans = attfac.calcAttFac(wavelength, att_thick)

        print("%8.1f[um] Transmission=%12.8f" % (att_thick, trans))

        # Final calculation
        exptime = ff_exptime / trans
        att_idx = attfac.getAttIndexConfig(att_thick)

        return att_idx, exptime

    # 2016/11/20 Single irradiation data collection
    # 2016/12/09 Large modification(commit 68e817e6d9af462d7fb685ce23706fbfcf51dcb2)
    # 2017/07/30 Observed transmission was utilized. This is quite temporal.
    def genSamePhotons(self, wavelength, h_beam, v_beam, start_phi, end_phi, gxyz, osc_width, total_photons, distance,
                       rot_speed=5.0, crystal_id="unknown", prefix="multi"):
        mc = MultiCrystal.MultiCrystal()

        # flux_factor: stored in 'beamsize.config'
        # flux: estimated by flux factor and base-photon flux (TCS 0.1 mm sq beam at BL32XU)
        beam_index, flux_factor, flux = self.beamsizeconf.getBeamParams(h_beam, v_beam)

        # total oscillation range
        total_osc = end_phi - start_phi
        # Caclculate exposure condition 
        # 2016/12/09 added the function: calcExpConds2
        # exposure time is estimated from rotation speed.
        att_idx, real_exptime = self.calcExpConds2(wavelength, start_phi, end_phi, osc_width, rot_speed, total_photons,
                                                   flux)

        # 160618 Added by K. Hirata
        mc.setBeamsizeIndex(beam_index)
        mc.setAttIdx(att_idx)
        mc.setCrystalID(crystal_id)
        mc.setWL(wavelength)
        mc.setExpTime(real_exptime)
        mc.setCameraLength(distance)
        mc.setScanCondition(start_phi, end_phi, osc_width)
        mc.setDir(self.multi_dir)
        mc.setShutterlessOn()
        sch_str = mc.makeSchStrEach(prefix, gxyz)

        return sch_str

    # Rotation speed should be fixed: only attenuator thickness can be modified
    def calcExpCondWithoutModExpTime(self, wavelength, start_phi, end_phi, osc_width, total_photons, flux_beam,
                                     exp_time):
        attfac = AttFactor.AttFactor()
        # total oscillation range
        total_osc = end_phi - start_phi

        # Multi conditions
        n_frames = int(total_osc / osc_width)

        # Total photons/frame
        phs_per_frame = total_photons / float(n_frames)
        print("Aimed flux/frame: %5.2e" % (phs_per_frame))

        # Exposure time for full flux
        ff_exptime = phs_per_frame / flux_beam
        print("Full flux exposure time for aimed flux=%13.8f sec/frame" % ff_exptime)

        # Suitable exposure time range
        print("Attenuation factor for 1sec exposure/frame", ff_exptime / exp_time)
        transmission = ff_exptime / exp_time

        # Suitable attenuation factor
        att_thick = attfac.getBestAtt(wavelength, transmission)
        trans = attfac.calcAttFac(wavelength, att_thick)

        # Final calculation
        att_idx = attfac.getAttIndexConfig(att_thick)

        return att_idx, exp_time

    # 2016/12/04 Rotation speed change
    def genRotSpeed(self, wavelength, h_beam, v_beam, start_phi, end_phi, gxyz, osc_width, total_photons, distance,
                    rot_speed, crystal_id="unknown", prefix="multi"):
        mc = MultiCrystal.MultiCrystal()
        multi_sch = "%s/multi.sch" % self.multi_dir

        beam_index, flux_factor, flux = self.beamsizeconf.getBeamParams(h_beam, v_beam)

        # rotation speed [deg./s]
        exp_time = osc_width / rot_speed
        # EIGER readout time 
        if 1.0 / exp_time > self.max_framerate:
            print("genRotSpeed. Frame rate exceeds the maximum frame rate!!")
            sys.exit(1)

        # total oscillation range
        total_osc = end_phi - start_phi

        # calcExpCondRotSpeed(self,wavelength,start_phi,end_phi,osc_width,total_photons,flux_beam,exp_time):
        att_idx, real_exptime = self.calcExpCondWithoutModExpTime(wavelength, start_phi, end_phi, osc_width,
                                                                  total_photons, flux, exp_time)

        # 160618 Added by K. Hirata
        mc.setBeamsizeIndex(beam_index)
        mc.setAttIdx(att_idx)
        mc.setCrystalID(crystal_id)
        mc.setWL(wavelength)
        mc.setExpTime(real_exptime)
        mc.setCameraLength(distance)
        mc.setScanCondition(start_phi, end_phi, osc_width)
        mc.setDir(self.multi_dir)
        mc.setShutterlessOn()
        sch_str = mc.makeSchStrEach(prefix, gxyz)

        return sch_str

    def genSchedule(self, sch_str):
        mc = MultiCrystal.MultiCrystal()
        multi_sch = "%s/multi.sch" % self.multi_dir

        ofile = open(multi_sch, "w")
        for each_sch in sch_str:
            for line in each_sch:
                ofile.write("%s" % line)
        ofile.close()

        return multi_sch

    # 2016/09/26 Multiple various conditions
    # From one loop: datasets with various conditions
    def genMultiVarious(self, phi_mid, glist, osc_width, total_osc, add_conds,
                        exp_time, distance, crystal_id="unknown", prefix="multi"):

        mc = MultiCrystal.MultiCrystal()
        multi_sch = "%s/multi.sch" % self.multi_dir

        # Multi conditions
        n_frames = int(total_osc / osc_width)
        half_width = total_osc / 2.0
        start_phi = phi_mid - half_width
        end_phi = phi_mid + half_width

        # Various conditions
        # add_conds list of 'exposure time limit'
        # add_conds=[0.0033,0.0066,0.0165,0.033,0.165] # [sec]

        comstr = []
        data_index = 1
        for exp_limit in add_conds:
            attfac = AttFactor.AttFactor()
            best_transmission = exp_limit / float(n_frames) / exp_time
            best_thick = attfac.getBestAtt(self.wavelength, best_transmission)
            print("Suggested Al thickness = %8.1f[um]" % best_thick)
            att_idx = attfac.getAttIndexConfig(best_thick)
            # 160618 Added by K. Hirata
            this_prefix = "%s-%02d" % (prefix, data_index)
            mc.setPrefix(this_prefix)
            mc.setAttIdx(att_idx)
            mc.setCrystalID(crystal_id)
            mc.setWL(self.wavelength)
            mc.setExpTime(exp_time)
            mc.setCameraLength(distance)
            mc.setScanCondition(start_phi, end_phi, osc_width)
            mc.setDir(self.multi_dir)
            mc.setShutterlessOn()
            cstr = mc.makeSchStr(glist)
            comstr.append(cstr)
            data_index += 1

        # print multi_sch
        mf = open(multi_sch, "w")
        for cstr in comstr:
            for line in cstr:
                print(line)
                mf.write("%s" % line)
        return multi_sch

    # 2019/05/22 Largely modified to use KUMA
    def genHelical(self, startphi, endphi, left_xyz, right_xyz, prefix, flux, cond):
        schbss = ScheduleBSS.ScheduleBSS()
        gv = GonioVec.GonioVec()
        self.logger.info("LoopMeasurement.genHelical starts")

        # Total oscillation width
        total_osc = endphi - startphi
        # Number of frames
        stepphi = cond['osc_width']
        nframe = int(total_osc / stepphi)
        ### From KUMA code 2015/12/18
        scanvec = gv.makeLineVec(left_xyz, right_xyz)
        # Distance of this vector [mm] along 'rotation axis'
        dist_vec = np.fabs(scanvec[1])

        if dist_vec < 0.005:
            raise MyException("crystal size is too small for helical data collection")

        nframes_per_point = 1
        while (1):
            # number of irradiation points
            n_irrad = int(float(nframe) / float(nframes_per_point))
            # Scan vector length is divided by number of frames
            # [mm]
            step_length = dist_vec / float(n_irrad)
            # ideal_step_length < 0.5um
            # increase number of frames per irradiation point
            step_um = step_length * 1000.0
            if step_um < 0.5:
                nframes_per_point += 1
            else:
                break

        self.logger.info("Total oscillation range: %12.5f (%5.1f - %5.1f)" % (total_osc, startphi, endphi))
        self.logger.info("Scan vector length: %8.5f [um]" % (dist_vec * 1000.0))

        # Dose estimation
        kuma = KUMA.KUMA()
        # the routine considers 'dose slicing' also
        self.logger.info("Estimate best conditions....")
        # This line is very important for HITO not for HEBI.
        cond['total_osc'] = total_osc

        exp_time, best_transmission = kuma.getBestCondsHelical(cond, flux, dist_vec)
        self.logger.info("Best transmission = %8.2f" % best_transmission)
        self.logger.info("Estimate best ends....")
        ntimes = cond['ntimes']

        # Beam size setting : extracting beamsize index from beamsize.config
        beamsize_index = self.beamsizeconf.getBeamIndexHV(cond['ds_hbeam'], cond['ds_vbeam'])

        if beamline == "BL32XU" or beamline == "BL41XU" or beamline == "BL45XU":
            # Check transmission with 'thinnest attenuator'
            attfac = AttFactor.AttFactor()
            mod_exp, mod_trans = attfac.checkThinnestAtt(cond['wavelength'], exp_time, best_transmission)
            tmp_trans = mod_trans * 100.0
            schbss.setTrans(tmp_trans)  # this is unit of [%]

            # case when the transmission is modified.
            if mod_trans != best_transmission:
                self.logger.info("Transmission is changed : %9.5f   -> %9.5f (Max 1.0 (=100 perc))" % (best_transmission, mod_trans))
                self.logger.info("Exposure     is changed : %9.5f[s]-> %9.5f[s]" % (exp_time, mod_exp))

            # change the value
            exp_time = mod_exp

        else:
            # Attenuation factor setting
            self.logger.info("Attenuator calculation")
            attfac = AttFactor.AttFactor()
            best_thick = attfac.getBestAtt(self.wavelength, best_transmission)
            self.logger.info("Attenuator calculation ends Best= %s" % best_thick)
            self.logger.info("Attenuator index searching")
            self.logger.info("Suggested Al thickness = %8.1f[um] at W.L.=%8.5f A" % (best_thick, self.wavelength))
            att_idx = attfac.getAttIndexConfig(best_thick)
            self.logger.info("Att index is selected as %5d" % att_idx)
            schbss.setAttIdx(att_idx)

        # Condition settings
        # Data directory
        img_dir = "%s/" % (self.multi_dir)
        # print img_dir
        schedule_file = "%s/%s.sch" % (img_dir, prefix)
        self.prepPath(img_dir)
        schbss.setDir(img_dir)
        schbss.setDataName(prefix)
        if self.isBeamsizeIndexOnScheduleFile == True:
            schbss.setBeamsizeIndex(beamsize_index)
        schbss.setOffset(0)
        schbss.setWL(self.wavelength)
        schbss.setExpTime(exp_time)
        schbss.setCameraLength(cond['dist_ds'])
        schbss.setAdvanced(n_irrad, step_length, nframes_per_point)
        schbss.setAdvancedVector(left_xyz, right_xyz)
        schbss.setScanCondition(startphi, endphi, stepphi)

        # ntimes is the number of time of same data collection
        if cond['ntimes'] == 1:
            schbss.make(schedule_file)
        # ntimes > 1
        else:
            schbss.makeMulti(schedule_file, ntimes)

        print("OK")
        return schedule_file

    # 2015/11/26 AM5:15 K.Hirata wrote
    # Vertical scan for each gonio position from 2D raster results
    # phi_start: raster phi start
    # glist: code lists from 2D scan results
    # raster_step: Vertical scan step in [mm]
    # raster_npoints: vertical scan points
    # raster_exp: exposure time in [sec]
    # distance: raster scan camera distance

    # 2015/12/06 modified

    def genVrasterMulti(self, cry_name, phi_start, glist, raster_step, raster_npoints, raster_exp, distance):
        vraster_dir = "%s/%s/" % (self.raster_dir, cry_name)
        multi_sch = "%s/vraster.sch" % (vraseter_dir)
        image_outdir = vraster_dir

        # Vertical scan prefix
        rs = RasterSchedule.RasterSchedule()

        # Conditions for Shutterless vertical scan
        rs.setPrefix(prefix)
        rs.setCL(cond.distance)
        rs.setImgDire(self.raster_dir)
        rs.setStartPhi(phi_start)
        rs.setVertical()
        rs.setVstep(raster_step)
        rs.setVpoints(raster_npoints)
        rs.setHpoints(1)
        rs.setExpTime(raster_exp)
        rs.makeMulti(sc_name, glist)


if __name__ == "__main__":
    import ESA

    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    # ESA
    esa = ESA.ESA("./zoo.db")
    esa.makeTable(sys.argv[1])
    ppp = esa.getDict()

    root_dir = "/isilon/users/t_shimizu_4368/t_shimizu_4368/Junk/junk4/"
    root_dir = "/isilon/users/target/target/AutoUsers/191114/kun/"
    cxyz = [1.7601, -6.1756, 0.6280]
    phi = 0.00
    scan_id = "sample99"
    trayid = 1
    pinid = 1
    beamsize = 10.0

    lm = LoopMeasurement(ms, root_dir, scan_id)

    wavelength = 1.0
    startphi = 0.0
    endphi = 90.0
    osc_width = 0.1
    flux = 1.3E13

    left_xyz = [0.0, 0.0, 0.1]
    right_xyz = [0.0, 0.1, 0.0]
    print(left_xyz, right_xyz)
    prefix = "TEST"

    logfile = open("logfile.log", "w")
    #lm.genHelical(startphi, endphi, left_xyz, right_xyz, prefix, flux, ppp[0], logfile)

    lm.multi_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo"
    glist=[left_xyz, right_xyz]
    cond={'total_osc':10.0,'dist_ds':130.0, 'ds_hbeam':10.0, 'ds_vbeam':10.0, 'osc_width':0.1,'dose_ds':10.0, 'wavelength':1.0,'exp_ds':0.02, 'reduced_fact':1.0, 'sample_name':"TEST",'ntimes':1}
    lm.genMultiSchedule(0.0, glist, cond, flux, prefix="multi")

    ms.close()
