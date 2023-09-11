import os, sys, math, numpy, socket, datetime, time

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio, BS
import Device
import LoopMeasurement
import StopWatch
import MyException
import logging
import AnaHeatmap
import CrystalList
import logging
import logging.config

# 2021/06/10 22:50

beamline="BL32XU"

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc, b_blanc))

    dev = Device.Device(s)
    dev.init()

    zoo = Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # Logger
    logname = "./iboinocc.log"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline,
                              defaults={'logfile_name': logname})

    logger = logging.getLogger('ZOO')

    # preparation
    dev.colli.off()

    flux = 1.2E13 # photons/sec

    # Conditions (normally cond.####)
    cond = {
        'raster_hbeam': 10.0,
        'raster_vbeam': 15.0,
        'att_raster': 100.0,
        'exp_raster': 0.01,
        'dist_raster': 200.0,
        'score_min' : 10,
        'score_max' : 300,
        'maxhits' : 200,
        'total_osc' : 5.0,
        'osc_width' : 0.1,
        'ds_vbeam': 15.0,
        'ds_hbeam': 10.0,
        'exp_ds' : 0.02,
        'dist_ds': 200.0,
        'cry_max_size_um': 20.0,
        'dose_ds' : 10.0,
        'sample_name' : 'nor',
        'scanv_um' : 2000,
        'scanh_um' : 2000,
        'hstep_um' : 10.0,
        'vstep_um' : 15.0,
        'att_idx' : 0,
        'raster_exp' : 0.01,
        'wavelength' : 0.90,
        'reduced_fact' : 1.00,
        'raster_roi': 1,
        'ntimes': 1,
        'cover_scan_flag': 1,
        'sample_name' : 'lysbr',
        'root_dir' : '/isilon/users/target/target/Staff/kuntaro/210727-Okkotonushi/TEST/'
    }

    # Change energy
    # Wavelength is changed
    en = 12.3984 / cond['wavelength']

    curr_en = dev.mono.getE()

    if math.fabs(curr_en - en) > 0.001:
        dev.changeEnergy(en, isTune=True)

    #for puckid in ["CPS2721", "CPS2720"]:
    for puckid in ["CPS2720"]:
        for pinid in [4]:
            # NAGO initialized for each pin
            nago = IboINOCC.IboINOCC(dev)
            prefix = "%s-%02d" % (puckid, pinid)

            nago.setPrefix(prefix)

            stopwatch = StopWatch.StopWatch()
            stopwatch.setTime("start")

            # the backlight should be up before mounting the loop
            dev.light.on()
            # Mounting the loop
            zoo.mountSample(puckid, pinid)
            zoo.waitTillReady()

            stopwatch.setTime("mount_finished")
            starttime = datetime.datetime.now()

            # Alignment with 'beam stopper on'
            nago.captureMatchBackcam()

            # Alignment without 'beam stopper on'
            dev.prepCenteringLargeHolderCam1()
            nago.centerHolder(prefix)

            # Alignment of 'pint' direction
            nago.alignGonioPintDirection(scan_wing=1000.0, scan_div=10.0)

            # Alignment without 'beam stopper on'
            dev.prepCenteringLargeHolderCam1()
            nago.fit_tateyoko()

            sx, sy, sz = dev.gonio.getXYZmm()
            sphi = dev.gonio.getPhi()
            stopwatch.setTime("centering_finished")

            ################# Loop measurement
            lm = LoopMeasurement.LoopMeasurement(s, cond['root_dir'], prefix)
            cxyz = sx, sy, sz
            raster_id = "2d"
            lm.setWavelength(cond['wavelength'])
            lm.prepDataCollection()
            # scan V and H length is fixed
            scanv_um = cond['scanv_um']
            scanh_um = cond['scanh_um']
            vstep_um = cond['raster_vbeam']
            hstep_um = cond['raster_hbeam']

            scan_id="2d"
            scan_mode="2D"
            raster_schedule, raster_path = lm.rasterMaster(scan_id, scan_mode, cxyz,
                                                                scanv_um, scanh_um, vstep_um, hstep_um,
                                                                sphi, cond)

            raster_start_time = time.localtime()
            stopwatch.setTime("raster_start")
            zoo.doRaster(raster_schedule)
            zoo.waitTillReady()
            stopwatch.setTime("raster_end")

            # Raster scan results
            ###################
            # Analyzing raster scan results
            try:
                glist = []
                cxyz = sx, sy, sz
                scan_id = lm.prefix
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
                # self.esa.updateValueAt(o_index, "nds_multi", n_crystals)

                # Writing down the goniometer coordinate list
                gfile = open("%s/collected.dat" % lm.raster_dir, "w")
                gfile.write("# Found crystals = %5d\n" % n_crystals)
                for gxyz in glist:
                    x, y, z = gxyz
                    gfile.write("%8.4f %8.4f %8.4f\n" % (x, y, z))
                gfile.close()

            except MyException as tttt:
                raise Exception("Something wrong in the main data collection loop.")
                sys.exit(1)

            # Number of detected crystals = 0
            if len(glist) == 0:
                logger.info("Skipping this loop!!")
                # Disconnecting capture in this loop's 'capture' instance
                logger.info("Disconnecting capture")
                lm.closeCapture()
                continue

            # Data collection
            time.sleep(5.0)
            data_prefix = "%s-%02d-multi" % (puckid, pinid)
            multi_sch = lm.genMultiSchedule(sphi, glist, cond, flux, prefix=data_prefix)
            time.sleep(5.0)

            dev.gonio.moveXYZmm(sx, sy, sz)
            zoo.doDataCollection(multi_sch)
            zoo.waitTillReady()

            # Writing CSV file for data processing
            sample_name = cond['sample_name']
            root_dir = cond['root_dir']
            # data_proc_file.write("%s/_kamoproc/%s/,%s,no\n" % (root_dir, prefix, sample_name))
            # data_proc_file.flush()

            # Writing Time table for this data collection
            # Disconnecting capture in this loop's 'capture' instance
            logger.info("Data collection has been finished.")
            lm.closeCapture()

            # prep the next data collection
            dev.colli.off()

    zoo.disconnect()
