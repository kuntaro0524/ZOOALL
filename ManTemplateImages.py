import socket, os, sys, datetime, cv2, time, numpy

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import pylab as plt
import LargePlateMatching, BS
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
        # 2018/11/07 exptime=2000 binnig x4
        # 2018/11/07 exptime=2500 binnig x4
        self.side_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"
        self.naname_bg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/naname_bg.png"

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
        self.sc_xmin = 320
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
        self.roi_wx0 = 230
        self.roi_wx1 = 352
        self.roi_wy0 = 238
        self.roi_wy1 = 335

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
        return True

    def simpleAna(self, targetimg, backimg, bin_thresh=30):
        prefix = targetimg.replace(".png", "")
        im = cv2.imread(targetimg)
        bk = cv2.imread(backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        oimg = "%s_diff.png" % (prefix)
        cv2.imwrite(oimg, dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (5, 5), 0)

        # 2 valuize
        th = cv2.threshold(blur, bin_thresh, 150, 0)[1]
        oimg = "%s_bin.png" % (prefix)
        print(oimg)
        cv2.imwrite(oimg, th)

        return th

    def anaImage(self, targetimg, view, gauss=5, bin_thresh=20):
        # picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"
        prefix = targetimg.replace(".png", "")
        if view == "back":
            backimg = self.back_bg
            roi_x0 = self.roi_bx0
            roi_x1 = self.roi_bx1
            roi_y0 = self.roi_by0
            roi_y1 = self.roi_by1
        if view == "back_bin1":
            backimg = self.back_bin1_bg
            roi_x0 = self.roi_b1x0
            roi_x1 = self.roi_b1x1
            roi_y0 = self.roi_b1y0
            roi_y1 = self.roi_b1y1
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


        print((targetimg, backimg))
        im = cv2.imread(targetimg)
        bk = cv2.imread(backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bk, cv2.COLOR_BGR2GRAY)

        dimg = cv2.absdiff(gim, gbk)
        oimg = "%s_diff.png" % (prefix)
        print(oimg)
        cv2.imwrite(oimg, dimg)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (gauss, gauss), 0)

        # 2 valuize
        th = cv2.threshold(blur, bin_thresh, 150, 0)[1]
        oimg = "%s_bin.png" % (prefix)
        print(oimg)
        cv2.imwrite(oimg, th)

        # ROI
        print(im.shape)
        # roi=th[roi_x0:roi_x1,roi_y0:roi_y1]
        roi = th[roi_y0:roi_y1, roi_x0:roi_x1]
        cv2.imwrite("%s_binroi.jpg" % prefix, roi)

        return roi

    def captureTestData(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        for phi in range(0, 360, 10):
            file1 = "%s/bc_%s.png" % (picture_path, phi)
            file2 = "%s/sc_%s.png" % (picture_path, phi)
            self.dev.gonio.rotatePhi(phi)
            self.getImage("back", file1)
            self.getImage("side", file2)

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

    # Making backcamera template files for centering (BINNING=1)
    def makeBackcamTemplateBin1(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        view = "back_bin1"
        for phi in range(0, 360, 10):
            phis = "%03d" % phi
            bcimg = "%s/bc1_%s.png" % (picture_path, phis)
            print("capturing ", bcimg)
            self.dev.gonio.rotatePhi(phi)
            self.getImage("back", bcimg, 1)
            print("anaImage start")
            roi = self.anaImage(bcimg, view, bin_thresh=10)
            cv2.imwrite("%s/bc1_%s_template.jpg" % (picture_path, phis), roi)

    # 2018/07/24
    # Making naname-camera template files for centering
    def makeNanamecamTemplate(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        view = "naname"
        for phi in range(0, 360, 10):
            phis = "%03d" % phi
            bcimg = "%s/nc_%s.png" % (picture_path, phis)
            self.dev.gonio.rotatePhi(phi)
            self.getImage(view, bcimg)
            print("anaImage start")
            roi = self.anaImage(bcimg, view, bin_thresh=10)
            cv2.imwrite("%s/nc_%s_template.jpg" % (picture_path, phis), roi)

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
    def captureBackcamMatching(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_path = picture_path
        template_prefix = "bc_"

        bcimg = "%s/tmp.png" % (picture_path)
        self.getImage("back", bcimg, 2)
        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "back_wide", bin_thresh=10)
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        print(ok_file, ok_phi, max_sim)

    def captureBackcamMatchingBin1(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_path = picture_path
        template_prefix = "bc1_"

        bcimg = "%s/bc1.png" % (picture_path)
        self.logger.info("BCIMG=%s" % bcimg)
        self.getImage("back", bcimg, 1)
        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "back_bin1_wide", bin_thresh=10)
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        print(ok_file, ok_phi, max_sim)
        self.dev.gonio.rotatePhiRelative(-ok_phi)

    def captureNanamecamMatching(self, picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_path = picture_path
        template_prefix = "nc_"

        bcimg = "%s/naname.png" % (picture_path)
        self.getImage("naname", bcimg, 2)
        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "naname_wide", bin_thresh=10)
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        self.dev.gonio.rotatePhiRelative(-ok_phi)
        return max_sim

    # 2018/11/04 Back camera is the farest camera from sample
    # Capture back camera image & template matching of the target holder template to
    # the image
    def captureMatchBackcam(self, picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"):
        template_path = "%s/BackCamera/" % self.template_path
        template_prefix = "bc_"

        dt = Date.Date()
        timestr = dt.getNowMyFormat(option="sec")

        # From now, this function captures the image.
        bcimg = "%s/bc_%s.png" % (picpath, timestr)
        self.getImage("back", bcimg, 2)
        print(("Image = %s" % bcimg))
        print((os.path.exists(bcimg)))

        # ROI should be wider than the template images
        roi = self.anaImage(bcimg, "back", bin_thresh=10)
        lpm = LargePlateMatching.LargePlateMatching(template_path, template_prefix)
        ok_file, ok_phi, max_sim = lpm.match(roi)
        # ok_file, ok_phi, max_sim = lpm.match(bcimg)
        cv2.imwrite("roi_target.png", roi)
        print((ok_file, ok_phi))
        if numpy.fabs(ok_phi) > 360:
            print("No thank you")
        else:
            print(("Rotating -%.1f deg." % ok_phi))
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

    def testCapture(self):
        starttime = datetime.datetime.now()
        # for phi in [0,45,90]:
        for phi in [0]:
            self.dev.gonio.rotatePhi(phi)
            self.getImage()

            prefix = "%f" % phi
            self.anaim(prefix)

        endtime = datetime.datetime.now()
        print(starttime, endtime)

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

    # By using side view camera, phi is tuned for large holder
    # Target image is side view camera
    def tune_phi(self, timg):

        # This is currently used in side view only
        target_img = cv2.imread(timg)
        back_img = cv2.imread(self.side_bg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(back_img, cv2.COLOR_BGR2GRAY)
        dimg = cv2.absdiff(gim, gbk)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (3, 3), 0)
        sgb = cv2.threshold(blur, 30, 150, 0)[1]
        cv2.imwrite("sgb.png", sgb)

        # Contours analysis
        contours, hierarchy = cv2.findContours(sgb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Draw contours on picture
        cv2.drawContours(gim, contours, -1, (0, 255, 0), 3)
        cv2.imwrite("cont.png", gim)

        # Contour: reduction of dimension
        cnt = self.squeeze_contours(contours)

        # ROI (x axis direction only)
        # To choose region betweeen cryo-nozzle and goniometer
        # Xrange can be set self.sc_xmin, self.sc_xmax
        roi_xy = self.contour_roi(cnt)
        under_edge = self.find_under_edge(roi_xy)
        # print "UNDER=",under_edge
        for un in under_edge:
            print("UNDER ", un[0], un[1])
        # ymean is used for tuning gonio pint direction
        angle, score, ymean = self.fitting_pix_line(under_edge)

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
        print("Thick mean = ", thick_mean, thick_std)
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

        return angle, final_score, ymean

    # 2018/11/09 Coded from 14_mount_fit_side.py
    def fit_side(self, puckid, pinid):
        # Rough facing 
        n_fail = 0
        while (1):
            max_similarity = self.captureMatchBackcam()
            if max_similarity > 0.80:
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

        ifail = 0
        while (1):
            self.getImage("side", target_image, binning=4)
            angle, score, ymean = self.tune_phi(target_image)
            diff_from_good_facing = self.face_phi - angle
            print(angle, score, ymean, diff_from_good_facing)
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

        # ycenter=self.pint_ymean
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

    def fit_pint_direction(self):
        # Align to pint direction
        ifail = 0
        target_image = "%s/sc.png" % self.img_path
        ycenter = 289
        pix_resol = 0.0319
        while (1):
            self.getImage("side", target_image, binning=4)
            angle, score, ymean = self.tune_phi(target_image)

            if score > 100.0:
                self.dev.gonio.rotatePhiRelative(180.0)
                ifail += 1

            print("LOG=", ymean)
            diff_y = ymean - ycenter
            move_um = diff_y / pix_resol

            print("Dpix(y)=", diff_y)
            print("Dpint[um]=", move_um)

            if numpy.fabs(move_um) < 3.0:
                break

            elif numpy.fabs(move_um) < 1000.0:
                self.dev.gonio.movePint(move_um)
                ifail += 1

            if ifail > 5:
                self.dev.gonio.rotatePhiRelative(180.0)

    def align_rotation(self, puckid, pinid):
        # pin path
        pp = "%s-%02d" % (puckid, pinid)
        pin_path = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/%s/" % pp
        if os.path.exists(pin_path) == False:
            os.makedirs(pin_path)

        dev.prepCenteringSideCamera()
        back_image = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"

        # current phi 
        save_phi = dev.gonio.getPhi()
        dev.prepCenteringSideCamera()

        ofile = open("%s/log.dat" % pin_path, "w")
        ofile.write("# delphi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle\n")
        # Side camera background
        min_thick = 9999.9999
        l_angle_set = 0.0
        diff_angle_set = 0.0
        for delphi in range(-10, 12, 2):
            curr_phi = save_phi + delphi
            dev.gonio.rotatePhi(curr_phi)
            prefix = "rot%04d" % curr_phi
            imagefile = "%s/%s_%03d.png" % (pin_path, prefix, curr_phi)
            inocc.getImage("side", imagefile, binning=4)
            l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std = \
                inocc.analyzePreciseSideCamera(imagefile, back_image, prefix=prefix, proc_dir=pin_path)

            if min_thick > thick_mean and l_score < 10.0:
                min_thick = thick_mean
                l_angle_set = l_angle
                # Angle based on horizontal axis of the coax image
                # Absolute phi angle for facing is ....
                diff_angle_set = 2.8 - l_angle_set
                abs_target_phi = curr_phi + diff_angle_set
                print("Lower angle = %s D(angle) = %s Final = %s" % (l_angle_set, diff_angle_set, abs_target_phi))

            diff_lu_angle = l_angle - u_angle

            ofile.write("%5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f \n" % (
                curr_phi, l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std, diff_lu_angle))

        dev.gonio.rotatePhi(abs_target_phi)
        imagefile = "%s/%s_%s_final.png" % (pin_path, prefix, abs_target_phi)
        inocc.getImage("side", imagefile, binning=4)

    # 2018/11/09
    # Copy from 19_recover_tateyoko.py
    def fit_tateyoko(self):
        # Basic information
        # ROI center for ideal position 
        # x0=251
        # y0=275
        # 2019/2/11 version
        x0 = 254
        y0 = 274

        trans_resol = 0.006727
        vert_resol = 0.0092727

        lpmbc = LargePlateMatchingBC.LargePlateMatchingBC()

        # preparation
        self.dev.prepCenteringBackCamera()

        for i in range(0, 10):
            imgname = "%s/bctest.png" % (self.img_path)
            self.getImage("back", imgname, binning=2)
            max_loc = lpmbc.getHoriVer(imgname)
            x, y = max_loc

            # diff
            diffx = x - x0
            diffy = y - y0

            # movement
            trans_um = diffx / trans_resol
            vert_um = diffy / vert_resol

            print("TRANS=", diffx, trans_um)
            print("VERT =", diffy, vert_um)

            if numpy.fabs(trans_um) < 25.0 and numpy.fabs(vert_um) < 25.0:
                break

            if numpy.fabs(trans_um) < 2000.0:
                self.dev.gonio.moveTrans(trans_um)
            if numpy.fabs(vert_um) < 2000.0:
                self.dev.gonio.moveUpDown(vert_um)

    def analyzePreciseSideCamera(self, target, back, prefix="checking", proc_dir="./"):
        target_img = cv2.imread(target)
        back_img = cv2.imread(back)

        data_file = "%s/%s.dat" % (proc_dir, prefix)
        dfile = open(data_file, "w")

        tg = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        bg = cv2.cvtColor(back_img, cv2.COLOR_BGR2GRAY)
        dimg = cv2.absdiff(tg, bg)
        cv2.imwrite("%s/diff.png" % proc_dir, dimg)

        # This value for filtering was not so different (20 - 50)
        param = 20
        baseimg = cv2.imread(target)
        blur = cv2.bilateralFilter(dimg, 15, param, param)
        cv2.imwrite("%s/blur%02d.png" % (proc_dir, param), blur)
        result1 = cv2.threshold(blur, 10, 150, 0)[1]
        cv2.imwrite("%s/bin%02d.png" % (proc_dir, param), result1)
        # Contour finding
        cont1, hi1 = cv2.findContours(result1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = self.squeeze_contours(cont1)
        cv2.drawContours(baseimg, cont1, -1, (0, 255, 0), 3)
        roi_xy = self.contour_roi(cnt)
        lower_edge = self.find_lower_edge(roi_xy)
        upper_edge = self.find_upper_edge(roi_xy)
        l_angle, l_score, l_meany = self.fitting_pix_line(lower_edge)
        u_angle, u_score, u_meany = self.fitting_pix_line(upper_edge)
        # print param,angle,"score=",score,"meany=",meany

        for lower in lower_edge:
            lx, ly = lower
            dfile.write("lower: %3d %3d\n" % (lx, ly))
        for upper in upper_edge:
            ux, uy = upper
            dfile.write("upper: %3d %3d\n" % (ux, uy))

        l_text = "Lower angle = %5.1f score = %5.1f meany = %5.1f" % (l_angle, l_score, l_meany)
        u_text = "Upper angle = %5.1f score = %5.1f meany = %5.1f" % (u_angle, u_score, u_meany)
        cv2.putText(baseimg, l_text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), thickness=1)
        cv2.putText(baseimg, u_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), thickness=1)

        line_start_x = self.sc_xmin
        line_end_x = self.sc_xmax
        l_line_start_y = int(l_meany)
        u_line_start_y = int(u_meany)
        xlen = self.sc_xmax - self.sc_xmin

        l_diff_y = int(xlen * numpy.tan(numpy.radians(l_angle)))
        u_diff_y = int(xlen * numpy.tan(numpy.radians(u_angle)))

        print(l_diff_y, u_diff_y)

        thick_mean, thick_std = self.analyzeWidth(lower_edge, upper_edge)

        thick_text = "Thickness mean = %5.1f Thickness std = %5.3f" % (thick_mean, thick_std)
        # cv2.putText(baseimg, thick_text, (20,450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), thickness=1)
        cv2.putText(baseimg, thick_text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (0, 0, 255), 2)

        cv2.line(baseimg, (self.sc_xmin, l_line_start_y), (self.sc_xmax, l_line_start_y + l_diff_y), (0, 0, 255), 3)
        cv2.line(baseimg, (self.sc_xmin, u_line_start_y), (self.sc_xmax, u_line_start_y + u_diff_y), (0, 0, 255), 3)
        cv2.imwrite("%s/%s_ana.png" % (proc_dir, prefix), baseimg)

        # Checking the value
        return l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std


if __name__ == "__main__":
    import Device

    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc, b_blanc))

    dev = Device.Device(s)
    dev.init()

    file1 = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/cam1_test.png"
    # def getImage(self,view,filename,binning=2):

    bs = BS.BS(s)
    inocc = IboINOCC(dev)
    dev.prepCenteringLargeHolderCam1()

    ### 210607 AOMUSHI week
    apath=os.path.abspath("./TemplateImages/")
    # path="path./TemplateImages/"
    # prefix="holder01"
    # inocc.makeBackcamTemplate()

    ### 210607 15:53 K.Hirata
    # test captureBackcamMatching()
    inocc.captureMatchBackcam(picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/")


    """

    ######
    ### back ground images
    ######
    backpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"
    # All of background images
    # inocc.getBackImages()
    # Back camera
    # inocc.getImage("back","%s/bc_back_bin2.png"%backpath,binning=2)
    # inocc.getImage("back","%s/bc_back_bin1.png"%backpath,binning=2)
    # inocc.anaBack("bc.png")
    # Side camera
    # inocc.getImage("side","%s/side.png"%backpath,binning=4)
    # inocc.getImage("side","%s/sc_back_bin2.png"%backpath,binning=2)
    # inocc.anaSide("sc.png")

    # Naname camera
    # inocc.getImage("naname","%s/naname.png"%backpath)
    # inocc.getImage("side","%s/sc_back_bin2.png"%backpath,binning=2)
    # inocc.anaSide("sc.png")

    # inocc.getImage("side","%s/side_bin4.png"%backpath,binning=4)
    # inocc.getImage("side","%s/side_bin2.png"%backpath,binning=2)
    # inocc.getImage("back","%s/back_bin2.png"%backpath,binning=2)
    # inocc.getImage("back","%s/back_bin1.png"%backpath,binning=1)
    # inocc.getImage("naname","%s/naname.png"%backpath)

    # Naname camera template files
    # inocc.makeNanamecamTemplate()
    # inocc.makeSidecamTemplate()
    # inocc.getImage("side","%s/side_bin4.png"%backpath,binning=4)
    # inocc.getImage("side","%s/side_bin2.png"%backpath,binning=2)

    # inocc.getImage("side","%s/side_bin4_bg.png"%backpath,binning=4)
    # inocc.getImage("side","%s/side_bin2_bg.png"%backpath,binning=2)

    # timg="%s/side_bin4.png"%backpath
    # bimg="%s/side_bin4_bg.png"%backpath
    # inocc.simpleAna(timg,bimg)

    # timg="%s/side_bin2.png"%backpath
    # bimg="%s/side_bin2_bg.png"%backpath
    # inocc.simpleAna(timg,bimg)

    # Naname camera recoveing to face angle
    # while(1):
    # max_similarity=inocc.captureNanamecamMatching()
    # if max_similarity > 0.80:
    # break

    # 2018/07/23
    # inocc.captureTestData()
    # inocc.captureTestAnalysis()

    # Capture & Template matching
    # inocc.captureTestMatching()
    # inocc.makeBackcamTemplate()
    # inocc.captureBackcamMatching()

    dev.prepCenteringLargeHolderCam2()
    # inocc.makeBackcamTemplateBin1()
    inocc.captureBackcamMatchingBin1()

    phi=120.0
	ylen_max=inocc.anaROI2(phi)
	print "(PHI,YLEN)=",phi,ylen_max
	if ylen_max < 30.0:
		phi=phi+90.0
		print phi
	elif ylen_max < 60.0:
		phi=phi+50.0
		print phi
	elif ylen_max < 70.0:
		phi=phi+30.0
		print phi
	elif ylen_max < 80.0:
		phi=phi+10.0
		print phi
	gonio.rotatePhi(phi)

	#path="./TemplateImages"
	#prefix="holder01"
	#inocc.makeTemplateFiles(path,prefix)
	bs.on()
	inocc.getCam2Image("./test.png")

	for phi in range(0,360,10):
		file1="cam1_%s.png"%phi
		file2="cam2_%s.png"%phi
		gonio.rotatePhi(phi)
		inocc.getImage(file1)
		inocc.getCam2Image(file2)
	
	for ntime in range(1,10):
		trans=100.0*ntime
		gonio.moveTrans(100.0)
		file1="cam2_trans_%fum.png"%trans
		inocc.getCam2Image(file1)
        #inocc.analyseGonioTranslation()

	# From contour of opencv2: find right edge position
	# not good for contour analysis
	#hori,vert=inocc.findRightPosition()
	#inocc.anaGonioUpDown()

	#print hori,vert
	#h_diff=hori-101
	#v_diff=vert-79
	
	# XMAX,Y_XMAX 101 79
	#h_move=h_diff/-0.003684/2.0
	#v_move=v_diff/-0.006406/2.0

	#print h_move,v_move

        #gonio.moveTrans(-h_move/2.0)
        #gonio.moveUpDown(-v_move/2.0)
	#gonio.translate
	#inocc.analyseGonioTranslation()
	#inocc.anaGonioY()

	starttime=datetime.datetime.now()
	# Recover Face angle
	bs.evacLargeHolder()
	inocc.recoverFaceAngle()

	# Precise facing
	inocc.rotateToFace()

	# 2D alignment 
	inocc.moveToOtehon()

	#inocc.translateToCenter()
        #inocc.translateToCenterROI()
	endtime=datetime.datetime.now()
	microsec= (endtime-starttime).microseconds
	print microsec/1000.0

	#phi=120.0
	#inocc.kukei(phi)
	#print starttime,endtime
	#inocc.testCapture()
	#for phi in range(0,360,20):
		#print "---PHI--- ",phi
		#inocc.kukei(phi)
		#ylen_max=inocc.anaROI2(phi)
    #inocc.rinkaku("rinkaku")
    """
