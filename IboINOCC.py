import socket, os, sys, datetime, cv2, time, numpy

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import pylab as plt
import LargePlateMatching, BS
import File
import DirectoryProc
import LargePlateMatchingBC
import LargePlateMatchingCam2
import Date
import logging
import logging.config


# Largely modified on 2018/07/23

class IboINOCC:
    def __init__(self, device):
        self.DEBUG = False

        # bl32upc5
        # self.capture_host="192.168.163.11"
        self.capture_host = "192.168.163.25"
        self.capture_port = 9203

        # vserv2
        self.cam2_host = "192.168.163.12"
        self.cam2_port = 9203

        self.dev = device
        self.pinimg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large.jpg"

        # Image path
        self.img_path = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"
        # Template path and prefix
        self.template_path = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/"
        self.template_prefix = "sc_"

        self.back_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/bcbg.png"
        self.back_bin1_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/bc_bg_bin1.png"
        self.back_template = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/BackCamera/bc_0_binroi.jpg"
        # 2018/11/07 exptime=2000 binnig x4
        # 2018/11/07 exptime=2500 binnig x4
        self.side_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"
        self.naname_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/naname_bg.png"

        # Default log directory
        self.logdir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Log/"

        # Default binning
        self.bc_focus = 2
        self.bc_normal = 4

        # Side camera ROI
        self.roi_sx0 = 200
        self.roi_sx1 = 430
        self.roi_sy0 = 130
        self.roi_sy1 = 386
        self.ysize = self.roi_sy1 - self.roi_sy0

        # 2019/01/29
        # Side camera view: tuning phi (xrange)
        # 2019/02/08 x width = 90 pixels
        # 2021/06/08 modified
        # self.sc_xmin = 242
        # self.sc_xmax = self.sc_xmin + 90
        # 2021/06/09 15:00 K.Hirata
        self.sc_xmin = 250
        self.sc_xmax = self.sc_xmin + 90

        # ROI was modified on 2018/11/03 K.Hirata
        # ROI was modified on 2019/01/30 K.Hirata
        # ROI was modified on 2021/06/07 K.Hirata
        # Back camera ROI (BIN=2)
        # Centering for YZ directions and PHI template matching
        self.roi_bx0 = 230
        self.roi_bx1 = 352
        self.roi_by0 = 238
        self.roi_by1 = 346

        # Back camera ROI (BIN=1)
        self.roi_b1x0 = 380
        self.roi_b1x1 = 580
        self.roi_b1y0 = 65
        self.roi_b1y1 = 265

        # Back camera ROI for real images (a little bit wider)
        # 2021/06/07 K. Hirata modified.
        self.roi_wx0 = self.roi_bx0 - 20
        self.roi_wx1 = self.roi_bx1 + 20
        self.roi_wy0 = self.roi_by0 - 20
        self.roi_wy1 = self.roi_by1 + 20

        self.roi_nx0 = 230
        self.roi_nx1 = 352
        self.roi_ny0 = 238
        self.roi_ny1 = 335

        # 2019/01/30 setting
        # To define the values, otehon holder should be aligned manuarlly.
        # And feed the side image to 'tune_phi' to estimate 'angle' and 'ymean'
        # The values must be correct position and angle for 'pinting' and 
        # 'precise facing'
        self.pint_ymean = 244
        self.face_phi = 0.0

        self.logger = logging.getLogger('ZOO').getChild("ZooNavigator")
        self.isInit = False

        # Prefix
        self.dprefix = "loop"

    def init(self):
        # Log directory is making for Today
        tds = "%s" % (datetime.datetime.now().strftime("%y%m%d"))
        self.todaydir = "%s/%s" % (self.logdir, tds)

        # Making today's directory
        if os.path.exists(self.todaydir):
            self.logger.info("%s already exists" % self.todaydir)
        else:
            os.makedirs(self.todaydir)
            os.system("chmod a+rw %s" % self.todaydir)

        # Loop directory
        dp = DirectoryProc.DirectoryProc(self.todaydir)
        # Get the newest number in 4 digits: like "0001","0099"
        num_prefix = dp.getRoundHeadPrefix(ndigit=4)
        self.loop_dir = "%s/%s_%s" % (self.todaydir, num_prefix, self.dprefix)

        # Making today's directory
        if os.path.exists(self.loop_dir):
            print("%s already exists" % self.loop_dir)
        else:
            os.makedirs(self.loop_dir)
            os.system("chmod a+rw %s" % self.loop_dir)
        # Loop directory
        self.ff = File.File(self.loop_dir)

        self.isInit = True

    def setPrefix(self, dprefix):
        self.dprefix = dprefix

    def setLogDir(self, logdir):
        self.logdir = logdir

    def getImage(self, view, filename, binning=2, sc_exptime=2000):
        if view == "naname" or view == "side":
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.capture_host, self.capture_port))
            client.send("%s,%s,%d,%d" % (view, filename, binning, sc_exptime))
            response = client.recv(4096)
        if view == "back":
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.cam2_host, self.cam2_port))
            client.send("%s" % filename)
            response = client.recv(4096)
        if view == "normal":
            self.dev.capture.capture(filename)
        return True

    def simpleAna(self, targetimg, backimg):
        prefix = targetimg.replace(".png", "")
        subimg = self.procSubtract(targetimg, backimg, opposite=True)
        # Binarization
        # function can be easily modified in it
        th = self.variousBinarize(subimg, mode="aThresh")
        oimg = "%s_bin.png" % prefix
        cv2.imwrite(oimg, th)

        return th

    def procSubtract(self, target_name, bg_name, mode="median", opposite=True, color=False):
        # mode is 'median' and 'birateral'
        if mode == "median":
            print("processing")
            if color == False:
                timg = cv2.imread(target_name, 0)
                bimg = cv2.imread(bg_name, 0)
            else:
                timg = cv2.imread(target_name)
                bimg = cv2.imread(bg_name)

            # Median filter
            b_timg = cv2.medianBlur(timg, 5)
            b_bimg = cv2.medianBlur(bimg, 5)
            if opposite == False:
                subimg = cv2.subtract(b_timg, b_bimg)
                return subimg
            else:
                # For a black holder in a white background -> this should be True!!
                subimg = cv2.subtract(b_bimg, b_timg)
                return subimg
        else:
            print("not yet!")

    def variousBinarize(selfself, cvimg, mode="aThresh"):
        # mode: aThresh = 'adaptiveThreshold' in opencv
        if mode == "aThresh":
            th = cv2.adaptiveThreshold(cvimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            return th
        elif mode == "Thresh":
            th = cv2.threshold(cvimg, 30, 150, cv2.THRESH_BINARY)[1]
            return th
        else:
            print("Not implemented yet.")

    def anaImage(self, targetimg, view, isTemplate=False, gauss=5, bin_thresh=20):
        # picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"
        prefix = targetimg.replace(".png", "")

        # def procSubtract(self, target_name, bg_name, mode="median", opposite=True, color=False):

        # before subtraction
        subimg = self.procSubtract(targetimg, self.back_bg)
        # Binarization
        th = self.variousBinarize(subimg)
        oimg = "%s_bin.png" % (prefix)
        print(("writing %s" % oimg))
        cv2.imwrite(oimg, th)
        # ROI
        if isTemplate:
            roi = self.roiCutter(th, "back")
        else:
            roi = self.roiCutter(th, "back_real")
        cv2.imwrite("%s_binroi.jpg" % prefix, roi)

        return roi

    # Modified on 2021/06/08 K.Hirata
    def captureTestData(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        backimg = os.path.join(picture_path, "bcbg.png")
        for phi in range(0, 30, 10):
            file1 = "%s/bc_%s.png" % (picture_path, phi)
            self.dev.gonio.rotatePhi(phi)
            self.getImage("back", file1)
            # proc before subtraction
            op_img = self.procSubtract(file1, backimg, mode="median", opposite=True, color=False)

            # np_img = self.procSubtract(file1, backimg, mode="median", opposite=False)
            opname = os.path.join(picture_path, "sub_%s_op.png" % phi)
            cv2.imwrite(opname, op_img)
            # npname = os.path.join(picture_path, "sub_%s_np.png"%phi)
            # cv2.imwrite(npname, np_img)
            # Binarization
            binimg = self.variousBinarize(op_img)
            binname = os.path.join(picture_path, "bin_%s.png" % phi)

            cv2.imwrite(binname, binimg)

    # Modified on 2021/06/08 K.Hirata
    # This is used to make 'template images' for back camera now.
    # Flag for 'template' should be swithced ON.
    def makeBCtemplate(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        backimg = os.path.join(picture_path, "bcbg.png")
        for phi in range(0, 360, 10):
            file1 = "%s/bc_%s.png" % (picture_path, phi)
            self.dev.gonio.rotatePhi(phi)
            self.getImage("back", file1)
            # Analyze image
            self.anaImage(file1, view="back", isTemplate=True)

    def roiCutter(self, cvimg, view):
        if view == "back":
            backimg = self.back_bg
            roi_x0 = self.roi_bx0
            roi_x1 = self.roi_bx1
            roi_y0 = self.roi_by0
            roi_y1 = self.roi_by1
        if view == "back_real":
            backimg = self.back_bin1_bg
            roi_x0 = self.roi_wx0
            roi_x1 = self.roi_wx1
            roi_y0 = self.roi_wy0
            roi_y1 = self.roi_wy1
        if view == "back_bin1_wide":
            backimg = self.back_bin1_bg
            roi_x0 = self.roi_b1x0 - 10
            roi_x1 = self.roi_b1x1 + 10
            roi_y0 = self.roi_b1y0
            roi_y1 = self.roi_b1y1
        if view == "side":
            backimg = self.side_bg
            roi_x0 = self.roi_sx0
            roi_x1 = self.roi_sx1
            roi_y0 = self.roi_sy0
            roi_y1 = self.roi_sy1
        if view == "back_wide":
            backimg = self.back_bg
            roi_x0 = self.roi_wx0
            roi_x1 = self.roi_wx1
            roi_y0 = self.roi_wy0
            roi_y1 = self.roi_wy1
        if view == "naname":
            backimg = self.naname_bg
            roi_x0 = self.roi_nx0
            roi_x1 = self.roi_nx1
            roi_y0 = self.roi_ny0
            roi_y1 = self.roi_ny1
        if view == "naname_wide":
            backimg = self.naname_bg
            roi_x0 = self.roi_nx0 - 10
            roi_x1 = self.roi_nx1 + 10
            roi_y0 = self.roi_ny0 - 10
            roi_y1 = self.roi_ny1 + 10

        roi = cvimg[roi_y0:roi_y1, roi_x0:roi_x1]
        return roi

    def captureTestAnalysis(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        for phi in range(0, 360, 10):
            phis = "%03d" % phi
            bcimg = "%s/bc_%s.png" % (picture_path, phis)
            scimg = "%s/sc_%s.png" % (picture_path, phis)
            self.dev.gonio.rotatePhi(phi)
            self.getImage("back", bcimg, 2)
            self.getImage("side", scimg, 4)
            # Analysis
            print("anaImage start")
            self.anaImage(bcimg, "back", bin_thresh=20)
            self.anaImage(scimg, "side", bin_thresh=20)

    # Making backcamera template files for centering
    def makeBackcamTemplate(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/BackCamera/"):
        view = "back"
        prefix = "bc"
        for phi in range(0, 360, 10):
            phis = "%03d" % phi
            bcimg = "%s/bc_%s_template.png" % (picture_path, phis)
            self.dev.gonio.rotatePhi(phi)
            self.getImage(view, bcimg, 2)
            if os.path.exists(bcimg):
                roi = self.anaImage(bcimg, view, bin_thresh=10)
                cv2.imwrite("%s/%s_%s_template.png" % (picture_path, prefix, phi), roi)
            else:
                print("FATAL error!")

    # 2018/07/24
    # Making side-camera template files for centering
    def makeSidecamTemplate(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        view = "side"
        for phi in range(-60, -19, 5):
            phis = "%03d" % phi
            scimg = "%s/sc_%s.png" % (picture_path, phis)
            self.dev.gonio.rotatePhi(phi)
            self.getImage(view, scimg, 4)
            print("anaImage start")
            roi = self.anaImage(scimg, view, bin_thresh=40)
            cv2.imwrite("%s/sc_%s_template.jpg" % (picture_path, phis), roi)

    # This is the main function to achieve the initial 'rough' facing
    # Commented on 2021/06/07 Kunio Hirata
    def testMatchingByCaptureCurrentImage(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_prefix = "bc_"
        template_path = os.path.join(self.template_path, "BackCamera")

        bcimg = os.path.join(picture_path, "tmp.png")
        self.getImage("back", bcimg, 2)

        # (blurred + binarized) ROI extraction
        roi = self.anaImage(bcimg, "back")
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)

        print(ok_file, ok_phi, max_sim)

    # 2018/11/04 Back camera is the farest camera from sample
    # Capture back camera image & template matching of the target holder template to
    # the image
    def captureMatchBackcam(self, isForceToRotate=False):
        if self.isInit == False: self.init()

        template_path = "%s/BackCamera/" % self.template_path
        template_prefix = "bc_"

        # From now, this function captures the image.
        new_idx = self.ff.getNewIdx3()

        bcimg = os.path.join(self.loop_dir, "%03d_bcmatch.png" % new_idx)
        self.getImage("back", bcimg, 2)
        self.logger.info("Back image for 'rough facing' = %s" % bcimg)

        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "back")

        # count white pixels
        whole_area = roi.size
        white_area = cv2.countNonZero(roi)
        white_ratio = white_area/whole_area * 100.0
        self.logger.info("File=%s"%bcimg)
        self.logger.info("Whole: %s white area=%s (ratio %s perc)" % (whole_area, white_area, white_ratio))

        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        new_idx = self.ff.getNewIdx3()
        logimg = os.path.join(self.loop_dir, "%03d_mTemplate.png" % new_idx)
        cv2.imwrite(logimg, roi)

        if max_sim < 0.4 and isForceToRotate==True:
            if numpy.fabs(ok_phi) > 360:
                print("No thank you")
            else:
                self.logger.info("Rotating -%.1f deg." % ok_phi)
                self.dev.gonio.rotatePhiRelative(-ok_phi)
        elif max_sim >= 0.4:
                self.dev.gonio.rotatePhiRelative(-ok_phi)

        return max_sim

    def captureSidecamMatching(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_path = picture_path
        template_prefix = "sc_"

        bcimg = "%s/side.png" % (picture_path)
        self.getImage("side", bcimg, 4)
        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "side", bin_thresh=40)
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        print(ok_file, ok_phi, max_sim)
        self.dev.gonio.rotatePhiRelative(ok_phi)
        return max_sim

    # Remake 2018/07/24 K.Hirata before Gordon conference
    # Remake 2018/11/08 K.Hirata before Kessho gakkai
    def moveToOtehon(self):
        lpm = LargePlateMatching.LargePlateMatching(self.template_path, self.template_prefix)
        filename = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/171212-Okkotonushi/MakingPictures2/cam1/get.png"
        template = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/holder_otehon_0deg.png"
        self.getImage(filename)
        max_value, max_loc = lpm.comp(filename, self.backimg1, template)
        print("LOG", max_value, max_loc)
        # 0.967775225639 (238, 275)
        h_diff = max_loc[0] - 238
        v_diff = max_loc[1] - 275
        print(h_diff, v_diff)

        h_diff_um = h_diff / 0.00684848
        v_diff_um = v_diff / 0.00915152

        print(h_diff_um, v_diff_um)

        self.dev.gonio.moveTrans(h_diff_um)
        self.dev.gonio.moveUpDown(v_diff_um)

        return h_diff_um, v_diff_um, max_value

    def anaim(self, prefix, gauss=5):
        print("Start calcEdge")
        im = cv2.imread(self.pinimg)
        bk = cv2.imread(self.backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        cv2.imwrite("./diff.jpg", dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (gauss, gauss), 0)

        # 2 valuize
        th = cv2.threshold(blur, 20, 150, 0)[1]
        cv2.imwrite("./%s_bin.jpg" % prefix, th)

        # ROI
        print(im.shape)
        # roi=th[self.roi_x0:self.roi_x1,self.roi_y0:self.roi_y1]
        self.roi = th[self.roi_y0:self.roi_y1, self.roi_x0:self.roi_x1]
        cv2.imwrite("%s_binroi.jpg" % (prefix), self.roi)

        return self.roi

    def getTargetROI(self, pinimg):
        im = cv2.imread(pinimg)
        bk = cv2.imread(self.backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (5, 5), 0)

        # 2 valuize
        th = cv2.threshold(blur, 20, 150, 0)[1]

        # ROI
        roiy0 = self.roi_y0 - 20
        roiy1 = self.roi_y1 + 20
        roix0 = self.roi_x0 - 20
        roix1 = self.roi_x1 + 20
        print(roiy0, roiy1, roix0, roix1)
        # self.roi=th[self.roi_y0:self.roi_y1,self.roi_x0:self.roi_x1]
        self.roi = th[roiy0:roiy1, roix0:roix1]

        return self.roi

    # RINKAKU
    def rinkaku(self, prefix):
        print("Start calcEdge")
        im = cv2.imread(self.pinimg)
        bk = cv2.imread(self.backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        cv2.imwrite("./diff.jpg", dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (11, 11), 0)

        # 2 valuize
        # imgray=cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
        th = cv2.threshold(blur, 20, 150, 0)[1]
        cv2.imwrite("./%s.jpg" % prefix, th)

        # ROI
        print(im.shape)
        # roi=th[self.roi_x0:self.roi_x1,self.roi_y0:self.roi_y1]
        self.roi = th[self.roi_y0:self.roi_y1, self.roi_x0:self.roi_x1]
        cv2.imwrite("%s_roi.jpg" % (prefix), self.roi)

        # RINKAKU
        # contours,hierarchy=cv2.findContours(self.roi,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(self.roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contours,hierarchy=cv2.findContours(self.roi,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(self.roi, contours, 0, (0, 255, 0), 3)
        print(len(contours))
        for con in contours:
            print(con)
        cv2.imwrite("%s_rinkaku.jpg" % (prefix), self.roi)
        plt.imshow(self.roi, 'gray')

        print("Image subtraction in calcEdge finished")

    # KUKEI
    def kukei(self, phi):
        self.dev.gonio.rotatePhi(phi)
        prefix = "phi_%03f" % phi
        self.pinimg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/%s.jpg" % prefix
        self.getImage(self.pinimg)
        roi = self.anaim(prefix)

        print("Start calcEdge")
        im = cv2.imread(self.pinimg)
        bk = cv2.imread(self.backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        cv2.imwrite("./diff.jpg", dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (11, 11), 0)

        # 2 valuize
        th = cv2.threshold(blur, 20, 150, 0)[1]
        cv2.imwrite("./%s.jpg" % prefix, th)

        # ROI
        self.roi = th[self.roi_y0:self.roi_y1, self.roi_x0:self.roi_x1]
        cv2.imwrite("%s_roi.jpg" % (prefix), self.roi)

        # RINKAKU
        contours, hierarchy = cv2.findContours(self.roi, cv2.RETR_EXTERNAL, 2)
        cnt = contours[0]

        # print len(cnt)
        ofile = open("phi_%f.dat" % phi, "w")
        xa = []
        ya = []
        xmax = -9999
        ymax = -9999
        xmin = 9999
        ymin = 9999
        ymax_at_xmax = 0.0
        xgsum = 0.0
        ygsum = 0.0
        ndat = 0
        for d in cnt:
            for p in d:
                x, y = p
                ofile.write("%8.3f %8.3f\n" % (x, y))
                if xmax < x:
                    xmax = x
                    ymax_at_xmax = y
                if xmin > x:
                    xmin = x
                if ymax < y:
                    ymax = y
                if ymin > y:
                    ymin = y
                # For gravity calculation
                xgsum += x
                ygsum += y
                ndat += 1

        # Hantaigawa
        y_lower_upper_threshold = ymin + 5
        y_upper_lower_threshold = ymax - 5
        x_lower = 0
        x_upper = 0
        y_lower = 0
        y_upper = 0
        for d in cnt:
            for p in d:
                x, y = p
                if y < ymax and y >= y_upper_lower_threshold:
                    if x_upper < x:
                        x_upper = x
                        y_upper = y
                if y > ymin and y <= y_lower_upper_threshold:
                    if x_lower < x:
                        x_lower = x
                        y_lower = y

        xgrav = xgsum / float(ndat)
        ygrav = ygsum / float(ndat)

        ofile.write("\n\n%8.3f %8.3f\n\n\n" % (x_upper, y_upper))
        ofile.write("%8.3f %8.3f\n\n\n" % (x_lower, y_lower))
        ofile.write("%8.3f %8.3f\n\n\n" % (xmax, ymax_at_xmax))
        ofile.write("%8.3f %8.3f\n\n\n" % (xgrav, ygrav))

        # The leftest point (diff from grav_y)
        dy = ymax_at_xmax - ygrav
        ywidth = ymax - ymin

        # Gradient between the rightest point and another edge
        rx = xmax
        ry = ymax_at_xmax

        # Rightest point is nearby upper
        if dy > 0.0:
            ax = x_lower
            ay = y_lower
        else:
            ax = x_upper
            ay = y_upper

        # Max point to another
        if (ax - rx) != 0.0:
            gradient = float(ay - ry) / float(ax - rx)
        else:
            gradient = 0.0
            print("ax-rx was 0.0")

        # print phi,gradient
        print("CHECK", phi, ywidth, dy, gradient)

        # print x_upper,y_upper,x_lower,y_lower,xgrav,ygrav
        # x,y,w,h=cv2.boundingRect(cnt)
        # print x,y,w,h
        # print x,y,x+w,y+h
        # cv2.rectangle(self.roi,(x,y),(x+w,y+h),(0,255,0),-1)
        # print self.roi.shape
        # cv2.imwrite("kukei.jpg",self.roi)

        # rect=cv2.minAreaRect(
        # cv2.drawContours(self.roi,contours,0,(0,255,0),3)
        # print len(contours)
        # for con in contours:
        # print con
        # cv2.imwrite("%s_rinkaku.jpg"%(prefix),self.roi)
        # plt.imshow(self.roi,'gray')

        print("Image subtraction in calcEdge finished")

    def findRightPosition(self):
        while (1):
            prefix = "findright"
            self.pinimg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/%s.jpg" % prefix
            self.getImage(self.pinimg)

            print("Start calcEdge")
            im = cv2.imread(self.pinimg)
            bk = cv2.imread(self.backimg)

            # GRAY SCALE First this is modified from BL32XU version
            gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

            # Background subtraction
            dimg = cv2.absdiff(gim, gbk)

            # Gaussian blur
            blur = cv2.GaussianBlur(dimg, (11, 11), 0)

            # 2 valuize
            th = cv2.threshold(blur, 15, 150, 0)[1]

            # ROI
            self.roi = th[self.roi_y0:self.roi_y1, self.roi_x0:self.roi_x1]

            # RINKAKU
            contours, hierarchy = cv2.findContours(self.roi, cv2.RETR_EXTERNAL, 2)
            cv2.drawContours(self.roi, contours, 0, (0, 255, 0), 3)
            cv2.imwrite("roi_check.png", self.roi)
            cnt = contours[0]
            print(len(cnt), cnt)
            if len(cnt) < 50:
                continue
            else:
                break

        # print len(cnt)
        ofile = open("findright.dat", "w")
        xa = []
        ya = []
        xmax = -9999
        ymax = -9999
        xmin = 9999
        ymin = 9999
        ymax_at_xmax = 0.0
        xgsum = 0.0
        ygsum = 0.0
        ndat = 0
        print("CONTOURS=", len(cnt))
        for d in cnt:
            for p in d:
                x, y = p
                ofile.write("%8.3f %8.3f\n" % (x, y))
                if xmax < x:
                    xmax = x
                    ymax_at_xmax = y
                if xmin > x:
                    xmin = x
                if ymax < y:
                    ymax = y
                if ymin > y:
                    ymin = y
                # For gravity calculation
                xgsum += x
                ygsum += y
                ndat += 1

        print("XMAX,Y_XMAX", xmax, ymax_at_xmax)
        return xmax, ymax_at_xmax

    # This analyzes x line for detecting line bunch
    def lineAnalysis(self, x_line):
        # print "###################"
        # print x_line
        # print "###################"
        index = 0
        n_found = 0
        none_x = 150
        find_flag = False

        y_len_max_each = 0
        for value in x_line:
            y_cen_max = 0.0
            # print value
            if value > 100 and find_flag == False:
                # print "START",index
                find_flag = True
                ok_y_start = index
                ok_y_end = index
            elif value < 100 and find_flag == True:
                # print "END",index
                find_flag = False
                ylength = ok_y_end - ok_y_start
                # print "YLENGTH=",ylength
                ycenter = (ok_y_end + ok_y_start) / 2.0
                if ylength > 10 and ylength > y_len_max_each:
                    y_len_max_each = ylength
                    y_cen_max_each = ycenter
                    n_found += 1
                    # print "FIND!",y_len_max_each
            elif value > 100 and find_flag == True:
                ok_y_end = index
            else:
                continue
            index += 1
        # edge made OK no baai
        if find_flag == True:
            ycenter = (index + ok_y_start) / 2.0
            ylength = index - ok_y_start
            if ylength > 10 and ylength > y_len_max_each:
                y_len_max_each = ylength
                n_max_each = ycenter
                n_found += 1
                # print "FIND!",y_len_max_each

        if n_found == 0:
            y_cen_max_each = -99.9999

        # print "BEFORE RETURN",y_len_max_each
        return y_len_max_each, y_cen_max_each, n_found

    # for the quick alignment for rotation
    def anaROI2(self, phi):
        # print self.roi.shape
        ok_data = []
        self.dev.gonio.rotatePhi(phi)
        self.getImage()
        prefix = "phi_%03f" % phi
        self.anaim(prefix)
        y_len_max_all = 0.0
        y_len_max_cen = 0.0
        none_x = 150

        print("STARTING PHI=", phi)
        for xline in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140]:
            # print "XLINE=",xline
            find_flag = False
            ok_line = 0
            y_len_max_each, max_y_cen, n_found = self.lineAnalysis(self.roi[:, xline])
            # print "N_FOUND=",n_found,max_y_cen
            if n_found > 0:
                ok_data.append((xline, y_len_max_each, max_y_cen))
                if y_len_max_each > y_len_max_all:
                    y_len_max_all = y_len_max_each
                    y_len_max_x = xline
                    y_len_max_cen = max_y_cen

            # Line not found
            elif n_found == 0:
                if none_x > xline:
                    print("NOT FOUND", xline, none_x)
                    none_x = xline

        print("NONE X=", none_x)
        # good_index=none_x-20
        hashi_index1 = none_x - 20
        hashi_index2 = none_x - 10
        ofile = open("phi.dat", "a")
        edge_sum = 0.0
        for x, y, cen in ok_data:
            if x == hashi_index1 or x == hashi_index2:
                edge_sum += cen
            if x == hashi_index2:
                cen = edge_sum / 2.0
                ofile.write("PHI,y,max_cen,edge_cen,diff= %8.5f %8.5f %8.5f %8.5f %8.5f\n" % (
                    phi, y_len_max_all, cen, y_len_max_cen, y_len_max_cen - cen))

        return y_len_max_all

    def align2D(self):
        # print self.roi.shape
        ok_data = []
        filename = "align2d.jpg"
        self.getImage(filename)
        prefix = "align2d"
        self.pinimg = filename
        self.anaim(prefix, gauss=5)
        y_len_max_all = 0.0
        y_len_max_cen = 0.0
        none_x = 150

        # Align horizontal direction
        # Search good and long bunch pixels from RIGHT

        for xline in numpy.arange(140, 0, -1):
            find_flag = False
            ok_line = 0
            # y_len_max_each : the longest good bunch pixels in this line
            # max_y_cen      : the middle point of the longest good bunch pixels in this line
            # n_found	 : number of found bunch pixels in this line
            y_len_max_each, max_y_cen, n_found = self.lineAnalysis(self.roi[:, xline])
            if y_len_max_each > 50:
                break
        diff_hori = xline - 99
        move_y_um = diff_hori / -0.00686466
        print("moving gonio Y ", move_y_um)
        self.dev.gonio.moveTrans(-move_y_um)

        # print self.roi.shape
        for yline in numpy.arange(119, 0, -1):
            find_flag = False
            ok_line = 0
            # y_len_max_each : the longest good bunch pixels in this line
            # max_y_cen      : the middle point of the longest good bunch pixels in this line
            # n_found	 : number of found bunch pixels in this line
            y_len_max_each, max_y_cen, n_found = self.lineAnalysis(self.roi[yline, :])
            # print y_len_max_each
            if y_len_max_each > 50:
                break
        # print yline
        diff_vert = yline - 93
        move_v_um = diff_vert / -0.00963158
        print(yline, diff_vert, move_v_um)
        self.dev.gonio.moveUpDown(-move_v_um)
        print("moving gonio UpDown ", move_v_um)
        return xline, yline

    def captureROI(self, phi):
        self.dev.gonio.rotate(phi)
        self.getImage()

    # Template pictures to detect 'rotation angle' of a goniometer.
    # 2021/06/07 K. Hirata modified the part.
    def makeTemplateFiles(self, path, prefix):
        # FIRST: you should move to the center the holder
        # SECOND: run this routine
        # def getImage(self, view, filename, binning=2, sc_exptime=2000):

        roi_x0 = 230
        roi_x1 = 352
        roi_y0 = 238
        roi_y1 = 335

        backimage = "LargeHolder/Data/bc_2106071026.png"
        for phi in numpy.arange(0, 360, 10.0):
            self.dev.gonio.rotatePhi(phi)
            filename = "%s/%s_%s.png" % (path, prefix, phi)

            print(filename)
            self.getImage("back", filename, binning=2)

            im = cv2.imread(filename)
            bk = cv2.imread(backimage)

            # GRAY SCALE First this is modified from BL32XU version
            gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)
            dimg = cv2.absdiff(gim, gbk)
            cv2.imwrite("bin.png", dimg)
            # Gaussian blur
            blur = cv2.GaussianBlur(dimg, (3, 3), 0)
            # 2 valuize
            th = cv2.threshold(blur, 20, 150, 0)[1]
            # ROI
            self.roi = th[roi_y0:roi_y1, roi_x0:roi_x1]
            cv2.imwrite("%s/%s_%s_template.png" % (path, prefix, phi), self.roi)

    def translateToCenter(self):
        # Gonio Y(+) -> pix(-)
        um2pix = -0.00368421
        good_position = 202

        lpm = LargePlateMatching.LargePlateMatching(self.template_path, self.template_prefix)
        prefix = "test"
        filename = "./%s.jpg" % prefix
        self.getImage(filename)
        hori, ver = lpm.getPosition(filename)
        print(hori, ver)
        # Gonio Y direction
        diff_x = hori - good_position
        moving_um = diff_x / um2pix
        print("Y,DIFF_Y", hori, diff_x, moving_um)

    def translateToCenterROI(self):
        # Gonio Y(+) -> pix(-)
        um2pix = -0.00368421
        good_position = 202

        lpm = LargePlateMatching.LargePlateMatching(self.template_path, self.template_prefix)
        prefix = "test"
        filename = "./%s.jpg" % prefix
        self.getImage(filename)
        roi_image = self.getTargetROI(filename)
        hori, ver = lpm.getPosition2(roi_image)
        print(hori, ver)
        # Gonio Y direction
        diff_x = hori - good_position
        moving_um = diff_x / um2pix
        print("Y,DIFF_Y", hori, diff_x, moving_um)

    def rotateToFace(self):
        lpm = LargePlateMatching.LargePlateMatching(self.template_path, self.template_prefix)
        init_phi = self.devlgonio.getPhi()
        max_similarity = 0.0
        max_phi = 0.0
        for relative_phi in [-7.5, -5.0, -2.5, 0.0, 2.5, 5.0, 7.5]:
            phi = init_phi + relative_phi
            self.dev.gonio.rotatePhi(phi)
            prefix = "test"
            filename = "./%s.jpg" % prefix

            self.getImage(filename)
            im = cv2.imread(filename)
            bk = cv2.imread(self.backimg1)

            # GRAY SCALE First this is modified from BL32XU version
            gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

            # Diff with background
            dimg = cv2.absdiff(gim, gbk)

            # Gaussian blur
            blur = cv2.GaussianBlur(dimg, (5, 5), 0)

            # 2 valuize
            th = cv2.threshold(blur, 20, 150, 0)[1]
            ok_file, ok_phi, similarity = lpm.match(th)

            print("(Matched PHI(relative),Similarity,PHI(abs))=", ok_phi, similarity, phi)
            if ok_phi == 0.0 or ok_phi == 180.0:
                if max_similarity < similarity:
                    max_similarity = similarity
                    max_phi = phi
        print("Rotating to the max phi", max_phi)
        self.dev.gonio.rotatePhi(max_phi)

    def recoverFaceAngle(self):
        prefix = "test"
        filename = "./%s.jpg" % prefix
        self.getImage(filename)

        print("Start calcEdge")
        im = cv2.imread(filename)
        bk = cv2.imread(self.backimg1)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        cv2.imwrite("./diff.jpg", dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (5, 5), 0)

        # 2 valuize
        th = cv2.threshold(blur, 20, 150, 0)[1]

        lpm = LargePlateMatching.LargePlateMatching(self.template_path, self.template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(th)
        if ok_phi == 180.0 or ok_phi == 360.0 or ok_phi == 0.0:
            rel_phi = 0.0
        elif ok_phi > 180.0:
            rel_phi = -(ok_phi - 180.0)
        else:
            rel_phi = -float(ok_phi)
        print(ok_phi, rel_phi)
        self.dev.gonio.rotatePhiRelative(rel_phi)

    def find_under_edge(self, roi_xy):
        under_edge = []
        for xscan in range(self.sc_xmin, self.sc_xmax):
            ymax = 0
            xsave = ysave = 0
            for x, y in roi_xy:
                if xscan == x:
                    if y > ymax:
                        ymax = y
                        xsave = x
                        ysave = y
                    else:
                        continue
                else:
                    continue
            print("CONTOUR=", xsave, ysave)
            under_edge.append((xsave, ysave))

        return under_edge

    # By using side view camera, phi is tuned for large holder
    # Target image is side view camera
    def tune_phi(self, timg):

        # Median blurring is applied to the target image
        dimg = self.procSubtract(timg, self.side_bg, opposite=True)
        # The simple 'threshold' binarization is preferred for the side camera.
        binimg = self.variousBinarize(dimg, mode="Thresh")
        cv2.imwrite("sc_bin.png", binimg)

        # Contours analysis
        contours, hierarchy = cv2.findContours(binimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # Draw contours on picture
        cv2.drawContours(dimg, contours, -1, (133, 255, 133), 3)
        cv2.imwrite("sc_cont.png", dimg)

        # Contour: reduction of dimension
        cnt = self.squeeze_contours(contours)

        # ROI (x axis direction only)
        # To choose region betweeen cryo-nozzle and goniometer
        # Xrange can be set self.sc_xmin, self.sc_xmax
        roi_xy = self.contour_roi(cnt)
        under_edge = self.find_under_edge(roi_xy)
        # Just a logging
        for un in under_edge:
            self.logger.info("UNDER %s %s" % (un[0], un[1]))

        # ymean is used for tuning gonio pint direction
        angle, score, ymean = self.fitting_pix_line(under_edge)
        self.logger.info("angle=%s deg score=%s ymean=%s" % (angle, score, ymean))

        if self.DEBUG:
            print(angle, score, ymean)

        return angle, score, ymean

    # This routine squeeze contours 
    # Reduce the dimensions
    def squeeze_contours(self, contours):
        new_array = []
        # contours structure
        # found contours are included in 'contours'
        # This loop is a treatment for each 'found contour'.
        if self.DEBUG:
            print("Found contours=", len(contours))
            # self.print_contours(contours)
        if len(contours) != 1:
            print("Found contours are not single.")
            # self.print_contours(contours)

        for i, cnt in enumerate(contours):
            # print "Before squeeze:",cnt.shape
            # Delete non-required dimension
            cnt = numpy.squeeze(cnt)
            # print "after squeeze:",cnt.shape
            # cnt=cnt[cnt[:,0].argsort()]
            new_array.append(cnt)

        return new_array

    def print_contours(self, contours):
        for contour in contours:
            if len(contour.shape) == 1:
                print(contour)
                continue
            else:
                print(contour)
                ndata, dummy = contour.shape
                for i in range(0, ndata):
                    print(contour[i])

    # This routines limits a given contours to the preferred
    # region defined at the header of this file.
    def contour_roi(self, contours):
        roi_xy = []

        def isInRange(x):
            if x >= self.sc_xmin and x <= self.sc_xmax:
                return True
            else:
                return False

        for contour in contours:
            if len(contour.shape) == 1:
                x, y = contour
                if isInRange(x):
                    roi_xy.append((x, y))
                continue
            else:
                ndata, dummy = contour.shape
                for i in range(0, ndata):
                    x, y = contour[i]
                    if isInRange(x):
                        roi_xy.append((x, y))
        return roi_xy

    def find_lower_edge(self, roi_xy):
        lower_edge = []
        # Loop 1
        for xscan in range(self.sc_xmin, self.sc_xmax):
            ymax = 0
            xsave = ysave = 0
            # Loop2
            for x, y in roi_xy:
                if xscan == x:
                    if y > ymax:
                        ymax = y
                        xsave = x
                        ysave = y
                    else:
                        continue
                else:
                    continue
            # print "CONTOUR=",xsave,ysave
            lower_edge.append((xsave, ysave))

        return lower_edge

    def find_upper_edge(self, roi_xy):
        upper_edge = []
        for xscan in range(self.sc_xmin, self.sc_xmax):
            ymin = 999
            xsave = ysave = 0
            for x, y in roi_xy:
                if xscan == x:
                    if y < ymin:
                        ymin = y
                        xsave = x
                        ysave = y
                    else:
                        continue
                else:
                    continue
            if self.DEBUG:
                print("CONTOUR=", xsave, ysave)
            upper_edge.append((xsave, ysave))

        return upper_edge

    # 2019/02/05 inserted from MBP13 version
    # holder width is calculated in this routine
    def analyzeWidth(self, lower_contour, upper_contour):
        dy_list = []
        for each_lc in lower_contour:
            lx, ly = each_lc
            for each_uc in upper_contour:
                ux, uy = each_uc
                if ux == lx:
                    dy = uy - ly
                    dy_list.append(dy)
                    continue

        dya = numpy.array(dy_list)
        thick_mean = numpy.fabs(dya.mean())
        thick_std = dya.std()
        self.logger.info("Thick mean = %s(Std: %s)" % (thick_mean, thick_std))

        return thick_mean, thick_std

    # Fitting 1D for X,Y of under-edge of the loop
    # from side view camera
    def fitting_pix_line(self, xy_array):
        # Making X,Y numpy array
        xlist = []
        ylist = []
        for x, y in xy_array:
            xlist.append(x)
            ylist.append(y)

        xa = numpy.array(xlist)
        ya = numpy.array(ylist)

        # Linear arregression
        a, b = numpy.polyfit(xa, ya, 1)

        # scoring the fitting
        score = 0.0

        # Print log
        for x, y in zip(xa, ya):
            if self.DEBUG:
                print("FITTED=,", x, a * x + b)
            residual = (a * x + b) - y
            score += residual * residual

        final_score = score / float(len(xa))

        if self.DEBUG:
            print("a=", a)
            print("b=", b)
        angle = numpy.degrees(numpy.arctan(a))
        ymean = numpy.mean(ya)
        ymin = numpy.min(ya)
        ymax = numpy.max(ya)

        self.logger.info("final_score fitting=%s angle=%s ymean=%s" % (final_score, angle, ymean))
        self.logger.info("Y(min) %s Y(max) %s" % (ymin, ymax))

        return angle, final_score, ymean

    # 2018/11/09 Coded from 14_mount_fit_side.py
    def fit_side(self):
        # Rough facing 
        n_fail = 0
        while (1):
            max_similarity = self.captureMatchBackcam()
            if max_similarity > 0.7:
                break
            else:
                n_fail += 1
            if n_fail > 3:
                return False

        # Side view camera
        self.dev.prepCenteringSideCamera()

        # Side camera background
        face_phi = self.dev.gonio.getPhi()
        if face_phi < 0.0:
            face_phi += 360.0

        target_image = "%s/sc.png" % self.img_path

        # Precise facing by using side picture
        # self.pint_ymean = 55.0
        # self.face_phi = -1.46

        self.logger.info("Side capture & analysis will start soon.")
        ifail = 0
        while (1):
            self.getImage("side", target_image, binning=4)
            angle, score, ymean = self.tune_phi(target_image)
            diff_from_good_facing = self.face_phi - angle
            self.logger.info(angle, score, ymean, diff_from_good_facing)
            if score > 100.0:
                self.dev.gonio.rotatePhiRelative(180.0)
                ifail += 1
                continue
            # Finishing condition
            elif score < 40.0:
                print("Good score")
                self.dev.gonio.rotatePhiRelative(-diff_from_good_facing)
                break
            elif numpy.fabs(diff_from_good_facing) < 10.0 and numpy.fabs(diff_from_good_facing) > 3.0:
                self.dev.gonio.rotatePhiRelative(-diff_from_good_facing)
                ifail += 1

            if ifail > 10:
                print("Rough facing value was applied")
                self.dev.gonio.rotatePhi(face_phi)
                break

        # ycenter=self.pint_ymeanch
        pix_resol = 0.0319

        # Align to pint direction
        ifail = 0
        while (1):
            self.getImage("side", target_image, binning=4)
            angle, score, ymean = self.tune_phi(target_image)
            print("Fitting pint score = ", score)

            if score > 100.0:
                self.dev.gonio.rotatePhiRelative(180.0)
                ifail += 1

            print("LOG=", ymean, self.pint_ymean)
            diff_y = ymean - self.pint_ymean
            move_um = diff_y / pix_resol

            print("Dpix(y)=", diff_y)
            print("Dpint[um]=", move_um)

            if numpy.fabs(move_um) < 3.0:
                break

            elif numpy.fabs(move_um) < 1500.0:
                self.dev.gonio.movePint(move_um)
                ifail += 1

            if ifail > 5:
                self.dev.gonio.rotatePhiRelative(180.0)

        return True

    # Modified on 2021/06/08 K.Hirata
    # this function was previously coded on 'LargePlateMatchingBC.py'
    # But the structure is confusing and refactored.
    def getHoriVer(self, cvimg_bin):
        if self.isInit == False: self.init()

        template = cv2.imread(self.back_template, 0)
        h, w = template.shape[0], template.shape[1]

        result = cv2.matchTemplate(template, cvimg_bin, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # self.logger.info("MAX_LOC=%s"%max_loc)
        self.logger.info("Top left=%s Bottom right=%s" % (top_left, bottom_right))
        cv2.rectangle(cvimg_bin, top_left, bottom_right, (125, 125, 125), 2)
        # out image
        newidx = self.ff.getNewIdx3()
        fname = os.path.join(self.loop_dir, "%03d_template_loc.png" % newidx)
        cv2.imwrite(fname, cvimg_bin)

        return max_loc

    # 2018/11/09
    # Copy from 19_recover_tateyoko.py
    # 2021/06/08 17:02 K.Hirata modified.
    def fit_tateyoko(self):
        if self.isInit == False: self.init()
        # Basic information
        # ROI center for ideal position
        # 2019/2/11 version
        # x0 = 254
        # y0 = 274
        # trans_resol = 0.006727
        # vert_resol = 0.0092727
        # 2021/06/08
        x0 = 230
        y0 = 238

        trans_resol = 0.0068
        vert_resol = 0.0094

        for i in range(0, 3):
            x, y = self.calcTransHVpix(i)

            # diff
            diffx = x - x0
            diffy = y - y0

            # movement
            trans_um = diffx / trans_resol
            vert_um = diffy / vert_resol

            self.logger.info("Trans= %s pix %s um" % (diffx, trans_um))
            self.logger.info("Vert = %s pix %s um" % (diffy, vert_um))

            if numpy.fabs(trans_um) < 25.0 and numpy.fabs(vert_um) < 25.0:
                break

            if numpy.fabs(trans_um) < 3000.0:
                self.dev.gonio.moveTrans(trans_um)
            if numpy.fabs(vert_um) < 3000.0:
                self.dev.gonio.moveUpDown(vert_um)

    # Coded on 2021/06/08 K.Hirata
    # This is the initial code for XY centering using the back camera.
    def calcTransHVpix(self, file_index):

        # ROI center for ideal position
        self.dev.prepCenteringBackCamera()

        # Subtraction is done here
        newindex = self.ff.getNewIdx3()
        fname = os.path.join(self.loop_dir, "%03d_bintrans.png" % newindex)
        self.getImage("back", fname, binning=2)
        # Analyze
        th = self.simpleAna(fname, self.back_bg)
        newindex = self.ff.getNewIdx3()
        fname = os.path.join(self.loop_dir, "%03d_fittrans.png" % newindex)

        cv2.imwrite(fname, th)
        max_loc = self.getHoriVer(th)
        x, y = max_loc

        return x, y

    def anaImageBilateral(self, capimg):
        img = cv2.imread(capimg, 0)
        fimg = cv2.bilateralFilter(img, 15, 20, 20)
        cv2.imwrite("ffff.png", fimg)
        th = cv2.adaptiveThreshold(fimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5)
        # inverse
        inth = cv2.bitwise_not(th)
        return inth

    # 2021/06/10
    # Very simple function to see the lower contour only
    # (lower contour: upper-stream edge of the holder)
    # This function is a 'deteriorated' version of the 'analyzePreciseSideCamera'
    def anaSideCamImage(self, capimg):
        # inverse
        img = cv2.imread(capimg)
        inth = self.anaImageBilateral(capimg)
        cv2.imwrite("bin.png", inth)

        lower_edge = self.getLowerContour(inth)
        # for e in lower_edge:
        #     print(e)
        # cv2.imwrite("Q.png", img)
        l_angle, l_score, l_meany = self.fitting_pix_line(lower_edge)
        self.logger.info("image = %s %8.2f deg." % (capimg, l_angle))
        l_text = "Lower angle = %5.1f score = %5.1f meany = %5.1f" % (l_angle, l_score, l_meany)
        cv2.putText(img, l_text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), thickness=1)
        l_line_start_y = int(l_meany)
        xlen = self.sc_xmax - self.sc_xmin
        l_diff_y = int(xlen * numpy.tan(numpy.radians(l_angle)))
        # Point for 'pint' direction
        cv2.circle(img, (self.sc_xmin, int(l_meany)), 5, (255, 255, 0), thickness=-1)
        cv2.line(img, (self.sc_xmin, l_line_start_y), (self.sc_xmax, l_line_start_y + l_diff_y), (0, 0, 255), 3)
        cv2.imwrite("%s.preana.png" % capimg, img)

        return l_angle, l_meany

    def getLowerContour(self, cvth):
        # Contour finding
        cont1, hi1 = cv2.findContours(cvth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = self.squeeze_contours(cont1)
        cv2.drawContours(cvth, cont1, -1, (0, 125, 125), 2, 2)
        # ROI to analyze 'inclination' of the holder
        roi_xy = self.contour_roi(cnt)
        lower_edge = self.find_lower_edge(roi_xy)

        cv2.imwrite("R.png", cvth)

        return lower_edge

    # this is an important function to align rotation angle
    # of the sample holder.
    # Modified on 2021/06/10 22:30 K.Hirata
    def alignSideRotation(self, isCheckOnly=True):
        if self.isInit == False: self.init()
        # ideal angle : face angle of the holder
        ideal_angle = 5.5
        # Side view camera
        self.dev.prepCenteringSideCamera()

        newindex = self.ff.getNewIdx3()
        imagefile = os.path.join(self.img_path, "%03d_sc4rot.png" % newindex)
        self.getImage("side", imagefile, binning=4, sc_exptime=3000)

        theta_deg, mid_center_x, mid_center_y = self.analyzePreciseSideCamera(imagefile)
        move_angle = ideal_angle - theta_deg
        # calculation mode does not rotate a goniometer.
        if isCheckOnly == False:
            self.dev.gonio.rotatePhiRelative(move_angle)
        else:
            move_angle=0.0

        self.logger.info("rotation for the precise facing = %5.2f deg. (rotate=%8.2f deg)" % (theta_deg, move_angle))
        self.logger.info("Detected position of the holder center along 'a pint axis' = %s" % mid_center_y)

        return move_angle

    def fit_pint_direction(self, sc_exptime=3000):
        if self.isInit == False: self.init()

        # Align to pint direction
        n_max = 3
        # Otehon holder: y origin = 232 @ 2021/06/11 08:30 K. Hirata
        ycenter = 232
        pix_resol = 0.0319

        i_move = 3
        for i in range(0, i_move):
            newindex = self.ff.getNewIdx3()
            imagefile = os.path.join(self.loop_dir, "%03d_sc4pint.png" % newindex)
            self.getImage("side", imagefile, binning=4, sc_exptime=sc_exptime)
            theta_deg, mid_center_x, mid_center_y = self.analyzePreciseSideCamera(imagefile)

            # Difference between the 'correct' position
            diff_y = mid_center_y - ycenter
            move_um = diff_y / pix_resol

            if numpy.fabs(move_um) < 10.0:
                self.logger.info("Pint alignment succeeded. D(move)=%s um" % move_um)
                return True
            else:
                self.logger.info("Moving D(move)=%s um" % move_um)
                self.dev.gonio.movePint(move_um)
                i_move += 1
                if i_move == n_max:
                    return False
                else:
                    continue

    # 2021/06/10 22:39 K. Hirata coded.
    def centerHolder(self, prefix):
        self.dprefix = prefix
        n_fail = 0
        # Rough facing by using the back camera.
        while (1):
            max_similarity = self.captureMatchBackcam(isForceToRotate=False)
            if max_similarity > 0.45:
                break
            else:
                n_fail += 1
            if n_fail > 3 and max_similarity <= 0.30:
                raise Exception("The holder should not exist!!")
            else:
                self.logger.info("The similarity is relatively low. Please check log images carefully.")

        max_repetition = 3
        isPintFinished=False
        isSideRotationFinished=False
        for i in range(0, max_repetition):
            # Rough centering using the back camera.
            self.fit_tateyoko()
            # Tuning the rotation of the holder using the side camera.
            move_angle=self.alignSideRotation()
            # Side tuning finished.
            if move_angle == 0.0: isSideRotationFinished = True

            if isSideRotationFinished and isPintFinished == True:
                self.logger.info("Centering has been finished!")
                return True

            # Edge detections were improved by using longer exposure time of the side camera.
            isPintFinished=self.fit_pint_direction(sc_exptime=3000)

        return False

    # Aligning gonio-meter pint direction by using 'captured holder images'
    def alignGonioPintDirection(self, scan_wing=1000.0, scan_div=10.0):
        if self.isInit == False: self.init()

        # scan step is set to 1/scan_div of scan_wing
        scan_step = scan_wing / scan_div

        # Normal centering for 'videosrv'
        self.dev.prepCentering()
        # Capturing images -> stored into a 'loop directory'
        cap_path = "%s/" % self.loop_dir
        template_prefix = "pints_"

        # Current goniometer XYZ position
        x0,y0,z0 = self.dev.gonio.getXYZmm()

        # Defining pint scan range
        start_x = -scan_wing
        end_x = scan_wing + 10.0

        # An array of (pint_axis, variance_of_image_laplacian)
        ana_array = []
        for pint_movement in numpy.arange(start_x, end_x, scan_step):
            # Move to the original position
            self.dev.gonio.moveXYZmm(x0, y0, z0)
            # Move 'pint' direction
            self.dev.gonio.movePint(pint_movement)
            # From now, this function captures the image.
            new_idx = self.ff.getNewIdx3()
            filename = "%03d_pint%f.png" % (new_idx, pint_movement)
            pintimage = os.path.join(self.loop_dir, filename)
            self.getImage("normal", pintimage)
            vl = self.getVL(pintimage)
            ana_array.append((pint_movement, vl))
            self.logger.info("Pint axis %8.2f [um] Variance of Laplacian = %9.2f" % (pint_movement, vl))

        # Once back to the original position
        self.dev.gonio.moveXYZmm(x0, y0, z0)

        # The maximum VL among captured images.
        sorted_result = sorted(ana_array, key=lambda x:x[1], reverse=True)

        # Pint position is
        max_pint = sorted_result[0][0]
        self.logger.info("The best pint axis was %8.2f [um]" % max_pint)

        # Move 'pint' direction
        self.dev.gonio.movePint(max_pint)

    # Get Variance of Laplasian
    def getVL(self, imagepath):
        # load the image, convert it to grayscale, and compute the
        # focus measure of the image using the Variance of Laplacian
        # method
        text="test"
        image = cv2.imread(imagepath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = self.variance_of_laplacian(gray)

        return fm

    def variance_of_laplacian(self, image):
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        return cv2.Laplacian(image, cv2.CV_64F).var()

    # newly coded on 2021/06/10 17:30 Kunio Hirata
    def analyzePreciseSideCamera(self, targetimage):
        if self.isInit == False: self.init()

        # Data processing directory
        data_file = "%s/anaSideCamera.dat" % (self.loop_dir)
        dfile = open(data_file, "a")

        # For making a log image
        baseimg = cv2.imread(targetimage)
        # No background subtraction : just a bilateral filtering -> threshold
        dimg = self.anaImageBilateral(targetimage)

        # opposite should be true for 'black' holder in 'white' background.
        newindex = self.ff.getNewIdx3()
        outname = os.path.join(self.loop_dir, "%03d_scprec_bin.png" % newindex)
        cv2.imwrite(outname, dimg)
        # Contour finding
        cont1, hi1 = cv2.findContours(dimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = self.squeeze_contours(cont1)
        cv2.drawContours(baseimg, cont1, -1, (0, 255, 0), 3)
        # ROI to analyze 'inclination' of the holder
        roi_xy = self.contour_roi(cnt)
        lower_edge = self.find_lower_edge(roi_xy)
        upper_edge = self.find_upper_edge(roi_xy)

        # Fitting lines to the found contours
        l_angle, l_score, l_meany = self.fitting_pix_line(lower_edge)
        u_angle, u_score, u_meany = self.fitting_pix_line(upper_edge)

        # Just a logging
        for lower in lower_edge:
            lx, ly = lower
            dfile.write("lower: %3d %3d\n" % (lx, ly))
        for upper in upper_edge:
            ux, uy = upper
            dfile.write("upper: %3d %3d\n" % (ux, uy))

        # Picture logging is quite important for this kind of analysis
        l_text = "Lower angle = %5.1f score = %5.1f meany = %5.1f" % (l_angle, l_score, l_meany)
        u_text = "Upper angle = %5.1f score = %5.1f meany = %5.1f" % (u_angle, u_score, u_meany)
        cv2.putText(baseimg, l_text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), thickness=1)
        cv2.putText(baseimg, u_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), thickness=1)
        dfile.write("%s\n" % l_text)
        dfile.write("%s\n" % u_text)

        l_line_start_y = int(l_meany)
        u_line_start_y = int(u_meany)
        xlen = self.sc_xmax - self.sc_xmin

        # Calculation of height difference to draw 'lines' of upper/lower holder shape
        l_diff_y = int(xlen * numpy.tan(numpy.radians(l_angle)))
        u_diff_y = int(xlen * numpy.tan(numpy.radians(u_angle)))

        self.logger.info("L_diff=%s U_diff=%s" % (l_diff_y, u_diff_y))
        # Holder thickness is calculated from 'upper' and 'lower' edges from contour analysis
        thick_mean, thick_std = self.analyzeWidth(lower_edge, upper_edge)

        # Lower line left edge (Y)
        lower_left_y = l_line_start_y
        lower_right_y = l_line_start_y + l_diff_y

        # Upper line left edge (Y)
        upper_left_y = u_line_start_y
        upper_right_y = u_line_start_y + u_diff_y

        # Middle point of left and right
        mid_left_y = int((lower_left_y + upper_left_y) / 2.0)
        mid_right_y = int((lower_right_y + upper_right_y) / 2.0)
        # slope (diff y)
        slope_y = (mid_right_y - mid_left_y) / xlen
        theta = numpy.arctan(slope_y)
        theta_deg = numpy.degrees(theta)

        cv2.line(baseimg, (self.sc_xmin, l_line_start_y), (self.sc_xmax, l_line_start_y + l_diff_y), (0, 0, 255), 3)
        cv2.line(baseimg, (self.sc_xmin, u_line_start_y), (self.sc_xmax, u_line_start_y + u_diff_y), (0, 0, 255), 3)
        cv2.line(baseimg, (self.sc_xmin, mid_left_y), (self.sc_xmax, mid_right_y), (125, 125, 255), 3)

        # The center of the middle line
        mid_center_x = int((self.sc_xmin + self.sc_xmax) / 2.0)
        mid_center_y = int((mid_left_y + mid_right_y) / 2.0)
        cv2.circle(baseimg, (mid_center_x, mid_center_y), 5, (255, 255, 0), thickness=-1)

        # file name
        newindex = self.ff.getNewIdx3()
        fname = os.path.join(self.loop_dir, "%03d_scpre_ana.png" % newindex)
        cv2.imwrite(fname, baseimg)

        # Checking the value
        return theta_deg, mid_center_x, mid_center_y

if __name__ == "__main__":
    import Device

    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc, b_blanc))

    # Log file
    beamline = "BL32XU"
    logname = "./iboinocc.log"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline,
                              defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    dev = Device.Device(s)
    dev.init()

    file1 = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/cam1_test.png"
    # def getImage(self,view,filename,binning=2):

    bs = BS.BS(s)
    inocc = IboINOCC(dev)
    #dev.prepCenteringLargeHolderCam1()

    ### 210607 AOMUSHI week
    apath = os.path.abspath("./TemplateImages/")
    # path="path./TemplateImages/"
    # prefix="holder01"
    # inocc.makeBackcamTemplate()

    ### 210607 15:53 K.Hirata
    # test captureBackcamMatching()
    # inocc.captureMatchBackcam(picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/")

    ## 210608 10:13
    # check various background subtraction
    # inocc.captureTestData2()

    # 210608 11:19
    # check the current template files
    # inocc.testMatchingByCaptureCurrentImage()

    # 210608 11:32
    # inocc.captureMatchBackcam()

    # 210608 13:47
    # Just a trial
    # inocc.fit_side()

    # 210608 15:38
    # Tuning rotation by side camera test
    # inocc.align_rotation("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/test05/")

    # 210608 17:07
    # Tuning the holder height first to achieve better 'precise facing' by
    # inocc.align_rotation()
    # Capture the otehon picture
    # inocc.getImage("back", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/b.png")
    # inocc.fit_test()

    # 210609 16:53
    # Test to align the sample holder to the center position
    # This should be pre-done before the center position.
    # inocc.getImage("side", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/before.png", binning=4)
    # inocc.fit_tateyoko()
    # inocc.getImage("side", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/after.png", binning=4)

    # 210609 17:10
    # Trials to achieve whole alignment procedure
    # inocc.captureMatchBackcam(picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/")
    # inocc.getImage("side", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/before.png", binning=4)
    # inocc.fit_tateyoko()
    # inocc.getImage("side", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/after.png", binning=4)
    # inocc.align_rotation("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/test07/")

    # I noticed that the new shape of the holder is mis-aligned to the X-rays -> 180 deg.
    # 210609 10:00
    # making template pictures for 'back camera'
    # inocc.makeBCtemplate(picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/BackCamera/")

    # 210609 10:12
    # test of 'template pictures'
    # inocc.testMatchingByCaptureCurrentImage()
    # inocc.captureMatchBackcam()

    # 210609 10:16
    # X,Y origin of back camera is determined for the 'correct' orientation of the holder.
    # (X0, Y0) = 230, 238 (top left) at the time.
    # inocc.calcTransHVpix(0)

    # 210609 10:19
    # Test for the translational alignment of the holder to the rough center
    # inocc.fit_tateyoko()
    # inocc.align_rotation("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/test08/")

    # 210609 14:25
    # For more robust way to find edges
    # inocc.anaSideCamImage(sys.argv[1])

    # 210610 15:20
    # inocc.newCheck()

    # 210610 15:30
    # n_fail = 0
    # while (1):
    #     max_similarity = inocc.captureMatchBackcam()
    #     if max_similarity > 0.5:
    #         break
    #     else:
    #         n_fail += 1
    #     if n_fail > 3:
    #         break
    #
    # inocc.fit_tateyoko()
    # inocc.alignSideRotation()
    #
    # # 210610 16:30
    # # Edge detections were improved by using longer exposure time of the side camera.
    # inocc.fit_pint_direction(sc_exptime=3000)
    # inocc.fit_tateyoko()
    # inocc.alignSideRotation()
    # inocc.fit_pint_direction(sc_exptime=3000)
    # Exposure time
    # inocc.getImage("side", scimg, 4)
    # inocc.getImage("side", "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/3000.png", binning=4, sc_exptime=3000)

    # 210610 17:05
    # Longer exposure time
    # inocc.alignSideRotation()
    # inocc.fit_pint_direction()

    # 210610 17:35
    # inocc.onikusan()

    # 210610 22:38
    # obtain center Y coordinate of the "OTEHON" centering
    # inocc.alignSideRotation(isCheckOnly=True)

    # 210611 08:30
    # The all sequence in centering
    # inocc.centerHolder()

    # 210611 08:48 debug
    # inocc.alignSideRotation(isCheckOnly=False)

    # 210611 09:07 defining capturing images
    # inocc.captureMatchBackcam()
    # inocc.fit_tateyoko()
    # inocc.alignSideRotation()
    # inocc.fit_pint_direction()
    # inocc.centerHolder()

    # 210611 12:12 K.Hirata
    # inocc.captureMatchBackcam(isForceToRotate=False)

    # 210611 12:19 K.Hirata
    # inocc.centerHolder("TEST")
    #inocc.captureMatchBackcam(isForceToRotate=False)

    # 210727 11:08 Pint tuning
    inocc.alignGonioPintDirection(scan_wing=1000.0)

