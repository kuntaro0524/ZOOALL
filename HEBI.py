import sys, math, numpy, os

import datetime
import LoopMeasurement
import AttFactor
import MyException
import StopWatch
import AnaHeatmap
import CrystalList
import logging
import logging.config

beamline = "BL32XU"

# version 2.0.0 2019/07/04

class HEBI():
    def __init__(self, zoo, loop_measurement, stopwatch, phosec):
        self.min_score = 15
        self.max_score = 200
        self.naname_include = True
        self.sw = stopwatch

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

        # My logfile
        self.logger = logging.getLogger('ZOO').getChild("HEBI")

    # getSortedCryList
    def getSortedCryList(self, scan_path, scan_prefix, phi_center, isWeakScan=False):
        self.logger.debug("HEBI.getSortedCryList starts")
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

    # left_face_path=self.do2Dscan("lface",lpos,conditions,phi_center)
    def do2Dscan(self, scan_id, center, cond, phi_center):
        self.logger.info("A precise 2D scan at the face angle starts")
        scan_hbeam = 2.0
        scan_vbeam = 5.0
        vrange_um = 35.0
        hrange_um = 35.0
        hstep_um = 2.0
        vstep_um = 5.0
        scan_mode = "2D"
        # Wavelength is limited to 1.0A. Transmission is set to 10%
        wl = cond['wavelength']
        hebi_att = cond['hebi_att']

        print("Face scan at XYZ=", center)
        try:
            # Limited to 50 Hz
            schfile, raspath = self.lm.rasterMaster(scan_id, scan_mode, center, vrange_um, hrange_um,
                                                    vstep_um, hstep_um, phi_center, cond, isHEBI=True)
            print(schfile)

            self.zoo.doRaster(schfile)
            self.zoo.waitTillReady()
        except:
            raise MyException.MyException("HEBI.do2Dscan : Failed.")

        return raspath

    # Modified on 26th Jan 2019
    # Logging a lot 
    # Scan speed is currently checked
    def doVscan(self, prefix, center, cond, phi):
        self.logger.info("HEBI.doVscan: starts\n")
        # unit = [um]
        scan_hbeam = cond['ds_hbeam']
        scan_vbeam = cond['ds_vbeam']
        self.logger.info("Raster beamsize %5.1f(H) x %5.1f(V) [um]" % (scan_hbeam, scan_vbeam))
        # This length is a 'class' variant
        vrange_um = self.vscan_length
        # V step is set to 'half' length of the vertical beam size
        vstep_um = scan_vbeam / 2.0
        scan_mode = "Vert"
        # Dummy for vertical scan
        hrange_um = 1.0
        hstep_um = 1.0
        # Wavelength is limited to 1.0A. Transmission is set to 10%
        wl = cond['wavelength']
        hebi_att_origin = cond['hebi_att']

        # Checking the speed of vertical scan (should be smaller than 500um/sec)
        exp_origin = cond['exp_raster']
        self.logger.info("Initial exposure time: %8.3f[sec]" % exp_origin)
        vert_velocity = vstep_um / exp_origin

        self.logger.info("Scan velocity (ESA): %8.3f[um/sec]" % vert_velocity)
        if vert_velocity > self.limit_of_vert_velocity:
            exp_raster = vstep_um / self.limit_of_vert_velocity
            # Attenuation factor should be more for 'longer' exposure time
            factor_increase_exp = exp_raster / exp_origin
            self.logger.info("Vertical scan velocity is too fast. Limit = %8.2f[um/s]" % vert_velocity)
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
        self.logger.info("HEBI.doVscan: exposure time is replaced by %8.3f [sec]" % exp_raster)

        message = "Scan center (%9.4f, %9.4f, %9.4f)" % (center[0], center[1], center[2])
        self.logger.info(message)

        # 2019/06/03 rasterMaster was modified
        # def rasterMaster(self, scan_id, scan_mode, gxyz, vscan_um, hscan_um, vstep_um, hstep_um, phi, cond):
        schfile, raspath = self.lm.rasterMaster(prefix, scan_mode, center, vrange_um, hrange_um,
                                                vstep_um, hstep_um, phi, cond, isHEBI=True)
        self.zoo.doRaster(schfile)
        self.zoo.waitTillReady()

        return raspath

    # method "peak_xyz" : return xyz coordinate from the heatmap
    def ana2Dscan(self, diffscan_path, prefix, phi_center, method="peak_xyz", isWeakScan=False):
        # Get score-sorted crystal list
        sorted_crystal_list = self.getSortedCryList(diffscan_path, prefix, phi_center, isWeakScan)

        # There are no good crystals
        if len(sorted_crystal_list) == 0:
            raise MyException.MyException("HEBI.ana2Dscan : no crystals are found in scan %s" % prefix)

        the_best_crystal = sorted_crystal_list[0]
        if method == "peak_xyz":
            rtn_xyz = the_best_crystal.getPeakCode()
        elif method == "left_lower":
            rtn_xyz = the_best_crystal.getLLedge()
        elif method == "right_upper":
            rtn_xyz = the_best_crystal.getRUedge()

        return rtn_xyz

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
    def getRescanDist(self, index, LorR):
        gaburiyoru_mm = self.gaburiyoru_h_length / 1000.0  # [mm]
        y_abs = float(index) * gaburiyoru_mm
        # Left edge
        if LorR == "Left":
            return -1.0 * y_abs
        else:
            return +1.0 * y_abs

    def doSingle(self, center_xyz, cond, phi_face, prefix):
        start_phi = phi_face - cond['total_osc'] / 2.0
        end_phi = phi_face + cond['total_osc'] / 2.0
        try:
            gonio_list = []
            gonio_list.append(center_xyz)
            prefix = "single_from_helical"
            multi_sch = self.lm.genMultiSchedule(phi_face, gonio_list, cond, self.phosec_meas, prefix=prefix)
            self.logger.info("MultiSchedule class was used to generate the schedule file.\n")
            self.logger.info("Data collection will be started by using %s.\n" % multi_sch)
            self.zoo.doDataCollection(multi_sch)
            self.zoo.waitTillReady()
        except Exception as e:
            self.logger.info("Exception: %s\n" % e)
            self.logger.info("HEBI.doSingle: ERRors occured in data collection loop.\n")

    def doHelical(self, left_xyz, right_xyz, cond, phi_face, prefix):
        self.logger.info("Exposure condition will be considered from now...")

        start_phi = phi_face - cond['total_osc'] / 2.0
        end_phi = phi_face + cond['total_osc'] / 2.0
        try:
            # crystal size is smaller than horizontal beam size
            # helical data collection is switched to 'single irradiation mode'
            cry_y_len = numpy.fabs(left_xyz[1] - right_xyz[1]) * 1000.0 # [um]
            self.logger.info("Crystal length for this measurement: %8.3f [um]" % cry_y_len)

            #if cry_y_len <= cond['ds_hbeam']:
            if cry_y_len <= (2.0 * cond['ds_hbeam']):
                self.logger.info("Crystal size is smaller than the horizontal beam size (%5.2f [um])" % cond['ds_hbeam'])
                self.logger.info("Helical data collection is swithced to the single irradiation mode")
                self.doSingle(left_xyz, cond, phi_face, prefix)
            else:
                self.logger.info("Generate helical schedule file")
                helical_sch = self.lm.genHelical(start_phi, end_phi, left_xyz, right_xyz, prefix, self.phosec_meas, cond)

                self.logger.info("Schedule file has been prepared with LM.genHelical")
                self.zoo.doDataCollection(helical_sch)
                self.zoo.waitTillReady()
        except Exception as e:
            self.logger.info("Exception: %s\n" % e)
            self.logger.info("HEBI.doHelical: ERRors occured in data collection loop.\n")

        # When the data collection finished.
        # self.sw.setTime("end")
        # consumed_time=self.sw.getDsecBtw("start","end")
        # self.logfile.write("Consuming time for this crystal %5.1f[sec]\n"%(consumed_time))

    # Crystal edge: Left/Right vertical scan to define crystal position in 3D
    def edgeCentering(self, cond, phi_face, rough_xyz, LorR = "Left", cry_index=0):
        ####################
        # Y(L) + 0.005 mm
        # Y(R) + 0.005 mm
        ####################
        if LorR == "Left":
            prefix = "lv%02d" % cry_index
            ref_rot = -90.0
        elif LorR == "Right":
            prefix = "rv%02d" % cry_index
            ref_rot = 90.0
        else:
            prefix = "single"
            ref_rot = -90.0

        self.logger.info("Vertical scan started.\n")
        vertical_index = 0
        initial_y = rough_xyz[1]
        new_xyz = 0.0, 0.0, 0.0

        while (True):
            self.logger.info("%s vertical scan started." % LorR)
            # Vertical scan
            phi_lv = phi_face + ref_rot
            scan_prefix = "%s_%02d" % (prefix, vertical_index)
            step_diff = self.getRescanDist(vertical_index, LorR)
            mod_y = initial_y + step_diff
            mod_xyz = rough_xyz[0], mod_y, rough_xyz[2]
            self.logger.info(
                "%s scan is started at %9.4f %9.4f %9.4f\n" % (LorR, mod_xyz[0], mod_xyz[1], mod_xyz[2]))
            scan_vert_path = self.doVscan(scan_prefix, mod_xyz, cond, phi_lv)
            try:
                new_xyz = self.anaVscan(scan_vert_path, scan_prefix, phi_lv, method="peak_xyz", isWeakScan=False)
                self.logger.info("FOUND %s= (%9.4f %9.4f %9.4f)" % (prefix, new_xyz[0], new_xyz[1], new_xyz[2]))
            except:
                print("Analyze vertical scans failed.\n")
                self.logger.info("HEBI.mainLoop: %s vertical scan analysis failed." % LorR)
                self.logger.info("HEBI.mainLoop: increment Y coordinate by %8.4f mm" % self.gaburiyoru_h_length)
                vertical_index += 1
                if vertical_index > self.gaburiyoru_ntimes:
                    raise MyException("Left vertical scan finally failed.\n")
                else:
                    continue
            if new_xyz[0] != 0.0:
                return new_xyz

    # Before running this routine
    # 2D scan at face angle should be done in common preparation step
    def mainLoop(self, scan_path_2dface, scan_prefix_2dface, phi_face, cond, precise_face_scan=False):
        # The first 2D scan at face angle
        #   def getSortedCryList(self,scan_path,scan_prefix,phi_center):
        # The score threshold is derived from 'cond':score_min
        self.min_score = cond['score_min']
        self.max_score = cond['score_max']
        self.logger.debug("HEBI.mainLoop -> self.getSortedCryList")
        sorted_crylist = self.getSortedCryList(scan_path_2dface, scan_prefix_2dface, phi_face, isWeakScan=False)
        self.logger.info("# of found crystals: %05d\n" % len(sorted_crylist))

        if len(sorted_crylist) == 0:
            self.logger.info("No crystals were found\n")
            return 0

        self.logger.info("Max hits analysis...")
        # the number of crystals
        n_max = cond['maxhits']
        self.logger.info("# of Max crystals: %05d\n" % n_max)

        # Notification for me in future
        # When several crystals were found, and some of them could not be found in raster scan,
        # this routine currently cannot treat the case well. The reason is that
        n_crystals = 0
        cry_index = 0
        for crystal in sorted_crylist:
            rpos, lpos = crystal.getRoughEdges()
            self.logger.info("Right position 2D scan: %9.4f %9.4f %9.4f" % (rpos[0], rpos[1], rpos[2]))
            self.logger.info("Left  position 2D scan: %9.4f %9.4f %9.4f" % (lpos[0], lpos[1], lpos[2]))

            # Precise face scan for tiny crystal
            if precise_face_scan == True:
                print("Precise face scan starts")
                self.logger.info("HEBI.mainLoop: Precise face scan starts\n")
                try:
                    lface_prefix = "lface%02d" % cry_index
                    left_face_path = self.do2Dscan(lface_prefix, lpos, cond, phi_face)
                except:
                    print("L face scan failed.")
                    self.logger.info("HEBI.mainLoop: L face scan failed.\n")
                    continue
                try:
                    rface_prefix = "rface%02d" % cry_index
                    right_face_path = self.do2Dscan(rface_prefix, rpos, cond, phi_face)
                except:
                    print("R face scan failed.")
                    self.logger.info("HEBI.mainLoop: R face scan failed.\n")
                    continue
                # Analyses of scanned map
                try:
                    left_face_xyz = self.ana2Dscan(left_face_path, lface_prefix, phi_face, method="left_lower",
                                                   isWeakScan=True)
                    self.logger.info("Left  position precise 2D scan: %9.4f %9.4f %9.4f\n" % (
                    left_face_xyz[0], left_face_xyz[1], left_face_xyz[2]))
                except:
                    print("Analyze left scan failed.")
                    self.logger.info("HEBI.mainLoop: Left face scan failed.\n")
                    continue
                try:
                    right_face_xyz = self.ana2Dscan(right_face_path, rface_prefix, phi_face, method="right_upper",
                                                    isWeakScan=True)
                    self.logger.info("Right position precise 2D scan: %9.4f %9.4f %9.4f\n" % (
                    right_face_xyz[0], right_face_xyz[1], right_face_xyz[2]))
                except:
                    print("Analyze left scan failed.")
                    self.logger.info("HEBI.mainLoop: Right face scan failed.\n")
                    continue
            # for large crystals
            else:
                self.logger.info("HEBI.mainLoop: Precise scan is skipped.")
                left_face_xyz = lpos
                right_face_xyz = rpos

            # This is debug function for 'LR' vertical centering
            # Left and right rough position is shifted by 50 um
            # XYZ coordinate is treated as 'tuple' object. This is not so nice design...2019/06/30
            if self.debug_LR == True:
                new_ly = left_face_xyz[1] + 0.05
                new_ry = right_face_xyz[1] - 0.05
                left_face_xyz = left_face_xyz[0], new_ly, left_face_xyz[2]
                right_face_xyz = right_face_xyz[0], new_ry, right_face_xyz[2]

            # check crystal size along the rotation axis
            rough_crystal_um = numpy.fabs(left_face_xyz[1] - right_face_xyz[1]) * 1000.0
            self.logger.info("Rough crystal size   = %5.2f [um]\n" % rough_crystal_um)
            self.logger.info("Defined crystal size = %5.2f [um]\n" % cond['cry_min_size_um'])

            size_threshold = cond['ds_hbeam'] * 2.0
            self.logger.info("Size threshold = %5.2f [um]\n" % size_threshold)

            if rough_crystal_um <= size_threshold:
                self.logger.info("%5.2f [um] crystal is smaller than %5.2f [um] limit." % (
                    rough_crystal_um, size_threshold))
                self.logger.info("Data collection is switched to 'single' irradiation mode.")
                # Left edge vertical centering (loop expansion should be considered)
                newx = (left_face_xyz[0] + right_face_xyz[0])/2.0
                newy = (left_face_xyz[1] + right_face_xyz[1])/2.0
                newz = (left_face_xyz[2] + right_face_xyz[2])/2.0
                center_xyz = newx, newy, newz
                self.logger.info("Center of the coordinate (%8.4f %8.4f %8.4f) was chosen\n" % (newx, newy, newz))
                final_xyz = self.edgeCentering(cond, phi_face, center_xyz, LorR = "Left", cry_index=cry_index)
                self.doSingle(final_xyz, cond, phi_face, "single")

            else:
                print("Entering normal helical sequence.")
                # Left edge vertical centering
                try:
                    left_xyz = self.edgeCentering(cond, phi_face, left_face_xyz, LorR = "Left", cry_index=cry_index)
                except:
                    self.logger.write("Left vertical scan failed.")
                    self.logger.write("Next crystal...")
                    continue
                try:
                    # Right edge vertical centering
                    right_xyz = self.edgeCentering(cond, phi_face, right_face_xyz, LorR = "Right", cry_index=cry_index)
                except:
                    self.logger.write("Right vertical scan failed.")
                    self.logger.write("Next crystal...")
                    continue

                self.logger.info("Left and right edges are normally terminated.")
                self.helical_cry_size = numpy.fabs(left_xyz[1] - right_xyz[1]) * 1000.0 # [um]

                # generate helical schedule file
                # doHelical(self,left_xyz,right_xyz,cond,phi_face,prefix,phosec_meas):
                ds_prefix = "cry%02d" % cry_index
                sch_file = self.doHelical(left_xyz, right_xyz, cond, phi_face, ds_prefix)

            # Crystal index
            cry_index += 1

            # Check the maximum number
            if cry_index == n_max:
                break
        return cry_index


