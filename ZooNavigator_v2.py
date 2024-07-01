import sys, os, math, cv2, socket, time, copy
import traceback
import logging
import numpy as np

sys.path.append("/isilon/BL41XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL41XU/BLsoft/PPPP/10.Zoo/")
from MyException import *
import Zoo
import AttFactor
import LoopMeasurement
import BeamsizeConfig
import datetime
import StopWatch
import Device
import HEBI, HITO
import DumpRecover
import AnaHeatmap
import ESA
import KUMA
import CrystalList
import Date
import MyException
from html_log_maker import ZooHtmlLog

import logging
import logging.config

def check_abort(lm):
    print "Abort check"
    ret = lm.isAbort()
    if ret: print "ABORTABORT"
    return ret
# check_abort()

# Version 2.0.0 modified on 2019/07/04 K.Hirata

class ZooNavigator():
    def __init__(self, zoo, ms, esa_csv, is_renew_db=False):
        print "ZooNavigator was called."
        # From arguments
        self.zoo = zoo
        self.esa_csv = esa_csv
        self.ms = ms

        # Device settings
        self.dev = Device.Device(ms)
        self.dev.init()

        # Beam dump treatment
        self.dump_recov = DumpRecover.DumpRecover(self.dev)
        self.recoverOption = False

        # Back img
        self.backimg = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/BackImages/back-1811221806.ppm"

        # Configure directory
        self.config_dir = "/isilon/blconfig/bl41xu/"
        self.config_file = "%s/bss/bss.config" % self.config_dir

        # Attenuator index
        self.att = AttFactor.AttFactor()

        # Limit for raster scan
        self.limit_of_vert_velocity = 500.0  # [um/sec]

        self.logger = logging.getLogger('ZOO').getChild("ZooNavigator")

        self.zooprog = open("/isilon/BL41XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_progress.log", "a")
        self.stopwatch = StopWatch.StopWatch()

        # Data processing file
        self.isOpenDPfile = False

        # Goniometer positions 
        # The values will be updated by the current pin position
        self.sx = -0.5
        self.sy = 1.145
        self.sz = -0.5

        # Goniometer mount position( will be read from BSS configure file)
        self.mx = -0.5
        self.my = 1.145
        self.mz = -0.5

        # DB name
        self.phosec_meas = 0
        # DB is updated or not (using CSV file)
        self.is_renew_db = is_renew_db

        # Background image -> back ground is okay for one capture for each run
        self.isCaptured = False

        # Helical debugging
        self.helical_debug = False

        # Measured flux and Beam size
        self.meas_beamh_list = []
        self.meas_beamv_list = []
        self.meas_flux_list = []
        self.meas_wavelength_list = []

        self.needMeasureFlux = True  # test at 2019/06/18 at BL45XU

        # If BSS can change beamsize via command
        self.doesBSSchangeBeamsize = True

        # For cleaning information
        self.num_pins = 0
        self.n_pins_for_cleaning = 16


    def readZooDB(self, dbfile):
        self.esa = ESA.ESA(dbfile)
        return True

    def prepESA(self, doesExist = False):
        print "Preparation of ZOO database file."
        # Root directory from CSV file
        root_dir = open(sys.argv[1], "r").readlines()[1].split(",")[0]
        if os.path.exists(root_dir) == False:
            os.makedirs(root_dir)
        # zoo.db file check and remake and save
        d = Date.Date()
        time_str = d.getNowMyFormat(option="sec")
        dbfile = "%s/zoo_%s.db" % (root_dir, time_str)
        self.esa = ESA.ESA(dbfile)
        self.esa.makeTable(self.esa_csv, force_to_make=self.is_renew_db)
        return True

    def recoverOptionOn(self):
        self.recoverOption = True

    def rebootVservPC(self):
        command = "ssh 192.168.163.6 \"reboot\""
        os.system(command)

    # 2019/06/11 Simply measure flux
    def measureFlux(self, cond):
        # Wavelength is changed
        en = 12.3984 / cond['wavelength']
        # check energy
        self.checkEnergy(cond, isTune=True)
        # If the flux was measured in this beam sizes
        check_index = 0
        # Beam size for checking whether its flux was measured or not
        beamh = cond['ds_hbeam']
        beamv = cond['ds_vbeam']
        # Checking if the flux was measured or not
        if len(self.meas_beamh_list) != 0:
            for beamh_check, beamv_check, flux_check, wave_check in zip(self.meas_beamh_list, self.meas_beamv_list,
                                                                        self.meas_flux_list, self.meas_wavelength_list):
                if beamh_check == beamh and beamv_check == beamv and wave_check == cond['wavelength']:
                    self.logger.info("The flux has been measured already. Return to the main routine.")
                    nownownow = datetime.datetime.now()
                    logstr = "%s %f(H)[um] x %f(V)[um] PIN PHOSEC=%8.2e phs/sec." % \
                             (nownownow, beamh, beamv, float(flux_check))
                    self.logger.info("%s\n" % logstr)
                    # Now set the measured photon flux to self.phosec_meas
                    self.phosec_meas = flux_check
                    return
        else:
            self.logger.info("The flux has not been measured yet. Now, it will be measured.")

        # unmount current pin
        self.zoo.dismountCurrentPin()

        # Beam size change
        if self.doesBSSchangeBeamsize == True:
            current_beam_index = self.zoo.getBeamsize()
            beamsizeconf = BeamsizeConfig.BeamsizeConfig(self.config_dir)
            beamsize_index = beamsizeconf.getBeamIndexHV(cond['ds_hbeam'], cond['ds_vbeam'])
            if current_beam_index != beamsize_index:
                self.logger.info("Beam size will be changed from now.")
                self.logger.info("Beamsize index = %5d" % beamsize_index)
                self.zoo.setBeamsize(beamsize_index)

        # Measure the flux
        self.phosec_meas = self.dev.measureFlux()
        # Adding measured flux & beam size to the list
        self.meas_beamh_list.append(beamh)
        self.meas_beamv_list.append(beamv)
        self.meas_wavelength_list.append(cond['wavelength'])
        self.meas_flux_list.append(self.phosec_meas)

        # Writing down the log file
        nownownow = datetime.datetime.now()
        self.logger.info("================================================================")
        self.logger.info("-- Flux will be measured at the time when beam size is changed--")
        self.logger.info("================================================================")
        logstr = "%s %f[um] x %f[um] W.L.= %7.5f A. PIN PHOSEC=%8.2e phs/sec." % (nownownow,
                                                                                  cond['ds_hbeam'],
                                                                                  cond['ds_vbeam'],
                                                                                  cond['wavelength'],
                                                                                  self.phosec_meas)
        self.logger.info("%s" % logstr)

    def getBackgroundImage(self):
        self.logger.debug("getBackGroundImage starts..")
        # Check if the pin is mounted or not
        self.zoo.dismountCurrentPin()
        # Background image for centering
        backdir = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/BackImages/"
        self.backimg = "%s/%s" % (backdir, datetime.datetime.now().strftime("back-%y%m%d%H%M.ppm"))
        try:
            self.dev.prepCentering()
            self.logger.debug("Dummy capture for the first image")
            self.dev.capture.capture(self.backimg)
            self.logger.debug("The 2nd image..")
            self.dev.capture.capture(self.backimg)
        except MyException, tttt:
            raise MyException("Capture background file failed")
            sys.exit()
        self.logger.info("New background file has been replaced to %s" % self.backimg)
        self.dev.capture.disconnect()
        self.isCaptured = True
        return self.backimg

    def prepAttCondition(self, cond):
        # Attenuator thickness for raster scan
        att_fact = AttFactor.AttFactor(self.config_file)
        trans = cond['att_raster'] / 100.0
        best_thick = att_fact.getBestAtt(cond['wavelength'], trans)
        self.logger.info("Transmission is set to %5.2f percent" % trans)
        self.att_idx = att_fact.getAttIndexConfig(best_thick)

    def checkEnergy(self, cond, isTune=True):
        # Wavelength is changed
        current_wave = self.zoo.getWavelength()
        measure_wave = cond['wavelength']
        change_flag = False
        self.logger.info("wavelength check: CURR:%8.4f A-> COND:%8.4f A" % (current_wave, measure_wave))
        if math.fabs(current_wave - measure_wave) > 0.0001:
            self.zoo.setWavelength(measure_wave)
            change_flag = True
            self.stopwatch.setTime("last_energy_change")
        # when this is the first pin. Stopwatch should be set also
        elif cond['o_index'] == 0:
            self.stopwatch.setTime("last_energy_change")

        return change_flag

    def goAround(self, zoodb="none"):
        # Common settings
        print "goAround=", zoodb
        if zoodb == "none":
            self.prepESA()
        else:
            self.readZooDB(zoodb)
        # Zoom out
        self.dev.zoom.zoomOut()

        while(1):
            # Get a condition of the most important pin stored in a current zoo.db
            try:
                self.logger.info("Trying to get the prior pin")
                cond = self.esa.getPriorPinCond()
                self.processLoop(cond, checkEnergyFlag=True)
            except:
                message = "All measurements have been finished."
                self.logger.info(message)
                break
        sys.exit()

    def processLoop(self, cond, checkEnergyFlag=False, measFlux=False):
        # Root directory
        root_dir = cond['root_dir']
        # priority index 
        o_index = cond['o_index']

        # self.html_maker = ZooHtmlLog(root_dir, name, online=True)
        # open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s\n"%(name,root_dir))

        # For data processing
        if self.isOpenDPfile == False:
            self.data_proc_file = open("%s/data_proc.csv" % root_dir, "a")
            self.isOpenDPfile = True

        # Check point of 'skipping' this loop
        # check 'isSkip' in zoo.db
        if self.esa.isSkipped(o_index) == True:
            print "o_index=%5d %s-%s is skipped" % (o_index, cond['puckid'], cond['pinid'])
            print "Disconnecting capture"
            self.lm.closeCapture()
            return

        # Write log string
        self.logger.info(">>>> Processing %4s-%2s <<<<" % (cond['puckid'], cond['pinid']))

        # Making root directory
        if os.path.exists(root_dir):
            self.logger.info("%s already exists" % root_dir)
        else:
            self.logger.info("%s is being made now..." % root_dir)
            os.makedirs(root_dir)

        # Getting puck information from SPACE server program
        self.zoo.getSampleInformation()

        # Prep attenuator condition
        # Obsoleted 190711 K.Hirata
        # self.prepAttCondition(cond)

        # Background image should be done for each 'run'
        if self.isCaptured == False:
            self.logger.info("Now a new background image for centering will be captured.")
            self.getBackgroundImage()

        # For each pin, energy is checked.
        # Everytime, energy_change_flag is updated.
        if checkEnergyFlag == True:
            self.logger.info("Wavelength will be checked.")
            energy_change_flag = self.checkEnergy(cond)
            if energy_change_flag == True:
                self.logger.info("Here beam position tuning should be coded.")
            else:
                self.logger.info("Tuning is not required")

        # Beamsize setting
        if self.doesBSSchangeBeamsize == True:
            # Beamsize setting
            current_beam_index = self.zoo.getBeamsize()
            beamsizeconf = BeamsizeConfig.BeamsizeConfig(self.config_dir)
            self.logger.debug("%5.2f %5.2f" % (cond['raster_hbeam'], cond['raster_vbeam']))
            beamsize_index = beamsizeconf.getBeamIndexHV(cond['raster_hbeam'], cond['raster_vbeam'])
            self.logger.info("Current beamsize index= %5d" % current_beam_index)
            if current_beam_index != beamsize_index:
                self.logger.info("Beamsize index = %5d" % beamsize_index)
                self.zoo.setBeamsize(beamsize_index)

        self.logger.info("Beam size for raster scan= %5.2f(H) x %5.2f(V) [um^2]"% (cond['raster_hbeam'], cond['raster_vbeam']))

        # Making
        # try: self.html_maker.add_condition(cond)
        # except: print traceback.format_exc()

        if self.needMeasureFlux == True:
            self.measureFlux(cond)
            # Recording flux value to ZOODB
            self.esa.updateValueAt(o_index, "flux", self.phosec_meas)
        elif self.helical_debug == True:
            self.phosec_meas = 1E13  # 2019/05/24 K.Hirata

        # 2019/04/21 Measuring flux should be skipped now
        # Beamsize should be changed via BSS
        else:
            self.logger.info("Skipping measuring flux")
            # self.measureFlux(cond)

        # Experiment
        trayid = cond['puckid']
        pinid = cond['pinid']

        prefix = "%s-%02d" % (trayid, pinid)
        self.logger.info("Processing pin named %s" % prefix)

        # Loop measurement class initialization
        self.lm = LoopMeasurement.LoopMeasurement(self.ms, root_dir, prefix)

        # Making directories
        # d_index was defined as 'the newest directory number' of scan??/data??.
        d_index = self.lm.prepDataCollection()
        # n_mount is not useful then 'directory index' is stored to 'n_mount'

        self.esa.updateValueAt(o_index, "n_mount", d_index)
        self.esa.addEventTimeAt(o_index, "meas_start")

        # Setting wavelength for schedule file
        self.lm.setWavelength(cond['wavelength'])

        # Mount position of SPACE (copy from Loopmeasurement)
        self.logger.debug("INOCC get")
        self.mx = self.lm.inocc.mx
        self.my = self.lm.inocc.my
        self.mz = self.lm.inocc.mz

        self.logger.info("Mounting sample starts.")
        self.esa.addEventTimeAt(o_index, "mount_start")
        try:
            self.zoo.mountSample(trayid, pinid)
        except MyException, ttt:
            self.logger.info("Failed to mount a sample pin:%s" % ttt)
            msg = "%s : Sample mount failed!!" % self.stopwatch.getNowStr()
            # Accident case
            if ttt.rfind('-1005000003') != -1:
                message = "SPACE accident occurred! Please contact a beamline scientist."
                self.esa.updateValueAt(o_index, "log_mount", msg)
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.logger.critical(message)
                self.esa.updateValueAt(o_index, "isDone", 9999)
                sys.exit()
            elif ttt.rfind('-1005100001') != -1:
                message = "WARNING!! Please check the pin (%s - %s)" % (trayid, pinid)
                self.logger.warning(message)
                self.esa.updateValueAt(o_index, "log_mount", msg)
                self.zoo.skipSample()
                self.logger.info("Go to the next sample...")
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.esa.updateValueAt(o_index, "isDone", 5001)
                return
            else:
                message = "Unknown Exception: %s. Program terminates" % ttt
                self.logger.error(message)
                self.esa.updateValueAt(o_index, "isDone", 9998)
                sys.exit()
            return
        # Succeeded
        self.logger.info("Mount is finished")
        self.esa.incrementInt(o_index, "isMount")
        self.esa.addEventTimeAt(o_index, "mount_end")

        # Preparation for centering
        self.lm.prepCentering()

        # Move Gonio XYZ to the previous pin
        # if the previous pin Y position moves larger than 3.0mm from
        # the initial Y position, this code resets the Y position to
        # the initial one.
        if np.fabs(self.sy - self.my) > 4.0:
            print "SY value will be modified from %8.3f" % self.sy
            print "New value is got from mount position: %9.4f)" % self.my
            self.sy = self.my

        # Check point of 'skipping' this loop
        # check 'isSkip' in zoo.db
        if self.esa.isSkipped(o_index) == True:
            self.logger.info("o_index=%5d %s-%s is skipped" % (o_index, cond['puckid'], cond['pinid']))
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        #### Centering
        # 2015/11/21 Loop size can be set
        self.esa.addEventTimeAt(o_index, "center_start")
        try:
            print "move to the save point "
            print self.sx, self.sy, self.sz
            self.lm.moveGXYZphi(self.sx, self.sy, self.sz, 0.0)
            self.logger.info("ZooNavigator starts centering procedure...")
            height_add = 0.0
            self.rwidth, self.rheight = self.lm.centering(
                self.backimg, cond['loopsize'], offset_angle=cond['offset_angle'],
                height_add=height_add)
            self.center_xyz = self.dev.gonio.getXYZmm()
            self.logger.info("ZooNavigator finished centering procedure...")
            self.esa.incrementInt(o_index, "isLoopCenter")
            self.esa.updateValueAt(o_index, "scan_height", self.rheight)
            self.esa.updateValueAt(o_index, "scan_width", self.rwidth)

        except MyException, ttt:
            self.logger.error("failed in centering")
            self.logger.error("Go to next sample")
            self.esa.updateValueAt(o_index, "isLoopCenter", -9999)
            self.esa.updateValueAt(o_index, "isDone", 5002)
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.error("close Capture instance")
            self.lm.closeCapture()
            return

        #### /Centering
        # Succeeded
        self.esa.addEventTimeAt(o_index, "center_end")
        self.zooprog.flush()

        # Save Gonio XYZ to the previous pins
        self.sx, self.sy, self.sz, sphi = self.lm.saveGXYZphi()

        # Capture the crystal image before experiment
        self.logger.info("ZooNavigator is capturing the 'before.ppm'")
        capture_name = "before.ppm"
        self.lm.captureImage(capture_name)

        # Dump check and wait
        # if the routine recovers MBS/DSS status, 'False' flag
        # is received here. In this case, tuning was conducted
        # with TCS 0.1mm square. Then, beamsize should be recovered.
        if self.recoverOption == True:
            if self.dump_recov.checkAndRecover(cond['wavelength']) == False:
                # 2019/04/21 K.Hirata Skipped at BL45XU
                # self.bsc.changeBeamsizeHV(cond['raster_hbeam'],cond['raster_vbeam'])
                print "skipping change beam size"

        # Check point of 'skipping' this loop
        # check 'isSkip' in zoo.db
        if self.esa.isSkipped(o_index) == True:
            self.logger.info("o_index=%5d %s-%s is skipped" % (o_index, cond['puckid'], cond['pinid']))
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        self.logger.info("ZooNavigator starts MODE=%s" % (cond['mode']))
        if cond['mode'] == "multi":
            self.collectMulti(trayid, pinid, prefix, cond, sphi)
        elif cond['mode'] == "helical":
            self.collectHelical(trayid, pinid, prefix, cond, sphi)
        elif cond['mode'] == "mixed":
            self.collectMixed(trayid, pinid, prefix, cond, sphi)
        elif cond['mode'] == "single":
            self.collectSingle(trayid, pinid, prefix, cond, sphi)
        elif cond['mode'] == "ssrox":
            self.collectSSROX(cond, sphi)
        elif cond['mode'] == "screening":
            self.collectScreen(cond, sphi)

        self.num_pins += 1
        # cleaning
        if self.num_pins % self.n_pins_for_cleaning ==0:
            self.zoo.cleaning()
            self.zoo.waitTillReady()

        self.esa.addEventTimeAt(o_index, "meas_end")
        self.zooprog.flush()

    def finishZoo(self):
        open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s finished\n" \
                                                                          % (self.name, self.root_dir))

    def collectMulti(self, trayid, pinid, prefix, cond, sphi):
        o_index = cond['o_index']

        # Multiple crystal mode
        # For multiple crystal : 2D raster
        # if centering was skipped this is required
        self.lm.raster_start_phi = sphi

        scan_id = "2d"
        scan_mode = "2D"
        scanv_um = self.rheight
        scanh_um = self.rwidth
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']

        raster_schedule, raster_path = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                            scanv_um, scanh_um, vstep_um, hstep_um,
                                                            sphi, cond)
        raster_start_time = time.localtime()
        self.esa.addEventTimeAt(o_index, "raster_start")
        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "raster_end")
        # Flag on
        self.esa.incrementInt(o_index, "isRaster")

        # Analyzing raster scan results
        try:
            glist = []
            cxyz = self.sx, self.sy, self.sz
            scan_id = self.lm.prefix
            # Crystal size setting
            raster_hbeam = cond['raster_hbeam']
            raster_vbeam = cond['raster_vbeam']

            # getSortedCryList copied from HEBI.py
            # Size of crystals?
            cxyz = 0, 0, 0
            ahm = AnaHeatmap.AnaHeatmap(raster_path, cxyz, sphi)
            min_score = cond['score_min']
            max_score = cond['score_max']
            ahm.setMinMax(min_score, max_score)

            # Crystal size setting
            cry_size_mm = cond['cry_max_size_um'] / 1000.0  # [mm]
            # Analyze heatmap and get crystal list
            crystal_array = ahm.searchMulti(scan_id, cry_size_mm)
            crystals = CrystalList.CrystalList(crystal_array)
            glist = crystals.getSortedPeakCodeList()

            # Limit the number of crystals
            maxhits = cond['maxhits']
            if len(glist) > maxhits:
                glist = glist[:maxhits]

            # number of found crystals
            n_crystals = len(glist)
            self.esa.updateValueAt(o_index, "nds_multi", n_crystals)

            # Writing down the goniometer coordinate list
            gfile = open("%s/collected.dat" % self.lm.raster_dir, "w")
            gfile.write("# Found crystals = %5d\n" % n_crystals)
            for gxyz in glist:
                x, y, z = gxyz
                gfile.write("%8.4f %8.4f %8.4f\n" % (x, y, z))
            gfile.close()

            self.zooprog.flush()

        except MyException, tttt:
            print "Skipping this loop!!"
            self.zooprog.write("\n")
            self.zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print "Disconnecting capture"
            self.lm.closeCapture()
            return

        finally:
            try:
                print "FINALLY"
                # nhits = len(glist)
                # self.html_maker.add_result(puckname=trayid, pin=pinid,
                # h_grid=self.lm.raster_n_width, v_grid=self.lm.raster_n_height,
                # nhits=nhits, shika_workdir=os.path.join(self.lm.raster_dir, "_spotfinder"),
                # prefix=self.lm.prefix, start_time=raster_start_time)
                # self.html_maker.write_html()
            except:
                print traceback.format_exc()

        if len(glist) == 0:
            print "Skipping this loop!!"
            self.esa.updateValueAt(o_index, "isDone", 4001)
            # Disconnecting capture in this loop's 'capture' instance
            print "Disconnecting capture"
            self.lm.closeCapture()
            return

        # Data collection
        time.sleep(0.1)
        data_prefix = "%s-%02d-multi" % (trayid, pinid)

        # Photon flux is extracted from beamsize.config
        if self.phosec_meas == 0.0:
            beamsizeconf = BeamsizeConfig.BeamsizeConfig(self.config_dir)
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.zooprog.write("Flux value is read from beamsize.conf: %5.2e\n"% flux)
        else:
            flux = self.phosec_meas
            self.zooprog.write("Multi: Beam size = %5.2f %5.2f um Measured flux : %5.2e\n" % (cond['ds_hbeam'], cond['ds_vbeam'], flux))

        # For dose estimation
        print "Beam size = ", cond['ds_hbeam'], cond['ds_vbeam'], " [um]"
        print "Photon flux=%8.3e" % flux

        # Generate Schedule file
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond, flux, self.zooprog, prefix=data_prefix)
        # def genMultiSchedule(self, phi_mid, glist, cond, flux, logfile, prefix="multi"):

        time.sleep(0.1)

        self.esa.addEventTimeAt(o_index, "ds_start")
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.esa.incrementInt(o_index, "isDS")
        self.esa.updateValueAt(o_index, "isDone", 1)

        # Writing CSV file for data processing
        sample_name = cond['sample_name']
        prefix = "%s-%02d" % (trayid, pinid)
        root_dir = cond['root_dir']
        self.data_proc_file.write("%s/_kamoproc/%s/,%s,no\n" % (root_dir, prefix, sample_name))
        self.data_proc_file.flush()

        # Writing Time table for this data collection
        # logstr="%6.1f "%(t_for_ds)
        # self.zooprog.write("%s\n"%logstr)
        # self.zooprog.flush()
        # Disconnecting capture in this loop's 'capture' instance
        print "Disconnecting capture"
        self.lm.closeCapture()

    # Collect single
    def collectSingle(self, trayid, pinid, prefix, cond, sphi):
        o_index = cond['o_index']

        # 2D raster
        # if centering was skipped this is required
        self.lm.raster_start_phi = sphi

        scan_id = "2d"
        scan_mode = "2D"
        scanv_um = self.rheight
        scanh_um = self.rwidth
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']
        schfile, raspath = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                scanv_um, scanh_um, vstep_um, hstep_um, sphi, cond)
        self.logger.debug("HEREHERE")

        self.esa.addEventTimeAt(o_index, "raster_start")
        self.logger.debug("Running raster scan..")
        self.zoo.doRaster(schfile)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "raster_end")
        # Flag on
        self.esa.incrementInt(o_index, "isRaster")
        self.logger.info("Raster scan has been finished. Analyzing the result...")

        # Raster scan results and determine the vertical scan point
        try:
            glist = []
            scan_id = self.lm.prefix

            # Analyze heatmap and get crystal list
            self.logger.info("SHIKA heatmap will be analyzed from now..")
            ahm = AnaHeatmap.AnaHeatmap(raspath, self.center_xyz, sphi)
            min_score = cond['score_min']
            max_score = cond['score_max']
            ahm.setMinMax(min_score, max_score)
            crystal_array = ahm.searchPixelBunch(scan_id, naname_include=True)
            self.logger.info("SHIKA heatmap has been analyzed.")

            if len(crystal_array) == 0:
                self.logger.info("No crystals were found on this loop. Break a main loop.")
                self.logger.info("Skipping this loop: diffraction based centering loop.")
                self.esa.updateValueAt(o_index, "isDone", 4005)
                # Disconnecting capture in this loop's 'capture' instance
                self.logger.info("Disconnecting capture")
                self.lm.closeCapture()
                return

            crystals = CrystalList.CrystalList(crystal_array)
            raster_cxyz = crystals.getBestCrystalCode()

            ###############################################
            # all ID beamlines : okay for using this function
            def getRescanLeftDist(index):
                gaburiyoru_h_length = 10.0  # [um]
                gaburiyoru_mm = gaburiyoru_h_length / 1000.0  # [mm]
                y_abs = float(index) * gaburiyoru_mm
                return -1.0 * y_abs

            ##############################################
            self.logger.info("Vertical scan will be started.\n")
            initial_left_y = raster_cxyz[1]
            vertical_index = 0
            final_cxyz = 0, 0, 0
            n_try = 5
            while (True):
                self.logger.info("Vertical scan loop..")
                # Vertical scan
                phi_lv = sphi + 90.0
                v_prefix = "v%02d" % vertical_index
                step_diff = getRescanLeftDist(vertical_index)
                mod_y = initial_left_y + step_diff
                mod_xyz = raster_cxyz[0], mod_y, raster_cxyz[2]
                print "MOD_XYZ=", mod_xyz
                self.logger.info(
                    "Left v scan is started at %9.4f %9.4f %9.4f\n" % (mod_xyz[0], mod_xyz[1], mod_xyz[2]))
                scan_mode = "Vert"
                scanv_um = 1000.0
                scanh_um = 10.0
                vstep_um = cond['raster_vbeam'] / 2.0
                hstep_um = cond['raster_hbeam']
                ###
                exp_origin = cond['exp_raster']
                att_origin = cond['att_raster']
                vert_velocity = vstep_um / exp_origin
                if vert_velocity > self.limit_of_vert_velocity:
                    exp_mod = vstep_um / self.limit_of_vert_velocity
                else:
                    exp_mod = exp_origin
                # Attenuation factor should be more for 'longer' exposure time
                factor_increase_exp = exp_mod / exp_origin
                # DB information should be overwritten
                cond['exp_raster'] = exp_mod
                self.logger.info("Exposure time is changed from %8.3f [sec] to %8.3f [sec]\n" % (exp_origin, exp_mod))
                # Attenuation factor in [%]
                att_raster = att_origin / factor_increase_exp
                self.logger.info(
                "Attenuation %8.3f [percent] is replaced by %8.3f [percent]\n" % (att_origin, att_raster))
                cond['att_raster'] = att_raster
                schfile, raspath = self.lm.rasterMaster(v_prefix, "Vert", mod_xyz,
                                                        scanv_um, scanh_um, vstep_um, hstep_um, phi_lv, cond)
                self.zoo.doRaster(schfile)
                self.zoo.waitTillReady()
                self.esa.addEventTimeAt(o_index, "raster_end")

                try:
                    # Final analysis for vertical scan
                    # Analyze heatmap and get crystal list
                    ahm = AnaHeatmap.AnaHeatmap(raspath, mod_xyz, phi_lv)
                    # Minimum score is set to 3
                    min_score = 5
                    max_score = cond['score_max']
                    ahm.setMinMax(min_score, max_score)
                    crystal_array = ahm.searchPixelBunch(v_prefix, naname_include=True)
                    crystals = CrystalList.CrystalList(crystal_array)
                    final_cxyz = crystals.getBestCrystalCode()
                except:
                    print "Analyze vertical scans failed.\n"
                    self.zooprog.write("ZN.collectSingle: Left vertical scan analysis failed.\n")
                    vertical_index += 1
                    if vertical_index > n_try:
                        self.logger.info("Failed to find crystal in vertical scan.")
                        self.logger.info("Skipping this loop: diffraction based centering loop.")
                        self.esa.updateValueAt(o_index, "isDone", 4006)
                        # Disconnecting capture in this loop's 'capture' instance
                        self.logger.info("Disconnecting capture")
                        self.lm.closeCapture()
                        return
                    else:
                        continue
                if final_cxyz[0] != 0.0:
                    break

            glist.append(final_cxyz)
            # Writing down the goniometer coordinate list
            gfile = open("%s/final_code.dat" % self.lm.raster_dir, "w")
            gfile.write("%8.4f %8.4f %8.4f\n" % (raster_cxyz[0], raster_cxyz[1], raster_cxyz[2]))
            gfile.close()

        # Raster scan failed
        except MyException as message:
            self.logger.info("Caught error: %s "% message)
            self.logger.info("Skipping this loop: diffraction based centering loop.")
            self.esa.updateValueAt(o_index, "isDone", 4002)
            self.zooprog.write("\n")
            self.zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            self.zooprog.flush()
            return

        # Data collection
        # Why is this wait required?
        time.sleep(0.1)
        data_prefix = "%s-%02d-single" % (trayid, pinid)

        # Dose to limit exposure time
        kuma = KUMA.KUMA(self.zooprog)

        # Photon flux is extracted from beamsize.config
        if self.phosec_meas == 0.0:
            beamsizeconf = BeamsizeConfig.BeamsizeConfig(self.config_dir)
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.zooprog.write("Flux value is read from beamsize.conf: %5.2e\n"% flux)
            self.logger.info()
        else:
            flux = self.phosec_meas
            self.zooprog.write("Single: Beam size = %5.2f %5.2f um Measured flux : %5.2e\n" % (cond['ds_hbeam'], cond['ds_vbeam'], flux))

        # Exposure time limit from the dose and photon flux and energy
        print "Beam size = ", cond['ds_hbeam'], cond['ds_vbeam'], " [um]"
        print "Photon flux=%8.3e" % flux
        exp_limit = kuma.convDoseToExptimeLimit(cond['dose_ds'], cond['ds_vbeam'], cond['ds_hbeam'], flux,
                                                cond['wavelength'])

        # Generate Schedule file
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond, flux, self.zooprog, prefix=data_prefix)
        # def genMultiSchedule(self, phi_mid, glist, cond, flux, logfile, prefix="multi"):

        # Why is this wait required?
        # For waiting the schedule file???
        time.sleep(0.1)

        self.esa.addEventTimeAt(o_index, "ds_start")
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.esa.incrementInt(o_index, "isDS")
        self.esa.updateValueAt(o_index, "isDone", 1)

        # Disconnecting capture in this loop's 'capture' instance
        print "Disconnecting capture"
        self.lm.closeCapture()

    # collectSingle

    # 2018/04/13 modified for DB-based measurement
    # 2018/12/15 modified for stop watching
    def collectHelical(self, trayid, pinid, prefix, cond, sphi):
        o_index = cond['o_index']
        # Beamsize
        print "now moving to the beam size to raster scan..."
        print "Liar: beam size should be changed by BSS"
        # self.bsc.changeBeamsizeHV(cond['raster_hbeam'],cond['raster_vbeam'])

        # Initial 2D scan 
        scan_id = "2d"
        gxyz = self.sx, self.sy, self.sz
        # Scan step is set to the same to the beam size
        # Experimental settings
        scan_mode = "2D"
        scanv_um = self.rheight
        scanh_um = self.rwidth
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']

        schfile, raspath = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                scanv_um, scanh_um, vstep_um, hstep_um,
                                                sphi, cond)

        self.esa.addEventTimeAt(o_index, "raster_start")
        self.zoo.doRaster(schfile)
        self.zoo.waitTillReady()
        self.esa.incrementInt(o_index, "isRaster")
        self.esa.addEventTimeAt(o_index, "raster_end")

        # photon flux
        if self.phosec_meas == 0.0:
            beamsizeconf = BeamsizeConfig.BeamsizeConfig(self.config_dir)
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.logger.info("Flux value is read from beamsize.conf: %5.2e" % flux)
        else:
            flux = self.phosec_meas
            self.logger.info("Helical: Beam size = %5.2f %5.2f um Measured flux : %5.2e" % (cond['ds_hbeam'], cond['ds_vbeam'], flux))

        # HEBI instance
        hebi = HEBI.HEBI(self.zoo, self.lm, self.zooprog, self.stopwatch, flux)

        # Log for dose
        self.logger.info("Dose limit  = %3.1f[MGy]" % cond['dose_ds'])
        n_crystals = 0
        try:
            self.esa.addEventTimeAt(o_index, "ds_start")
            # Processing all found crystals for helical data collections
            n_crystals = hebi.mainLoop(raspath, scan_id, sphi, cond, precise_face_scan=False)
            if n_crystals > 0:
                self.esa.incrementInt(o_index, "isDS")
                self.esa.updateValueAt(o_index, "isDone", 1)
                # Update the database
                self.esa.updateValueAt(o_index, "nds_helical", n_crystals)
            else:
                self.logger.info("No crystals were found in HEBI.")
                self.esa.updateValueAt(o_index, "isDone", 4003)
            # Log file for time stamp
            self.esa.addEventTimeAt(o_index, "ds_end")
            self.zooprog.write("helical end\n")
        except:
            self.zooprog.write("ZooNavigator.collectHelical failed.")
            self.esa.updateValueAt(o_index, "isDone", 4004)
        self.lm.closeCapture()

    def collectMixed(self, trayid, pinid, prefix, cond, sphi):
        # Pin index
        o_index = cond['o_index']
        # Beamsize
        print "now moving to the beam size to raster scan..."
        # Specific code for BL41XU and obsoleted temporally on 2019/06/03
        #self.bsc.changeBeamsizeHV(cond['raster_hbeam'], cond['raster_vbeam'])

        # Initial 2D scan 
        scan_id = "2d"
        gxyz = self.sx, self.sy, self.sz

        # Scan step is set to the same to the beam size
        # Experimental settings
        scan_mode = "2D"
        scanv_um = self.rheight
        scanh_um = self.rwidth
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']

        schfile, raspath = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                scanv_um, scanh_um, vstep_um, hstep_um,
                                                sphi, cond)
        # Raster start
        self.esa.addEventTimeAt(o_index, "raster_start")
        self.zoo.doRaster(schfile)
        self.zoo.waitTillReady()
        self.esa.incrementInt(o_index, "isRaster")
        self.esa.addEventTimeAt(o_index, "raster_end")

        # HITO instance
        # __init__(self,zoo,lm,cxyz_2d,phi_face,hbeam,vbeam):
        hito = HITO.HITO(self.zoo, self.lm, gxyz, sphi, cond['raster_hbeam'], cond['raster_vbeam'])
        hito.setHelicalCrystalSize(cond['hel_min_size'], cond['hel_max_size'])
        hebi = HEBI.HEBI(self.zoo, self.lm, gxyz, sphi, cond['wavelength'], numCry=cond['maxhits'],
                         scan_dist=cond['dist_raster'])
        hebi.setTrans(cond['hebi_att'])

        # What does this mean???? 2018/04/14 K.Hirata
        # Distance for searching near grids in the heat map of 2D raster scan
        # Raster beam size should be noted here 2018/04/14 K.Hirata
        # This should be largely modified 
        if cond['raster_hbeam'] > cond['raster_hbeam']:
            crysize = (cond['raster_hbeam'] + 1.000) / 1000.0  # [mm]
        else:
            crysize = (cond['raster_vbeam'] + 1.000) / 1000.0  # [mm]
        print "Crystal size is set to %8.2f[mm]" % crysize

        raster_path = "%s/%s/scan/%s/" % (cond['root_dir'], prefix, scan_id)

        single_crys, heli_crys, perfect_crys = hito.shiwakeru(raspath, scan_id, min_score=cond['score_min'],
                                                              max_score=cond['score_max'], crysize=crysize,
                                                              max_ncry=cond['maxhits'])

        print "MULTIPLE SMALL WEDGE =", len(single_crys)
        print "HELICAL              =", len(heli_crys)
        print "PERFECT HELICAL      =", len(perfect_crys)

        # Multi data collection
        # Precise centering
        # Making gonio list
        glist = []
        for cry in single_crys:
            cry.setDiffscanLog(raspath)
            gxyz = cry.getPeakCode()
            gx, gy, gz = gxyz
            glist.append((gx, gy, gz))

        data_prefix = "%s-%02d-multi" % (trayid, pinid)
        # Exposure time limit from the dose and photon flux and energy
        print "Beam size = ", cond['ds_hbeam'], cond['ds_vbeam'], " [um]"
        print "Photon flux=%8.3e" % flux
        exp_limit = kuma.convDoseToExptimeLimit(cond['dose_ds'], cond['ds_vbeam'], cond['ds_hbeam'], flux,
                                                cond['wavelength'])

        # Generate Schedule file
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond['osc_width'], cond['total_osc'],
                                             exp_limit, cond['exp_ds'], cond['dist_ds'], cond['sample_name'],
                                             prefix=data_prefix)
        time.sleep(0.1)

        self.esa.addEventTimeAt(o_index, "ds_start")
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()

        # hbeam_um, vbeam_um : helical beam size
        # phosec: photon flux of this beam size
        # exptime: exposure time for each frame
        # distance: camera distance
        # Dose to photon density limit
        kuma = KUMA.KUMA(self.zooprog)
        photon_density_limit = kuma.convDoseToDensityLimit(cond['dose_ds'], cond['wavelength'])
        self.zooprog.write("Dose limit  = %3.1f[MGy]\n" % cond['dose_ds'])
        self.zooprog.write("Photonlimit = %6.1e[phs/um^2]\n" % photon_density_limit)
        self.zooprog.flush()

        # This is the most important limit definition for helical data collections
        hebi.setPhotonDensityLimit(photon_density_limit)

        # Processing all found crystals for helical data collections
        # For 'good' crystals
        hebi.roughEdgeHelical(heli_crys, raspath, cond['ds_hbeam'], cond['ds_vbeam'],
                              self.phosec_meas, cond['exp_ds'], cond['dist_ds'], cond['hel_part_osc'],
                              cond['osc_width'],
                              self.zooprog, cond['ntimes'], cond['reduced_fac'], ds_index=0)

        # For 'perfect' crystals
        # Name for scan should be changed for avoiding overwriting the scan files
        hebi.roughEdgeHelical(heli_crys, raspath, cond['ds_hbeam'], cond['ds_vbeam'],
                              self.phosec_meas, cond['exp_ds'], cond['dist_ds'], cond['hel_full_osc'],
                              cond['osc_width'],
                              self.zooprog, cond['ntimes'], cond['reduced_fac'], ds_index=1)

        self.lm.closeCapture()

        # Log file for time stamp
        self.esa.incrementInt(o_index, "isDS")
        self.esa.addEventTimeAt(o_index, "ds_end")

        self.zooprog.write("mixed end\n")

    def collectSSROX(self, cond, sphi):
        # Pin index
        o_index = cond['o_index']
        trayid = cond['puckid']
        pinid = cond['pinid']
        prefix = "%s-%02d" % (trayid, pinid)
        scan_id = "ssrox"
        self.rheight
        raster_schedule, raster_path = self.lm.prepRotRaster(scan_id, self.center_xyz, sphi, cond)
        self.esa.addEventTimeAt(o_index, "ds_start")

        # Do the raster scan with rotation
        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.esa.incrementInt(o_index, "isDS")
        print "Disconnecting capture"
        self.lm.closeCapture()

    def collectScreen(self, cond, sphi):
        # Pin index
        o_index = cond['o_index']
        trayid = cond['puckid']
        pinid = cond['pinid']
        prefix = "%s-%02d" % (trayid, pinid)

        # Multiple crystal mode
        # For multiple crystal : 2D raster
        # if centering was skipped this is required
        self.lm.raster_start_phi = sphi
        scan_id = "2d"
        scan_mode = "2D"
        scanv_um = self.rheight
        scanh_um = self.rwidth
        vstep_um = cond['raster_vbeam']
        hstep_um = cond['raster_hbeam']

        # Full frame scan : roi_index = 0
        raster_schedule, raster_path = self.lm.rasterMaster(scan_id, scan_mode, cond['raster_vbeam'],
                                                            cond['raster_hbeam'], scanv_um,
                                                            scanh_um, vstep_um, hstep_um, self.center_xyz, sphi,
                                                            att_idx=self.att_idx, distance=cond['dist_raster'],
                                                            exptime=cond['exp_raster'], roi_index = 0)

        raster_start_time = time.localtime()
        self.esa.addEventTimeAt(o_index, "raster_start")
        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "raster_end")
        # Flag on
        self.esa.incrementInt(o_index, "isRaster")

        # Analyzing raster scan results
        try:
            glist = []
            cxyz = self.sx, self.sy, self.sz
            scan_id = self.lm.prefix
            # Crystal size setting
            raster_hbeam = cond['raster_hbeam']
            raster_vbeam = cond['raster_vbeam']

            # getSortedCryList copied from HEBI.py
            # Size of crystals?
            cxyz = 0, 0, 0
            ahm = AnaHeatmap.AnaHeatmap(raster_path, cxyz, sphi)
            min_score = cond['score_min']
            max_score = cond['score_max']
            ahm.setMinMax(min_score, max_score)

            # Crystal size setting
            cry_size_mm = cond['cry_max_size_um'] / 1000.0  # [mm]
            # Analyze heatmap and get crystal list
            crystal_array = ahm.searchMulti(scan_id, cry_size_mm)
            crystals = CrystalList.CrystalList(crystal_array)
            glist = crystals.getSortedPeakCodeList()

            # Writing down the goniometer coordinate list
            gfile = open("%s/crystal_candidates.dat" % self.lm.raster_dir, "w")
            gfile.write("# Found crystals = %5d\n" % n_crystals)
            for gxyz in glist:
                x, y, z = gxyz
                gfile.write("%8.4f %8.4f %8.4f\n" % (x, y, z))
            gfile.close()
            self.zooprog.flush()

        except MyException, tttt:
            print "Skipping this loop!!"
            self.zooprog.write("\n")
            self.zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print "Disconnecting capture"
            self.lm.closeCapture()
            return

        finally:
            try:
                print "FINALLY"
                # Disconnecting capture in this loop's 'capture' instance
                print "Disconnecting capture"
                self.lm.closeCapture()
                return
            except:
                print traceback.format_exc()
