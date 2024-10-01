import os, sys, math, numpy, socket, datetime

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio, BS
import Device

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc, b_blanc))

    gonio = Gonio.Gonio(s)
    bs = BS.BS(s)
    inocc = IboINOCC.IboINOCC(gonio)

    zoo = Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # preparation
    dev = Device.Device(s)
    dev.init()

    zoo.dismountCurrentPin()
    zoo.waitTillReady()

    dev.prepCenteringLargeHolderCam1()
    inocc.getImage("back1.png")

    # preparation
    dev.prepCenteringLargeHolderCam2()
    inocc.getCam2Image("back2.png")

    zoo.mountSample("HRC1010", 2)
    zoo.waitTillReady()

    starttime = datetime.datetime.now()
    # Recover Face angle
    bs.evacLargeHolder()
    inocc.recoverFaceAngle()
    inocc.recoverFaceAngle()

    # Precise facing
    inocc.rotateToFace()

    cx = 0.7757
    cy = -11.5582
    cz = 0.3020

    for i in range(0, 3):
        dev.prepCenteringLargeHolderCam1()
        ix, iy, iz = dev.gonio.getXYZmm()

        # Max value= 1.0 TOP_LEFT= (238, 275)
        # horizontal resolution -0.00684848
        # vertical resolution -0.00915152
        h_diff_um, v_diff_um, max_2d = inocc.moveToOtehon()
        print("2D=", max_2d)

    # preparation
    # dev.prepCenteringLargeHolderCam2()

    # ((316, 143), 0.97274786233901978)
    # um/pixel=0.0135
    # move_um,max_pint= inocc.moveToOtehonPint()
    # print "PINT=",max_pint

    x, y, z = dev.gonio.getXYZmm()
    dx = x - cx
    dy = y - cy
    dz = z - cz
    diff = math.sqrt(dx * dx + dy * dy + dz * dz)
    print("Distance=%8.3f mm\n" % diff)

    endtime = datetime.datetime.now()
    time_sec = (endtime - starttime).seconds

    print(time_sec)


    def collectMulti(self, trayid, pinid, prefix, cond, sphi):
        # Multiple crystal mode
        # For multiple crystal : 2D raster
        raster_schedule, raster_path = self.lm.prepRaster(dist=cond.distance,
                                                          att_idx=self.att_idx, exptime=cond.raster_exp,
                                                          crystal_id=cond.sample_name)
        raster_start_time = time.localtime()
        self.stopwatch.setTime("raster_start")
        self.zoo.doRaster(raster_schedule)
        self.zoo.waitTillReady()
        self.stopwatch.setTime("raster_end")

        # Raster scan results
        try:
            glist = []
            cxyz = self.sx, self.sy, self.sz
            scan_id = self.lm.prefix
            # Crystal size setting
            if cond.h_beam > cond.v_beam:
                crysize = cond.h_beam / 1000.0 + 0.0001
            else:
                crysize = cond.v_beam / 1000.0 + 0.0001

            glist = self.lm.shikaSumSkipStrongMulti(cxyz, sphi, raster_path,
                                                    scan_id, thresh_nspots=cond.shika_minscore, crysize=crysize,
                                                    max_ncry=cond.shika_maxhits,
                                                    mode="peak")

            n_crystals = len(glist)

            # Time calculation
            t_for_mount = self.stopwatch.getDsecBtw("start", "mount_finished") / 60.0
            t_for_center = self.stopwatch.getDsecBtw("mount_finished", "centering_finished") / 60.0
            t_for_raster = self.stopwatch.getDsecBtw("raster_start", "raster_end") / 60.0
            logstr = "%20s %20s %5d crystals MCRD[min]:%5.2f %5.2f %5.2f" % (
                self.stopwatch.getTime("start"), prefix, n_crystals, t_for_mount, t_for_center, t_for_raster)
            self.zooprog.write("%s " % logstr)
            self.zooprog.flush()

        except MyException as tttt:
            print("Skipping this loop!!")
            self.zooprog.write("\n")
            self.zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print("Disconnecting capture")
            self.lm.closeCapture()
            return
        finally:
            try:
                nhits = len(glist)
                self.html_maker.add_result(puckname=trayid, pin=pinid,
                                           h_grid=self.lm.raster_n_width, v_grid=self.lm.raster_n_height,
                                           nhits=nhits, shika_workdir=os.path.join(self.lm.raster_dir, "_spotfinder"),
                                           prefix=self.lm.prefix, start_time=raster_start_time)
                self.html_maker.write_html()
            except:
                print(traceback.format_exc())

        if len(glist) == 0:
            print("Skipping this loop!!")
            self.zooprog.write("\n")
            self.zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print("Disconnecting capture")
            self.lm.closeCapture()
            return

        # Precise centering
        time.sleep(5.0)
        data_prefix = "%s-%02d-multi" % (trayid, pinid)
        multi_sch = self.lm.genMultiSchedule(sphi, glist, cond.osc_width, cond.total_osc,
                                             cond.exp_henderson, cond.exp_time, cond.distance, cond.sample_name,
                                             prefix=data_prefix)

        time.sleep(5.0)

        self.stopwatch.setTime("data_collection_start")
        self.zoo.doDataCollection(multi_sch)
        self.zoo.waitTillReady()
        self.stopwatch.setTime("data_collection_end")

        # Writing Time table for this data collection
        t_for_ds = self.stopwatch.getDsecBtw("data_collection_start", "data_collection_end") / 60.0
        logstr = "%6.1f " % (t_for_ds)
        self.zooprog.write("%s\n" % logstr)
        self.zooprog.flush()
        # Disconnecting capture in this loop's 'capture' instance
        print("Disconnecting capture")
        self.lm.closeCapture()