if __name__ == "__main__":
    face_agnle = 60.0
    # def __init__(self,zoo,loop_measurement,logfile):

    zoo = 1
    lm = 2
    log = "test"
    stopwatch = "sw"
    # def __init__(self,zoo,loop_measurement,logfile,stopwatch):
    h2 = HEBI(zoo, lm, log, stopwatch)
    # def getSortedCryList(self,scan_path,scan_prefix,phi_center,isWeakScan=False):
    # sc= h2.getSortedCryList("/isilon/users/target/target/nagano/190121/Auto/1575-07/scan00/2d/","2d_",260.0,isWeakScan=False)
    sc = h2.getSortedCryList("/isilon/users/target/target/AutoUsers/190122/Toma/PF0082-03/scan00/2d", "2d_", 260.0,
                             isWeakScan=False)

    index = 0
    for cry in sc:
        print("############### CRYSTAL = %5d #############" % index)
        cry.printAll()
        print("score=", cry.getTotalScore())
        rpos, lpos = cry.getRoughEdges()
        print("Crystal %d: " % index)
        print("R=", rpos[0], rpos[1], rpos[2])
        print("L=", lpos[0], lpos[1], lpos[2])
        index += 1

    # scan_path_2dface=sys.argv[1]
    # scan_prefix_2dface="2d"
    # h2.mainLoop(scan_path_2dface,scan_prefix_2dface,face_agnel)
    # print h2.anaVscan("/isilon/users/target/target/Staff/kuntaro/181211-esa2/test8/CPS1991-09/scan00/rv/","rv",0.0,isWeakScan=True)
    # print h2.anaVscan("/isilon/users/target/target/Staff/kuntaro/181211-esa2/test8/CPS1991-08/scan00/rv/","rv",0.0)
    # print h2.anaVscan("helical_test/lv-fin-00/","lv-fin-00",0.0)
    # print h2.ana2Dscan("helical_test/rface-00/","rface-00",0.0,method="right_upper")
    # print h2.ana2Dscan("helical_test/lface-00/","lface-00",0.0,method="left_lower")

    # DEBUGGIN
