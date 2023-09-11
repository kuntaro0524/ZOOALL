import sys, os, math, cv2, socket, time, copy
import traceback
import logging
import numpy as np

beamline = "BL32XU"

from MyException import *
import Zoo
import AttFactor
import LoopMeasurement
import BeamsizeConfig
import datetime
import StopWatch
import Device
import HEBI
import DumpRecover
import AnaHeatmap
import ESA
import KUMA
import CrystalList
import Date
import DiffscanMaster
from html_log_maker import ZooHtmlLog

import logging
import logging.config

from configparser import ConfigParser, ExtendedInterpolation

def check_abort(lm):
    print("Abort check")
    ret = lm.isAbort()
    if ret: print("ABORTABORT")
    return ret

# Version 2.1.0 modified on 2019/07/04 K.Hirata
# Version 2.1.1 modified on 2019/07/23 K.Hirata
# Version 2.1.2 modified on 2019/10/26 K.Hirata at BL45XU

class ZooNavigator():
    def __init__(self, zoo, ms, esa_csv, is_renew_db=False):
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
        self.backimg = "dummy.ppm"

        # BSS configure file path
        # beamline.ini から読み込む 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
        self.config_file = self.config.get("files", "bssconfig_file")
        # directory to store background images.
        self.backimage_dir = self.config.get("dirs", "backimage_dir")

        # beamline name is read from 'beamline.ini'
        # section:beamline, option: beamline
        self.beamline = self.config.get("beamline", "beamline")

        # Attenuator index
        self.att = AttFactor.AttFactor()

        # Limit for raster scan
        self.limit_of_vert_velocity = 400.0  # [um/sec]

        self.logger = logging.getLogger('ZOO').getChild("ZooNavigator")

        self.stopwatch = StopWatch.StopWatch()

        # Data processing file
        self.isOpenDPfile = False

        # Checking data processing file
        self.isDPheader = False

        # Goniometer positions 
        # The values will be updated by the current pin position
        self.sx = -1.5089
        self.sy = 0.5714
        self.sz = -0.3183

        # Goniometer mount position( will be read from BSS configure file)
        self.mx = -1.5089
        self.my = 0.5714
        self.mz = -0.3183

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
        self.cleaning_interval_hours = 1.0  # [hour]
        self.time_for_elongation = 0.0  # [sec]

        # Bukkake & capture
        self.isZoomCapture = True

        # Time limit
        self.time_limit_ds = 9999  # [hours]

        # Flag for 10um raster scan at BL45XU
        self.flag10um_raster = False
        self.min_beamsize_10um_raster = 20.0

        # isDark flag : read from 'beamline.ini'
        # section: special_setting, option: isDark, value: boolean
        self.isDark = self.config.getboolean("special_setting", "isDark")

    def readZooDB(self, dbfile):
        self.esa = ESA.ESA(dbfile)
        return True

    def setTimeLimit(self, time_hours):
        self.logger.info("Limiting time for this data colletion to %5.1f hours" % time_hours)
        self.time_limit_ds = time_hours

    def setMinBeamsize10umRaster(self, beamsize_thresh):
        self.min_beamsize_10um_raster = beamsize_thresh
        self.flag10um_raster = True

    def prepESA(self, doesExist=False):
        self.logger.info("Preparation of ZOO database file from input CSV file. %s" % self.esa_csv)
        # Root directory from CSV file
        root_dir = open(self.esa_csv, "r").readlines()[1].replace("\"", "").split(",")[0]
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
            beamsizeconf = BeamsizeConfig.BeamsizeConfig()
            beamsize_index = beamsizeconf.getBeamIndexHV(cond['ds_hbeam'], cond['ds_vbeam'])
            if current_beam_index != beamsize_index:
                self.logger.info("Beam size will be changed from now.")
                self.logger.info("Beamsize index = %5d" % beamsize_index)
                self.zoo.setBeamsize(beamsize_index)

        # Measure the flux
        self.logger.info("Measuring photon flux....")
        self.phosec_meas = self.dev.measureFlux()
        # 2020/07/17 To be fixed.
        # 2021/04/12 Test without no X-ray beam
        if self.phosec_meas < 1E10:
            self.logger.info("Illegally weak X-ray... but test will continue (test mode w/o X-ray beam)")
            sys.exit()

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
        try:
            self.zoo.dismountCurrentPin()
        except MyException as tttt:
            self.logger.info("dismounting sample for capturing background image failed.")
            sys.exit()
        # Background image for centering
        self.backimg = "%s/%s" % (self.backimage_dir, datetime.datetime.now().strftime("back-%y%m%d%H%M.ppm"))
        self.logger.debug("Before while loop for capturing.")
        while (True):
            try:
                self.dev.prepCentering(zoom_out=True)
                self.logger.debug("Dummy capture for the first image")
                self.dev.capture.capture(self.backimg)
                time.sleep(0.5)
                self.logger.debug("The 2nd image..")
                self.dev.capture.capture(self.backimg)
            except MyException as tttt:
                raise MyException("Capture background file failed")
                sys.exit()

            timg = cv2.imread(self.backimg)
            mean_value = timg.mean()
            self.logger.debug("Checking the file size and background level.")
            if beamline.upper() == "BL32XU":
                # mean_thresh = 230
                mean_thresh = 240  # 2021/01/21 HM temporary setting
            elif beamline.upper() == "BL45XU":
                mean_thresh = 200

            self.logger.debug("HERHERERERER")
            if self.isDark == False and mean_value < 100:
                self.logger.info("Mean value of the image is %5d" % mean_value)
                self.logger.info("Background image seems to be bad with lower mean value than 100!")
                continue
            elif self.isDark == True and mean_value < 35:
                self.logger.info("Dark experiments: mean value of the image is %5d" % mean_value)
                self.logger.info("Background image seems to be bad with lower mean value than 50 in Dark!")
                continue
            elif mean_value > mean_thresh:
                self.logger.info("Mean value of the image is %5d" % mean_value)
                self.logger.info("Background image seems to be bad with higher mean value than 200!")
                continue
            else:
                self.logger.info("Background image seems to be good!")
                break

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
        self.logger.info(f"ZooDB: {zoodb}")
        if zoodb == "none":
            self.prepESA()
        else:
            self.readZooDB(zoodb)
        # Zoom out
        self.dev.zoom.zoomOut()
        # save the starting time for this data collection
        self.stopwatch.setTime("start_data_collection")
        # set the initial time for cleaning
        self.stopwatch.setTime("last_cleaning")
        while (1):
            # Get a condition of the most important pin stored in a current zoo.db
            try:
                self.logger.info("Trying to get the prior pin")
                cond = self.esa.getPriorPinCond()
                self.processLoop(cond, checkEnergyFlag=True)
                self.logger.info("ZN: processLoop has been finished for this pin.")
            except MyException as ttt:
                # Logging a caught exception message from modules.
                exception_message = ttt.args[0]
                self.logger.info("+++ Caught exception in a main loop.:%s +++" % exception_message)

                if self.num_pins == 0:
                    message = "Exception in ZN.processLoop: Please check CSV file or ZOODB file."
                else:
                    message = "All measurements have been finished."
                self.logger.info(message)
                return self.num_pins
            finally:
                # Check for total consumed time
                lap_time = self.stopwatch.calcTimeFrom("start_data_collection") / 3600.0  # hours
                residual_time_for_ds = self.time_limit_ds - lap_time

                self.logger.info("Lap time for data collection: %5.2f hours (residual= %5.2f hours)" % (
                    lap_time, residual_time_for_ds))

                if residual_time_for_ds < 0.0:
                    self.logger.info("Data collection has been finished due to the booked time finish.")
                    self.logger.info("Consumed time = %8.4f hours" % lap_time)
                    return self.num_pins

                # Time from last cleaning
                self.logger.info("Checking the cleaning interval time...")
                time_from_last_cleaning = self.stopwatch.calcTimeFrom("last_cleaning")
                residual_time_for_next_cleaning = self.cleaning_interval_hours * 3600 - time_from_last_cleaning
                self.logger.info("Time from last cleaning: %s seconds (%s remains)" % (
                    time_from_last_cleaning, residual_time_for_next_cleaning))
                if residual_time_for_next_cleaning < 0:
                    # cleaning
                    self.zoo.cleaning()
                    self.zoo.waitSPACE()
                    # Set the new 'last_cleaning' time
                    self.stopwatch.setTime("last_cleaning")

    def processLoop(self, cond, checkEnergyFlag=False, measFlux=False):
        # Root directory
        root_dir = cond['root_dir']
        # priority index 
        o_index = cond['o_index']

        # self.html_maker = ZooHtmlLog(root_dir, name, online=True)
        # open(os.path.join(os.environ["HOME"], ".zoo_current"), "w").write("%s %s\n"%(name,root_dir))

        # For data processing
        dp_file_name = "%s/data_proc.csv" % root_dir
        if self.isOpenDPfile == False:
            # 'data_proc.csv' does not exist
            if os.path.exists(dp_file_name) == False:
                self.data_proc_file = open(dp_file_name, "w")
                self.data_proc_file.write("topdir,name,anomalous\n")
            else:
                self.data_proc_file = open("%s/data_proc.csv" % root_dir, "a")
            # Flag for opening the data processing file
            self.isOpenDPfile = True

        # Check point of 'skipping' this loop
        # check 'isSkip' in zoo.db
        if self.esa.isSkipped(o_index) == True:
            self.logger.info("o_index=%5d %s-%s is skipped" % (o_index, cond['puckid'], cond['pinid']))
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        # Write log string
        self.logger.info(">>>>>>>>>>>>>>>> Processing %4s-%2s <<<<<<<<<<<<<<<<" % (cond['puckid'], cond['pinid']))

        # Making root directory
        if os.path.exists(root_dir):
            self.logger.info("%s already exists" % root_dir)
        else:
            self.logger.info("%s is being made now..." % root_dir)
            os.makedirs(root_dir)

        # Getting puck information from SPACE server program
        self.zoo.getSampleInformation()

        # Background image should be done for each 'run'
        if self.isCaptured == False:
            self.logger.info("Now a new background image for centering will be captured.")
            self.getBackgroundImage()

        # For each pin, energy is checked.
        # Everytime, energy_change_flag is updated.
        if checkEnergyFlag == True:
            self.logger.info("Wavelength will be checked.")
            energy_change_flag = self.checkEnergy(cond)
            # When the energy was changed in checkEnergy function
            if energy_change_flag == True:
                if beamline.upper() == "BL45XU":
                    self.logger.info("Wavelength will be changed.")
                    self.zoo.setWavelength(cond['wavelength'])
                    self.logger.info("Wavelength has been changed. You should wait for 15 minutes")
                    time.sleep(15 * 60)
                    self.logger.info("Tuning is required.")
                    # 2020/04/06 Dtheta1 tune will be conducted
                    self.logger.info("BOSS command : BLdtheta_tune will be run.")
                    self.zoo.runScriptOnBSS("BLdtheta_tune")
                    self.logger.info("BOSS command : BLTune will be run.")
                    self.zoo.runScriptOnBSS("BLTune")
                    self.dev.zoom.zoomOut()
            else:
                self.logger.info("Wavelength is not changed in this condition. Tuning is not required")

        # Beamsize setting
        if self.doesBSSchangeBeamsize == True:
            # Beamsize setting
            current_beam_index = self.zoo.getBeamsize()
            beamsizeconf = BeamsizeConfig.BeamsizeConfig()
            self.logger.debug(
                "Raster beam size = %5.2f(H) x %5.2f(V) [um]" % (cond['raster_hbeam'], cond['raster_vbeam']))
            beamsize_index = beamsizeconf.getBeamIndexHV(cond['raster_hbeam'], cond['raster_vbeam'])
            self.logger.info("Current beamsize index= %5d" % current_beam_index)
            if current_beam_index != beamsize_index:
                self.logger.info("Beamsize index = %5d" % beamsize_index)
                self.zoo.setBeamsize(beamsize_index)
                if beamline.upper() == "BL45XU":
                    self.logger.info("Tuning a beam position starts....")
                    self.zoo.runScriptOnBSS("BLTune")
                    self.dev.zoom.zoomOut()

        self.logger.info(
            "Beam size for raster scan= %5.2f(H) x %5.2f(V) [um^2]" % (cond['raster_hbeam'], cond['raster_vbeam']))

        # Making
        # try: self.html_maker.add_condition(cond)
        # except: print traceback.format_exc()

        # SSROX does not require measuring flux
        # Changed 2020/06/02: dose estimation is also required for SSROX measurement
        # if cond['mode'] == "ssrox":
        #     self.needMeasureFlux = False

        if self.needMeasureFlux == True:
            self.logger.debug("ZooNavigator.measureFlux is called from main routin")
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
        self.logger.info("Constructore finished.")

        # Making directories
        # d_index was defined as 'the newest directory number' of scan??/data??.
        d_index = self.lm.prepDataCollection()
        self.logger.info("Directory preparation finished.")
        # n_mount is not useful then 'directory index' is stored to 'n_mount'

        self.esa.updateValueAt(o_index, "n_mount", d_index)
        self.esa.addEventTimeAt(o_index, "meas_start")

        # Setting wavelength for schedule file
        self.lm.setWavelength(cond['wavelength'])

        # Mount position of SPACE (copy from Loopmeasurement.INOCC)
        self.mx = self.lm.inocc.mx
        self.my = self.lm.inocc.my
        self.mz = self.lm.inocc.mz

        self.logger.info("[PROCESS] Mounting sample starts.")
        self.esa.addEventTimeAt(o_index, "mount_start")
        try:
            self.zoo.mountSample(trayid, pinid)
        except MyException as ttt:
            exception_message = ttt.args[0]
            self.logger.info("Failed to mount a sample pin:%s" % ttt)
            # Accident case
            if exception_message.rfind('-1005000003') != -1:
                message = "SPACE accident occurred! Please contact a beamline scientist."
                message += "Check if 'puckid' matches in CSV file and SPACE server."
                self.logger.error(message)
                self.esa.updateValueAt(o_index, "log_mount", msg)
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.logger.critical(message)
                self.esa.updateValueAt(o_index, "isDone", 9999)
                sys.exit()
            if exception_message.rfind('-1005000004') != -1:
                message = "SPACE accident occurred! Please contact a beamline scientist.\n"
                message += "L-head value is negative in picking up the designated pin."
                self.logger.error(message)
                self.esa.updateValueAt(o_index, "log_mount", msg)
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.logger.critical(message)
                self.esa.updateValueAt(o_index, "isDone", 9997)
                sys.exit()
            elif exception_message.rfind('-1005100001') != -1:
                message = "'SPACE_WARNING_existense_pin_%s_%s'" % (trayid, pinid)
                self.logger.warning(message)
                self.esa.updateValueAt(o_index, "log_mount", message)
                self.zoo.skipSample()
                self.logger.info("Go to the next sample...")
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.esa.updateValueAt(o_index, "isDone", 5001)
                self.logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                return
            elif exception_message.rfind('-1005100002') != -1:
                message = "'SPACE_WARNING_push_too_much_%s_%s'" % (trayid, pinid)
                self.logger.warning(message)
                self.esa.updateValueAt(o_index, "log_mount", message)
                self.zoo.skipSample()
                self.logger.info("Go to the next sample...")
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.esa.updateValueAt(o_index, "isDone", 5001)
                self.logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                return
            elif exception_message.rfind('-1005100003') != -1:
                message = "'SPACE_WARNING_rotate_too_much_%s_%s'" % (trayid, pinid)
                self.logger.warning(message)
                self.esa.updateValueAt(o_index, "log_mount", message)
                self.zoo.skipSample()
                self.logger.info("Go to the next sample...")
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.esa.updateValueAt(o_index, "isDone", 5001)
                self.logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                return
            # 220629 K.Hirata added from BSS log.
            elif exception_message.rfind('-1005100007') != -1:
                message = "'Failed to pickup the sample pin from the tray. %s_%s'" % (trayid, pinid)
                self.logger.warning(message)
                self.esa.updateValueAt(o_index, "log_mount", message)
                self.zoo.skipSample()
                self.logger.info("Go to the next sample...")
                self.esa.addEventTimeAt(o_index, "meas_end")
                self.esa.updateValueAt(o_index, "isDone", 5001)
                self.logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
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

        # Time for waiting for the elongation
        time.sleep(self.time_for_elongation)

        # Preparation for centering
        self.dev.prepCentering()

        # Move Gonio XYZ to the previous pin
        # if the previous pin Y position moves larger than 3.0mm from
        # the initial Y position, this code resets the Y position to
        # the initial one.
        if np.fabs(self.sy - self.my) > 4.0:
            self.logger.warning("Saved Y position is so distant from the mount position: %8.3f" % self.sy)
            self.logger.warning("New value is got from mount position: %9.4f)" % self.my)
            self.sy = self.my

        # Check point of 'skipping' this loop
        # check 'isSkip' in zoo.db
        if self.esa.isSkipped(o_index) == True:
            self.logger.info("o_index=%5d %s-%s is skipped" % (o_index, cond['puckid'], cond['pinid']))
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        # The goniometer moves to the saved position
        self.logger.info("move to the save point (%9.4f %9.4f %9.4f)" % (self.sx, self.sy, self.sz))
        self.lm.moveGXYZphi(self.sx, self.sy, self.sz, 0.0)

        # Waiting warming up the pin
        if cond['warm_time'] > 0.0:
            # Rough centering will be started
            self.logger.info("Rough centering is started.")
            self.lm.roughCentering(self.backimg, cond['loopsize'], offset_angle=0.0)
            capture_name = "before_warmup.ppm"
            # Capture an image at 0.0 deg before warming
            self.dev.gonio.rotatePhi(0.0)
            self.lm.captureImage(capture_name)
            # Now warming up starts
            self.logger.info("ZOO starts warming up the loop.")
            # Recording start time
            self.stopwatch.setTime("start_warming")
            time_from_start = 1.0  # sec
            while (1):
                if time_from_start <= cond['warm_time']:
                    self.dev.gonio.rotatePhi(0.0)
                    time.sleep(0.5)
                    self.dev.gonio.rotatePhi(360.0)
                    time.sleep(0.5)
                else:
                    break
                time_from_start = self.stopwatch.calcTimeFrom("start_warming")
                self.logger.info("Warming up time: %10.2f sec" % time_from_start)
            self.logger.info("Warming up finished!!")

            # Capture after the warming up process
            self.dev.gonio.rotatePhi(0.0)
            capture_name = "after_warmup.ppm"
            self.lm.captureImage(capture_name)

        self.logger.info("[PROCESS] ZOO will start centering procedure.")

        #### Centering
        # 2015/11/21 Loop size can be set
        self.esa.addEventTimeAt(o_index, "center_start")
        try:

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

        except:
            self.logger.error("ZOO detects exception in centering")
            self.logger.error("Go to next sample")
            self.esa.updateValueAt(o_index, "isLoopCenter", -9999)
            self.esa.updateValueAt(o_index, "isDone", 5002)
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.info("close Capture instance")
            self.lm.closeCapture()
            return

        #### /Centering
        # Succeeded
        self.esa.addEventTimeAt(o_index, "center_end")

        # Save Gonio XYZ to the previous pins
        self.sx, self.sy, self.sz, sphi = self.lm.saveGXYZphi()

        # Capture the crystal image before experiment
        self.logger.info("ZooNavigator is capturing the 'before.ppm'")
        capture_name = "before.ppm"
        self.lm.captureImage(capture_name)

        if beamline.upper() == "BL45XU":
            # LN2:ON -> ZoomCap:ON
            if cond['ln2_flag'] == 1:
                self.dev.zoom.move(2000)
                capture_name = "loop_zoom.ppm"
                self.lm.captureImage(capture_name)
                # Bukkake
                self.logger.info("LN2 will be exposed from now...")
                self.zoo.exposeLN2(20)
                time.sleep(5.0)
                capture_name = "loop_zoom_ln2.ppm"
                self.lm.captureImage(capture_name)
                self.dev.zoom.zoomOut()
            # ZoomCap:ON only (withough LN2 bukkake)
            elif cond['zoomcap_flag'] == 1:
                self.logger.info("Zoom capture will be conducted from now...")
                self.dev.zoom.move(2000)
                capture_name = "loop_zoom.ppm"
                self.lm.captureImage(capture_name)
                self.dev.zoom.zoomOut()
            else:
                self.logger.info("Zoom capture will be skipped...")

        # Dump check and wait
        # if the routine recovers MBS/DSS status, 'False' flag
        # is received here. In this case, tuning was conducted
        # with TCS 0.1mm square. Then, beamsize should be recovered.
        if self.recoverOption == True:
            if self.dump_recov.checkAndRecover(cond['wavelength']) == False:
                # 2019/04/21 K.Hirata Skipped at BL45XU
                # self.bsc.changeBeamsizeHV(cond['raster_hbeam'],cond['raster_vbeam'])
                self.logger.info("skipping change beam size")

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

        self.esa.addEventTimeAt(o_index, "meas_end")
        self.logger.info("Adding 'meas_end' time information has been finished.")

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

        # 10um raster for BL45XU
        if self.flag10um_raster == True:
            self.lm.setMinBeamsize10umRaster(self.min_beamsize_10um_raster)

        raster_schedule, raster_path = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                            scanv_um, scanh_um, vstep_um, hstep_um,
                                                            sphi, cond)
        raster_start_time = time.localtime()

        # To catch a detailed exception
        try:
            self.esa.addEventTimeAt(o_index, "raster_start")
        except:
            raise Exception("Updating ESA failed.")
        try:
            self.zoo.doRaster(raster_schedule)
            self.zoo.waitTillReady()
        except:
            raise Exception("Raster scan by BSS failed.")
        try:
            self.esa.addEventTimeAt(o_index, "raster_end")
            # Flag on
            self.esa.incrementInt(o_index, "isRaster")
        except:
            raise Exception("Updating ESA failed.")

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
            ahm = AnaHeatmap.AnaHeatmap(raster_path)
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

        except MyException as tttt:
            self.logger.warning("Skipping this loop!!")
            self.esa.updateValueAt(o_index, "isDone", 4002)
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        finally:
            try:
                self.logger.info("FINALLY")
                # nhits = len(glist)
                # self.html_maker.add_result(puckname=trayid, pin=pinid,
                # h_grid=self.lm.raster_n_width, v_grid=self.lm.raster_n_height,
                # nhits=nhits, shika_workdir=os.path.join(self.lm.raster_dir, "_spotfinder"),
                # prefix=self.lm.prefix, start_time=raster_start_time)
                # self.html_maker.write_html()
            except:
                print(traceback.format_exc())

        if len(glist) == 0:
            self.logger.warning("Skipping this loop!!")
            self.esa.updateValueAt(o_index, "isDone", 4001)
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.warning("Disconnecting capture")
            self.lm.closeCapture()
            return

        # Data collection
        time.sleep(0.1)
        data_prefix = "%s-%02d-multi" % (trayid, pinid)

        # Photon flux is extracted from beamsize.config
        if self.phosec_meas == 0.0:
            beamsizeconf = BeamsizeConfig.BeamsizeConfig()
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.logger.info("Flux value is read from beamsize.conf: %5.2e" % flux)
        else:
            flux = self.phosec_meas
            # loggerにbeam size と Fluxを書き込む
            self.logger.info(f"Flux value is read from phosec: {flux:5.2e}")
            # beam size はそれぞれ小数点以下1桁まで記載する
            # cond['ds_hbeam], cond['ds_vbeam'] は小数点以下1桁まで記載する
            self.logger.info(f"Beam size is read from config: {cond['ds_hbeam']:.1f} x {cond['ds_vbeam']:.1f} um")
            
        # For dose estimation
        # self.loggerにbeam size と Fluxを書き込む
        self.logger.info(f"Flux value is read from phosec: {flux:5.2e}")
        # beam size はそれぞれ小数点以下1桁まで記載する
        # cond['ds_hbeam], cond['ds_vbeam'] は小数点以下1桁まで記載する
        self.logger.info(f"Beam size is read from config: {cond['ds_hbeam']:.1f}um x {cond['ds_vbeam']:.1f} um")

        # Generate Schedule file
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond, flux, prefix=data_prefix)
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

        self.logger.info("Disconnecting capture")
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

        # 10um step scan for larger beam
        # 10um raster for BL45XU
        if self.flag10um_raster == True:
            self.lm.setMinBeamsize10umRaster(self.min_beamsize_10um_raster)
        schfile, raspath = self.lm.rasterMaster(scan_id, scan_mode, self.center_xyz,
                                                scanv_um, scanh_um, vstep_um, hstep_um, sphi, cond)

        self.esa.addEventTimeAt(o_index, "raster_start")
        self.logger.debug("[PROCESS] ZOO starts raster scan..")
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
            ahm = AnaHeatmap.AnaHeatmap(raspath)
            min_score = cond['score_min']
            max_score = cond['score_max']
            ahm.setMinMax(min_score, max_score)
            crystal_array = ahm.searchPixelBunch(scan_id, naname_include=True)
            n_crystals = len(crystal_array)
            self.logger.info("SHIKA heatmap has been analyzed. %d crystals were found." % (n_crystals))

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
                self.logger.info(
                    "Left v scan is started at %9.4f %9.4f %9.4f" % (mod_xyz[0], mod_xyz[1], mod_xyz[2]))
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
                # If the exposure time was modified because of the vertical scan speed..
                if factor_increase_exp != 1.0:
                    # DB information should be overwritten
                    cond['exp_raster'] = exp_mod
                    self.logger.info(
                        "Exposure time is changed from %8.3f [sec] to %8.3f [sec]\n" % (exp_origin, exp_mod))
                    # Attenuation factor in [%]
                    att_raster = att_origin / factor_increase_exp
                    self.logger.info(
                        "Attenuation %8.3f [percent] is replaced by %8.3f [percent]\n" % (att_origin, att_raster))
                    cond['att_raster'] = att_raster
                # Now preparation of raster scan
                schfile, raspath = self.lm.rasterMaster(v_prefix, "Vert", mod_xyz,
                                                        scanv_um, scanh_um, vstep_um, hstep_um, phi_lv, cond)
                self.zoo.doRaster(schfile)
                self.zoo.waitTillReady()
                self.esa.addEventTimeAt(o_index, "raster_end")

                try:
                    # Final analysis for vertical scan
                    # Analyze heatmap and get crystal list
                    self.logger.info("Analyzing the vertical scan...")
                    ahm = AnaHeatmap.AnaHeatmap(raspath)
                    # Minimum score is set to 3
                    min_score = 5
                    max_score = cond['score_max']
                    ahm.setMinMax(min_score, max_score)
                    crystal_array = ahm.searchPixelBunch(v_prefix, naname_include=True)
                    self.logger.info("Number of found crystlas... %5d" % len(crystal_array))

                    crystals = CrystalList.CrystalList(crystal_array)
                    final_cxyz = crystals.getBestCrystalCode()
                except Exception as e:
                    self.logger.warning("Analyze vertical scans failed.\n")
                    self.logger.warning("ZN.collectSingle: Left vertical scan analysis failed.")
                    self.logger.error("ERROR", exc_info=True)
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
            self.logger.info("Caught error: %s " % message)
            self.logger.info("Skipping this loop: diffraction based centering loop.")
            self.esa.updateValueAt(o_index, "isDone", 4002)
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.info("Disconnecting capture")
            self.lm.closeCapture()
            return

        # Data collection
        # Why is this wait required?
        time.sleep(0.1)
        data_prefix = "%s-%02d-single" % (trayid, pinid)

        # Dose to limit exposure time
        self.logger.info("KUMA will be called from now!!")
        kuma = KUMA.KUMA()

        # Photon flux is extracted from beamsize.config
        if self.phosec_meas == 0.0:
            beamsizeconf = BeamsizeConfig.BeamsizeConfig()
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.logger.info("Flux value is read from beamsize.conf: %5.2e." % flux)
            # self.logger.info()
        else:
            flux = self.phosec_meas
            self.logger.info(
                "Single: Beam size = %5.2f %5.2f um Measured flux : %5.2e" % (cond['ds_hbeam'], cond['ds_vbeam'], flux))

        # Generate Schedule file
        self.logger.info("Preparing the schedule file for a single data collection.")
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond, flux, prefix=data_prefix)

        # Why is this wait required?
        # For waiting the schedule file???
        time.sleep(0.1)

        self.esa.addEventTimeAt(o_index, "ds_start")
        self.logger.info("Now ZOO starts single data collection.")
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.esa.incrementInt(o_index, "isDS")
        self.esa.updateValueAt(o_index, "isDone", 1)
        self.logger.info("Now ZOO finishes single data collection.")
        # Data proc
        sample_name = cond['sample_name']
        prefix = "%s-%02d" % (trayid, pinid)
        root_dir = cond['root_dir']
        self.data_proc_file.write("%s/_kamoproc/%s/,%s,no\n" % (root_dir, prefix, sample_name))
        self.data_proc_file.flush()

        # Disconnecting capture in this loop's 'capture' instance
        self.logger.info("Disconnecting capture")
        self.lm.closeCapture()

    # collectSingle

    # 2018/04/13 modified for DB-based measurement
    # 2018/12/15 modified for stop watching
    def collectHelical(self, trayid, pinid, prefix, cond, sphi):
        o_index = cond['o_index']
        # Beamsize
        self.logger.info("now moving to the beam size to raster scan...")
        self.logger.info("beam size should be changed by BSS")
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

        # 10um raster for BL45XU
        if self.flag10um_raster == True:
            self.lm.setMinBeamsize10umRaster(self.min_beamsize_10um_raster)

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
            beamsizeconf = BeamsizeConfig.BeamsizeConfig()
            flux = beamsizeconf.getFluxAtWavelength(cond['ds_hbeam'], cond['ds_vbeam'], cond['wavelength'])
            self.logger.info("Flux value is read from beamsize.conf: %5.2e" % flux)
        else:
            flux = self.phosec_meas
            self.logger.info("Helical: Beam size = %5.2f %5.2f um Measured flux : %5.2e" % (
                cond['ds_hbeam'], cond['ds_vbeam'], flux))

        # HEBI instance
        hebi = HEBI.HEBI(self.zoo, self.lm, self.stopwatch, flux)

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
                # Data proc
                sample_name = cond['sample_name']
                root_dir = cond['root_dir']
                self.data_proc_file.write("%s/_kamoproc/%s/,%s,no\n" % (root_dir, prefix, sample_name))
                self.data_proc_file.flush()
            else:
                self.logger.info("No crystals were found in HEBI.")
                self.esa.updateValueAt(o_index, "isDone", 4003)
            # Log file for time stamp
            self.esa.addEventTimeAt(o_index, "ds_end")
            self.logger.info("[PROCESS] Helical data collection ended.")
        except:
            self.logger.info("ZooNavigator.collectHelical failed.")
            self.esa.updateValueAt(o_index, "isDone", 4004)
        self.lm.closeCapture()
        self.logger.info("Return to the main loop of 'process'")

    def collectMixed(self, trayid, pinid, prefix, cond, sphi):
        # Pin index
        o_index = cond['o_index']
        # Beamsize
        self.logger.info("now moving to the beam size to raster scan...")
        # Specific code for BL41XU and obsoleted temporally on 2019/06/03
        # self.bsc.changeBeamsizeHV(cond['raster_hbeam'], cond['raster_vbeam'])

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

        # 10um step scan for larger beam
        # 10um raster for BL45XU
        if self.flag10um_raster == True:
            self.lm.setMinBeamsize10umRaster(self.min_beamsize_10um_raster)
        self.lm.setMinBeamsize10umRaster(self.min_beamsize_10um_raster)
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
        hito = DiffscanMaster.NOU(self.zoo, self.lm, sphi, self.phosec_meas)
        # Set the time limit for data collection from a pin.
        self.esa.addEventTimeAt(o_index, "ds_start")
        # HITO data collection time [mins] -> currently limited to 15 minutes.
        hito.setTimeLimit(15.0)
        try:
            n_datasets = hito.sokuteiSuru(raspath, cond, prefix)
            self.esa.incrementInt(o_index, "isDS")
            self.esa.updateValueAt(o_index, "isDone", 1)
        except Exception as e:
            self.logger.info(e.args[0])
            self.esa.addEventTimeAt(o_index, "ds_end")

        # Wrong information but update the zoo.db
        self.esa.updateValueAt(o_index, "nds_multi", n_datasets)
        self.esa.updateValueAt(o_index, "nds_helical", n_datasets)

        # Ending procedure of 'mixed' mode.
        self.lm.closeCapture()

        # Log file for time stamp
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.logger.info("mixed end")

    # 2020/06/02 Major revision in order to activate this function for BL45XU.
    def collectSSROX(self, cond, sphi):
        # Pin index
        o_index = cond['o_index']
        trayid = cond['puckid']
        pinid = cond['pinid']
        prefix = "%s-%02d" % (trayid, pinid)
        scan_id = "ssrox"

        # measured flux
        self.logger.info("SSROX schedule file preparation")
        raster_schedule, raster_path = self.lm.prepSSROX(scan_id, self.center_xyz, sphi, cond, self.phosec_meas)
        self.logger.info("ZOO has finished SSROX preparation.")
        self.esa.addEventTimeAt(o_index, "ds_start")

        # Do the raster scan with rotation
        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()
        self.esa.addEventTimeAt(o_index, "ds_end")
        self.esa.incrementInt(o_index, "isDS")
        self.logger.info("Disconnecting capture")
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
                                                            exptime=cond['exp_raster'], roi_index=0)

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
            ahm = AnaHeatmap.AnaHeatmap(raster_path)
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

        except MyException as tttt:
            self.logger.warning("Skipping this loop!!")
            # Disconnecting capture in this loop's 'capture' instance
            self.logger.warning("Disconnecting capture")
            self.lm.closeCapture()
            return

        finally:
            try:
                self.logger.info("FINALLY")
                # Disconnecting capture in this loop's 'capture' instance
                self.logger.info("Disconnecting capture")
                self.lm.closeCapture()
                return
            except:
                print(traceback.format_exc())
