import sys, math, numpy, os

import MyException
import StopWatch
import AnaHeatmap
import CrystalList
import logging
import logging.config
import LoopCrystals
# python 3 sorted function
from functools import cmp_to_key

beamline = "BL32XU"

class NOU():
    def __init__(self, zoo, loop_measurement, face_angle, phosec):
        self.min_score = 10
        self.max_score = 200
        self.naname_include = True

        # Vertical scan length
        # The longer, the better
        self.vscan_length = 1000.0  # [um]
        # 500 um/sec is the limit at BL32XU/BL45XU
        # A little bit smaller value is suitable for a threshold for determining exposure time
        # 2019/11/27 48 Hz exposure time for 10 um step scan showed
        self.limit_of_vert_velocity = 400.0  # [um]

        self.gaburiyoru_ntimes = 5  # times
        self.gaburiyoru_h_length = 10  # [um]

        # small beam scan 
        # The score threshold on small beam scan should be the minimum value
        self.min_score_smallbeam = 6
        # For debugging
        self.debug = True
        self.debug_LR = False

        self.zoo = zoo
        self.lm = loop_measurement

        self.phosec_meas = phosec
        self.face_angle = face_angle

        # My logfile
        self.logger = logging.getLogger('ZOO').getChild("HITO")

        # Stopwatch for this class
        self.sw = StopWatch.StopWatch()

        # Data collection time for this pin
        self.time_limit = 60.0  # [min]

    def setTimeLimit(self, limit_minutes):
        self.time_limit = limit_minutes

    def junbiSuru(self, scan_path, cond, prefix):
        ahm = AnaHeatmap.AnaHeatmap(scan_path)
        # Min & Max score value to pick up crystals
        self.min_score = cond['score_min']
        self.max_score = cond['score_max']

        # print min_score, max_score
        ahm.setMinMax(self.min_score, self.max_score)

        # output image: 'background' = black
        # 1 um pixel crystal map from SHIKA heatmap
        binimage_name = "%s/bin_summary.png" % scan_path
        origin_xyz, vert_koma, hori_koma = ahm.makeBinMap(prefix, binimage_name)

        # color_inverse = True: when the back ground color is black
        lc = LoopCrystals.LoopCrystals(binimage_name, origin_xyz, vert_koma, hori_koma, color_inverse=True)
        # Log image files are output to 'scan_path' directory.
        lc.setOutPath(scan_path)
        lc.prep()
        self.logger.info("HITO finished the preparation.")
        lc.analyze()
        self.logger.info("analysis finished.")
        dc_blocks = lc.getFinalCenteringInfo()

        self.logger.info("The number of data collection blocks=%5d" % len(dc_blocks))

        # Sort dc_blocks: priority is along with 'rotation range' (larger is higher priority)
        self.sortDCblocks(dc_blocks)

        # Slicing a list of data collection blocks
        maxhits = cond['maxhits']
        if len(dc_blocks) > maxhits:
            dc_blocks = dc_blocks[:maxhits]

        return dc_blocks

    def sokuteiSuru(self, scan_path, cond, prefix):
        # Prepare 'data collection blocks'
        dc_blocks = self.junbiSuru(scan_path, cond, prefix)
        # The number of collected datasets (log)
        n_datasets = 0

        # Record the starting time.
        self.sw.setTime("start")
        # Actual data collection for each 'data collection block'
        for dc_index, dc_block in enumerate(dc_blocks):
            try:
                self.logger.info(">> Data collection: DC_INDEX=%5d started." % dc_index)
                self.dododo(cond, dc_block, dc_index)
                n_datasets += 1
            except Exception as e:
                self.logger.info(self.commentException(e.args))
                self.logger.info(">> DC_INDEX=%5d data collection failed." % dc_index)
            # Check the time for data collection
            consumed_minutes = self.sw.calcTimeFrom("start") / 60.0  # [mins]
            if consumed_minutes > self.time_limit:
                self.logger.info(">> Data collection time exceeds the limit : %5.1f [mins]" % consumed_minutes)
                return n_datasets

        # Return the number of collected datasets
        return n_datasets

    # This function should be called for each 'data collection block'.
    def dododo(self, cond, dc_block, dc_index):
        # Mode selection
        # 'helical_full'
        mode = dc_block['mode']
        try:
            if mode == "helical_full":
                self.do_helical_full(cond, dc_block, dc_index)
            elif mode == "helical_part":
                self.do_helical_part(cond, dc_block, dc_index)
            elif mode == "helical_noalign":
                self.do_helical_noalign(cond, dc_block, dc_index)
            elif mode == "single_full":
                self.do_single_full(cond, dc_block, dc_index)
            elif mode == "single_part":
                self.do_single_part(cond, dc_block, dc_index)
            elif mode == "single_noalign":
                self.do_single_noalign(cond, dc_block, dc_index)
            elif mode == "multi":
                self.do_multi(cond, dc_block, dc_index)
        except Exception as e:
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("dododo failed in data collection. Exception caught.")

    def commentException(self, args):
        comment = ""
        for arg in args:
            comment += arg
        return comment

    # Helical data collectionasdfadsf
    def do_helical_full(self, cond, dc_block, dc_index):
        # Header information for this data collection
        left_face_xyz = dc_block['lxyz']
        right_face_xyz = dc_block['rxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        prefix = "helfull_%02d" % dc_index
        vscan_length = 1000.0  # [um]
        # Left centering
        try:
            left_phi = self.face_angle - 90.0  # [deg.]
            left_xyz = self.vertCentering(cond, left_phi, left_face_xyz, vscan_length, option="Left", dc_index=dc_index,
                                          max_repeat=1)
        except Exception as e:
            self.logger.info("Left centering failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("Left centering failed.")
        # Right centering
        try:
            right_phi = self.face_angle + 90.0  # [deg.]
            right_xyz = self.vertCentering(cond, right_phi, right_face_xyz, vscan_length, option="Right", dc_index=dc_index,
                                           max_repeat=1)
        except Exception as e:
            self.logger.info("Right centering failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("Right centering failed.")

        # Data collection
        try:
            self.startHelical(left_xyz, right_xyz, cond, osc_start, osc_end, prefix)
        except Exception as e:
            self.logger.info("startHelical failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("do_helical_full: startHelical failed.")

    # Partial helical data collection
    def do_helical_part(self, cond, dc_block, dc_index):
        # Header information for this data collection
        left_face_xyz = dc_block['lxyz']
        right_face_xyz = dc_block['rxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        prefix = "helpart_%02d" % dc_index
        vscan_length = 15.0 * 10  # [um]
        # Left centering
        try:
            left_xyz = self.vertCentering(cond, osc_start, left_face_xyz, vscan_length, option="Left", dc_index=dc_index,
                                          max_repeat=1)
        except Exception as e:
            self.logger.info("Left centering failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("hel_part: Left centering failed.")
        # Right centering
        try:
            right_xyz = self.vertCentering(cond, osc_end, right_face_xyz, vscan_length, option="Right", dc_index=dc_index,
                                           max_repeat=1)
        except Exception as e:
            self.logger.info("Right centering failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("hel_part: Right centering failed.")

        # Data collection
        try:
            self.startHelical(left_xyz, right_xyz, cond, osc_start, osc_end, prefix)

        except Exception as e:
            self.logger.info("startHelical failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("hel_part: startHelical failed.")


    # Non-centering helical data collection
    def do_helical_noalign(self, cond, dc_block, dc_index):
        # Header information for this data collection
        left_face_xyz = dc_block['lxyz']
        right_face_xyz = dc_block['rxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        prefix = "helnoal_%02d" % dc_index
        vscan_length = 15.0 * 6  # [um]
        # Data collection
        try:
            self.startHelical(left_face_xyz, right_face_xyz, cond, osc_start, osc_end, prefix)
        except Exception as e:
            self.logger.info("do_helical_noalign: startHelical failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("do_helical_noalign: startHelical failed.")


    # Helical data collection
    def do_single_full(self, cond, dc_block, dc_index):
        # Header information for this data collection
        center_face_xyz = dc_block['cxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        vscan_length = 1000.0  # [um]
        prefix = "singlefull_%02d" % dc_index
        try:
            centering_phi = self.face_angle + 90.0
            center_xyz = self.vertCentering(cond, centering_phi, center_face_xyz, vscan_length, option="center",
                                            dc_index=dc_index, max_repeat=1)
        except Exception as e:
            self.logger.info("Side view centering failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("single_full: vertical centering failed.")
        # Data collection
        try:
            self.doSingle(center_xyz, cond, osc_start, osc_end, prefix)
            # self.startHelical(left_xyz, right_xyz, cond, osc_start, osc_end, prefix)

        except Exception as e:
            self.logger.info("doSingle failed.")
            self.logger.info(self.commentException(e.args))
            raise MyException.MyException("single_full: doSingle failed.")


    # Single partial data collection
    # Rotation range ends at 90 deg.
    def do_single_part(self, cond, dc_block, dc_index):
        # Header information for this data collection
        center_face_xyz = dc_block['cxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        vscan_length = 15.0 * 6.0  # [um]
        prefix = "singlepart_%02d" % dc_index

        # Left centering
        try:
            center_xyz = self.vertCentering(cond, osc_end, center_face_xyz, vscan_length, option="center",
                                            dc_index=dc_index, max_repeat=1)
        except Exception as e:
            self.logger.info("Side view centering failed.")
            self.logger.info(self.commentException(e.args))
            raise Exception("do_single_part: during vertical centering.")
        # Data collection
        try:
            self.doSingle(center_xyz, cond, osc_start, osc_end, prefix)
        except Exception as e:
            self.logger.info("single:partial failed.")
            self.logger.info(self.commentException(e.args))
            raise Exception("during doSingle in do_single_part")


    # Single partial data collection
    # Rotation range ends at 90 deg.
    def do_single_noalign(self, cond, dc_block, dc_index):
        # Header information for this data collection
        center_xyz = dc_block['cxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        prefix = "singlenoal_%02d" % dc_index
        # Data collection
        try:
            self.doSingle(center_xyz, cond, osc_start, osc_end, prefix)
        except Exception as e:
            self.logger.info("single:no-align failed.")
            self.logger.info(self.commentException(e.args))
            raise Exception("during 'doSingle' in do_single_noalign")


    def do_multi(self, cond, dc_block, dc_index):
        # Header information for this data collection
        center_xyz = dc_block['cxyz']
        osc_start = dc_block['osc_start'] + self.face_angle
        osc_end = dc_block['osc_end'] + self.face_angle
        prefix = "multi_%02d" % dc_index
        # Data collection
        try:
            self.doSingle(center_xyz, cond, osc_start, osc_end, prefix)
        except Exception as e:
            self.logger.info("multi:do_multi failed.")
            self.logger.info(self.commentException(e.args))
            raise Exception("during 'doSingle' in do_multi")


    # 2020/07/10 modified from HEBI
    def doVscan(self, prefix, center, cond, scan_length, phi):
        self.logger.info("doVscan: starts\n")
        # unit = [um]
        scan_hbeam = cond['ds_hbeam']
        scan_vbeam = cond['ds_vbeam']
        self.logger.info("Raster beamsize %5.1f(H) x %5.1f(V) [um]" % (scan_hbeam, scan_vbeam))
        # V step is set to 'half' length of the vertical beam size
        vstep_um = scan_vbeam / 2.0
        scan_mode = "Vert"
        # Dummy for vertical scan
        hrange_um = 1.0
        hstep_um = 1.0
        # Wavelength is limited to 1.0A. Transmission is set to 10%
        # Wavelength is limited to 1.0A. Transmission is set to 10%
        wl = cond['wavelength']
        hebi_att_origin = cond['hebi_att']

        # Checking the speed of vertical scan (should be smaller than 500um/sec)
        exp_origin = cond['exp_raster']
        self.logger.info("Initial exposure time: %8.3f[sec]" % exp_origin)
        vert_velocity = vstep_um / exp_origin

        self.logger.info("Scan velocity (ESA): %8.3f[um/sec]" % vert_velocity)
        if vert_velocity > self.limit_of_vert_velocity:
            exp_raster = self.fitExptime(vstep_um)
            self.logger.info("Updated exposure time= %8.5f[sec]" % exp_raster)
            # Attenuation factor should be more for 'longer' exposure time
            factor_increase_exp = exp_raster / exp_origin
            self.logger.info("Vertical scan velocity is too fast. Limit = %8.2f[um/s]" % self.limit_of_vert_velocity)
            # Attenuation factor
            hebi_att_mod = hebi_att_origin / factor_increase_exp
            self.logger.info(
                "Attenuation %8.3f [percent] is replaced by %8.3f [percent]\n" % (hebi_att_origin, hebi_att_mod))
            cond['hebi_att'] = hebi_att_mod
        else:
            exp_raster = exp_origin
            factor_increase_exp = 1.0

        # DB information should be overwritten
        cond['exp_raster'] = exp_raster
        self.logger.info("doVscan: exposure time is replaced by %8.3f [sec]" % exp_raster)
        message = "Scan center (%9.4f, %9.4f, %9.4f)" % (center[0], center[1], center[2])
        self.logger.info(message)

        # 2019/06/03 rasterMaster was modified
        schfile, raspath = self.lm.rasterMaster(prefix, scan_mode, center, scan_length, 1.0,
                                                vstep_um, hstep_um, phi, cond, isHEBI=True, isAdd=False)
        # Start diffraction scan for vertical direction
        try:
            self.zoo.doRaster(schfile)
            self.zoo.waitTillReady()
        except:
            raise MyException.VscanZOOfailed("During raster scan...failed.")

        return raspath


    # method "peak_xyz" : return xyz coordinate from the heatmap
    def anaVscan(self, diffscan_path, prefix, phi_center, method="peak_xyz", isWeakScan=False):
        sorted_crystal_list = self.getSortedCryList(diffscan_path, prefix, phi_center, isWeakScan)

        # There are no good crystals
        if len(sorted_crystal_list) == 0:
            raise MyException.MyException("HEBI.anaVscan : no crystals are found in scan %s" % prefix)

        the_best_crystal = sorted_crystal_list[0]
        if method == "peak_xyz":
            peak_xyz = the_best_crystal.getPeakCode()

        return peak_xyz


    # All ID beamlines here can share this directions 2019/07/11 K.Hirata
    def getRescanDist(self, index, option):
        gaburiyoru_mm = self.gaburiyoru_h_length / 1000.0  # [mm]
        y_abs = float(index) * gaburiyoru_mm
        # Left edge
        if option == "Left":
            return -1.0 * y_abs
        else:
            return +1.0 * y_abs


    def doSingle(self, center_xyz, cond, osc_start, osc_end, prefix):
        try:
            multi_sch = self.lm.genSingleSchedule(osc_start, osc_end, center_xyz, cond, self.phosec_meas, prefix=prefix)
            self.logger.info("MultiSchedule class was used to generate the schedule file.\n")
            self.logger.info("Data collection will be started by using %s.\n" % multi_sch)
            self.zoo.doDataCollection(multi_sch)
            self.zoo.waitTillReady()
        except Exception as e:
            self.logger.info("Exception: %s\n" % e)
            self.logger.info("doSingle: ERRors occured in data collection loop.\n")


    # 2020/07/09 coded by K. Hirata
    def startHelical(self, left_xyz, right_xyz, cond, osc_start, osc_end, prefix):
        self.logger.info("Exposure condition will be considered from now...")

        try:
            # crystal size is smaller than horizontal beam size
            # helical data collection is switched to 'single irradiation mode'
            cry_y_len = numpy.fabs(left_xyz[1] - right_xyz[1]) * 1000.0  # [um]
            self.logger.info("Crystal length for this measurement: %8.3f [um]" % cry_y_len)

            # if cry_y_len <= cond['ds_hbeam']:
            if cry_y_len <= (2.0 * cond['ds_hbeam']):
                self.logger.info("Crystal size is smaller than the horizontal beam size (%5.2f [um])" % cond['ds_hbeam'])
                self.logger.info("Helical data collection is swithced to the single irradiation mode")
                self.doSingle(left_xyz, cond, phi_face, prefix)
            else:
                self.logger.info("Generate helical schedule file")
                helical_sch = self.lm.genHelical(osc_start, osc_end, left_xyz, right_xyz, prefix, self.phosec_meas, cond)

                self.logger.info("Schedule file has been prepared with LM.genHelical")
                self.zoo.doDataCollection(helical_sch)
                self.zoo.waitTillReady()
        except Exception as e:
            self.logger.info("Exception: %s\n" % e)
            self.logger.info("HEBI.startHelical: ERRors occured in data collection loop.\n")

        # When the data collection finished.
        # self.sw.setTime("end")
        # consumed_time=self.sw.getDsecBtw("start","end")
        # self.logfile.write("Consuming time for this crystal %5.1f[sec]\n"%(consumed_time))

    def fitExptime(self, vstep_um):
        exp_min = vstep_um / self.limit_of_vert_velocity
        if exp_min > 0.01 and exp_min <= 0.02:
            exptime = 0.02
        elif exp_min > 0.02 and exp_min <= 0.025:
            exptime = 0.025
        elif exp_min > 0.025 and exp_min <= 0.05:
            exptime = 0.05
        elif exp_min > 0.05 and exp_min <= 0.1:
            exptime = 0.1
        else:
            raise MyException.MyException("fitExptime: No ideal exposure time is found!!")

        return exptime

    # Desinged function
    # left_xyz = self.vertCentering(cond, osc_start, left_face_xyz, option="Left", cry_index=cry_index, max_repeat=1)
    # Crystal edge: Left/Right vertical scan to define crystal position in 3D
    # option: "Left", "Right", "Center"
    def vertCentering(self, cond, phi_scan, init_xyz, scan_length, option="Left", dc_index=0, max_repeat=0):
        index_of_this_scan = 0
        prefix = "%s_%02d" % (option.lower(), dc_index)
        # No need to do 'searching crystal edge'
        if option.lower() == "center":
            max_repeat = 0
        initial_y = init_xyz[1]

        # Final XYZ for the answer
        isFoundGoodPoint = False
        for scan_index in range(0, max_repeat + 1):
            self.logger.info("%s vertical scan started." % option)
            # Vertical scan: This block conducts 'translation' of Y-axis to catch 'edge of crystal'.
            scan_prefix = "%s_%02d" % (prefix, scan_index)
            step_diff = self.getRescanDist(scan_index, option)
            mod_y = initial_y + step_diff
            mod_xyz = numpy.array((init_xyz[0], mod_y, init_xyz[2]))
            self.logger.info(
                "%s scan is started at %9.4f %9.4f %9.4f\n" % (option, mod_xyz[0], mod_xyz[1], mod_xyz[2]))
            # Vertical scan
            try:
                scan_vert_path = self.doVscan(scan_prefix, mod_xyz, cond, scan_length, phi_scan)
            except Exception as e:
                self.logger.info("Exception occurred.")
                self.commentException(e.args)
                # raise MyException.MyException("doVscan failed.")
            # Analysis of raster scan
            try:
                new_xyz = self.anaVscan(scan_vert_path, scan_prefix, phi_scan, method="peak_xyz", isWeakScan=False)
                self.logger.info("FOUND %s= (%9.4f %9.4f %9.4f)" % (prefix, new_xyz[0], new_xyz[1], new_xyz[2]))
                # When the scan finds the good point for data collection
                isFoundGoodPoint = True
                break
            except Exception as e:
                print("Vertical scan analysis failed.\n")
                self.logger.info("%s scan analysis failed." % option)
                self.commentException(e.args)
                raise Exception("vertCentering: analysis failed.")

        if isFoundGoodPoint == True:
            return new_xyz
        else:
            raise MyException.MyException("%s vertical scan finally failed." % option.lower())

    # Sort the data collection blocks according to wedge sizes.
    def sortDCblocks(self, dc_blocks):
        # a,b: an object of 'Crystal' class
        def compOscRange(x, y):
            x_rotation = x['osc_range']
            y_rotation = y['osc_range']
            if x_rotation == y_rotation: return 0
            if x_rotation < y_rotation: return 1
            return -1

        if self.debug == True:
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            for c in dc_blocks:
                print(c)
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

        # Sorting data collection blocks
        # The top of crystal is the best one
        # The bottom is the worst one
        # dc_blocks.sort(cmp=compOscRange)
        dc_blocks=sorted(dc_blocks, key=cmp_to_key(compOscRange))


        if self.debug == True:
            print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
            for c in dc_blocks:
                print(c)
            print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")

        self.isSorted = True

        return dc_blocks

    # getSortedCryList
    def getSortedCryList(self, scan_path, scan_prefix, phi_center, isWeakScan=False):
        self.logger.debug("HITO.getSortedCryList starts")
        cxyz = 0, 0, 0

        ahm = AnaHeatmap.AnaHeatmap(scan_path)
        if isWeakScan == False:
            self.logger.info("Minimum score = %s" % self.min_score)
            self.logger.info("Maximum score = %s" % self.max_score)
            ahm.setMinMax(self.min_score, self.max_score)
        else:
            self.logger.info("This is weak scan")
            self.logger.info("Minimum score = %s" % self.min_score_smallbeam)
            self.logger.info("Maximum score = %s" % self.max_score)
            ahm.setMinMax(self.min_score_smallbeam, self.max_score)
        print("HEBI.getSortedCryList: AnaHeatmap.searchPixelBunch starts")
        crystal_array = ahm.searchPixelBunch(scan_prefix, self.naname_include)
        crystals = CrystalList.CrystalList(crystal_array)
        sorted_crystals = crystals.getSortedCrystalList()

        self.logger.info("Found crystal list in HEBI.getSortedCryList")
        self.logger.info("The number of crystals= %5d" % len(sorted_crystals))

        return sorted_crystals

if __name__ == "__main__":
    face_agnle = 60.0
