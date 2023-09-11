# encoding: utf-8
import cv2,sys
import numpy as np
import copy
from MyException import *
import logging
import logging.config
import File, os
from configparser import ConfigParser, ExtendedInterpolation

class CryImageProc():
    def __init__(self, logdir = "./"):
        self.debug = False
        # ROI definition 
        # これらの変数は重要ではあるが、各ビームラインごとに画像の画素数などが異なるため
        # ここでは適当な値を入れておく
        self.xmin = 10
        self.xmax = 600
        self.ymin = 10
        self.ymax = 480

        # beamlineのなまえ、gonio_direction, pix_size, bin_threshについては beamline.ini から読み込む
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(os.environ['ZOOCONFIGPATH']+"/beamline.ini")
        self.beamline = self.config.get("beamline", "beamline")

        # 最初に上下左右の一定ピクセルを解析から除外する→beamline.iniから読む
        # section: inocc, option: delete_pix
        self.delete_pix = self.config.getint("inocc", "delete_pix")

        # Pixel size (section: coaximage, option: pix_size)
        self.pix_size = self.config.getfloat("coaximage", "pix_size")
        # gonio direction (section: experiment, option: gonio_direction)
        self.gonio_direction = self.config.get("experiment", "gonio_direction")
        # bin threshold for detecting the edge (section: inocc, option: bin_thresh)
        self.bin_thresh = self.config.getint("inocc", "bin_thresh")
        # filter threshold for detecting the edge (section: inocc, option: filter_thresh_min)
        # filter threshold for detecting the edge (section: inocc, option: filter_thresh_max)
        self.filter_thresh_min = self.config.getint("inocc", "filter_thresh_min")
        self.filter_thresh_max = self.config.getint("inocc", "filter_thresh_max")

        # ROI length [um]
        # 上下左右の方向からこの距離オフセットした中央のROIを設定するためのパラメータ
        # 通常は200umくらいだが beamline.iniから読むことにする
        # section: inocc, option: roi_len_um
        self.roi_len_um = self.config.getfloat("inocc", "roi_len_um")
        # Edge margin to judge 'Hamidashi'
        self.edge_margin_pix = int(self.roi_len_um / self.pix_size)
        self.roi_len_pix = self.roi_len_um / self.pix_size
        
        # Flags 
        self.isContourFull = False
        self.isContourROI  = False
        self.isTopXY = True

        # Log picture
        self.roi_pic = "roi.png"

        # Logging directory
        self.logdir = logdir

        # File treatment
        self.fileclass = File.File(self.logdir)

        # My logfile
        self.logger = logging.getLogger('ZOO').getChild("CryImageProc")

        # Gamma correction (2021/01/21 coded by K.Hirata)
        # Gamma correction was switched off on 2021/03/26 -> Magnification ratio is set to smaller value
        self.isGamma=False

        # New method without background image
        self.isUseNew=False

    def setROIpic(self, roi_pic):
        self.roi_pic = roi_pic

    def setDebugFlag(self, flag):
        self.debug = flag

    # 長さを指定して、ROIのピクセル数を計算している
    def calcPixLen(self, length):
        # loop size は、ROIの横幅の長さ
        self.roi_len_um = length
        self.roi_len_pix = self.roi_len_um / self.pix_size
        return int(self.roi_len_pix)

    def setBinThresh(self, binthresh):
        self.bin_thresh = binthresh

    def printImage(self, image):
        im_height = image.shape[0]
        im_width = image.shape[1]
        #print "Height, Width=", im_height, im_width
        for i in range(0, im_height):
            for j in range(0, im_width):
                print(i,j,image[i,j])
            print("\n")

    # Coax CCD camera sometimes include 'noise at edges'
    def trimEdges(self, cvimage, ntrim):
        tmpimg = copy.deepcopy(cvimage)
        # trim range
        # Top of the image
        for height in range(0, ntrim):
            tmpimg[height,] = 0
        # Bottom of the image
        down_edge = tmpimg.shape[0]
        del_start = down_edge - ntrim
        for height in range(del_start, down_edge):
            tmpimg[height,] = 0
        # right of the image
        im_width = tmpimg.shape[1]
        right_start = im_width - ntrim
        right_end = im_width
        for vert_pixels in range(right_start, right_end):
            tmpimg[:, vert_pixels] = 0

        # Left of the image
        left_start = 0
        left_end = ntrim
        for vert_pixels in range(left_start, left_end):
            tmpimg[:, vert_pixels] = 0

        return tmpimg

    def setImages(self, target_file, back_file):
        self.target_file = target_file
        self.back_file = back_file
        self.timg = cv2.imread(target_file)
        self.bimg = cv2.imread(back_file)
        self.logger.info("CIP.setImages: T: %s, B: %s"% (target_file, back_file))
        self.tgrey = cv2.cvtColor(self.timg, cv2.COLOR_BGR2GRAY)
        self.bgrey = cv2.cvtColor(self.bimg, cv2.COLOR_BGR2GRAY)
        self.tgrey = self.trimEdges(self.tgrey, ntrim=7)
        self.bgrey = self.trimEdges(self.bgrey, ntrim=7)

        # For binarization
        if self.isGamma:
            self.dimg = self.gammaCorrAndDiff(self.tgrey, self.bgrey)
            # Median Blur
            self.blur = cv2.bilateralFilter(self.dimg,self.filter_thresh_min,self.filter_thresh_max,self.filter_thresh_max)
            self.bin_image = cv2.threshold(self.blur, self.bin_thresh, 150, 0)[1]

        elif self.isUseNew:
            self.dimg = self.tgrey
            self.blur = cv2.medianBlur(self.tgrey, 5)
            self.bin_image = cv2.adaptiveThreshold(self.blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, self.filter_thresh_min, 3)
            cv2.imwrite("bin.png", self.bin_image)

        else:
            self.dimg=cv2.absdiff(self.tgrey,self.bgrey)
            self.blur = cv2.bilateralFilter(self.dimg,self.filter_thresh_min,self.filter_thresh_max,self.filter_thresh_max)
            # binirization1
            self.bin_image = cv2.threshold(self.blur, self.bin_thresh, 150, 0)[1]

        self.im_width = self.dimg.shape[0]
        self.im_height = self.dimg.shape[1]

        self.im_width_um = float(self.im_width) * self.pix_size
        self.im_height_um = float(self.im_height) * self.pix_size

        # target image on the memory for debug image
        self.target_save = copy.deepcopy(self.timg)

        # min - max in XY directions
        self.xmin = self.delete_pix 
        self.xmax = self.im_width - self.delete_pix 
        self.ymin = self.delete_pix 
        self.ymax = self.im_height - self.delete_pix 

        #print(self.im_width, self.im_height)

        # Top centering edge
        self.xmin_top = self.edge_margin_pix
        self.xmax_top = self.im_width - self.edge_margin_pix
        self.ymin_top = self.edge_margin_pix
        self.ymax_top = self.im_height - self.edge_margin_pix

        #print(self.xmin_top, self.xmax_top, self.ymin_top, self.ymax_top)

        # Log file for centering
        self.logfile = open("%s/cip.log" % self.logdir, "a")
        self.logfile.write("Processing %s back = %s \n" % (target_file, back_file))

    # Low pass fileter using FFT
    def lowpass_filter(self, src, a=0.5):
        src = np.fft.fft2(src)
        h, w = src.shape
        cy, cx = int(h / 2), int(w / 2)
        rh, rw = int(a * cy), int(a * cx)
        fsrc = np.fft.fftshift(src)
        fdst = np.zeros(src.shape, dtype=complex)
        fdst[cy - rh:cy + rh, cx - rw:cx + rw] = fsrc[cy - rh:cy + rh, cx - rw:cx + rw]
        fdst = np.fft.fftshift(fdst)
        dst = np.fft.ifft2(fdst)
        return np.uint8(dst.real)

    def create_gamma_img(self, gamma, img):
        gamma_cvt = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            gamma_cvt[i][0] = 255 * (float(i) / 255) ** (1.0 / gamma)
        return cv2.LUT(img, gamma_cvt)

    def gammaCorrAndDiff(self, target_img, back_img):
        # Gamma coefficient
        gamma=1.1

        gtarget = self.create_gamma_img(gamma, target_img)
        ghikufile = self.create_gamma_img(gamma, back_img)

        dimg = cv2.absdiff(gtarget, ghikufile)

        """
        th3 = cv2.threshold(blurimg, 9, 255, 0)[1]

        contours, hierarchy = cv2.findContours(th3, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        print(len(cv2.findContours(th3, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)))

        cv2.drawContours(img, contours, -1, (0, 0, 255), 1)
        cv2.imwrite("result.png", img)

        th4 = lowpass_filter(th3, 4)
        """
        return (dimg)


    # 190514 coded by K.Hirata
    # ratio = 1.0 -> Full length of image width
    def getHoriDistOAVmmToGoniometer(self, ratio = 1.0):
        oav_hori_mm = self.im_width_um/1000.0 * ratio #[mm]
        oav_hori_mm_directed = -1.0 * self.calcYdistAgainstGoniometer(oav_hori_mm)

        #print "MMMMMMMM= ", oav_hori_mm_directed
        
        return oav_hori_mm_directed

    def getImageHeight(self):
        return self.im_height_um

    # This routine squeeze contours 
    # Reduce the dimensions
    def squeeze_contours(self, contours):
        new_array=[]
        # contours structure
        # found contours are included in 'contours'
        # This loop is a treatment for each 'found contour'.
        self.logfile.write("Number of found contours. Len = %5d\n" % len(contours))
        if len(contours)!=1:
            max_len = -9999
            self.logfile.write("A contour is being chosen from %5d contours\n" % len(contours))
            for i, cnt in enumerate(contours):
                if self.debug == True:
                    arclen = cv2.arcLength(cnt, True)
                    self.logfile.write("ARCLENGTH= %8d\n" % arclen)
                tmplen = len(cnt)
                if tmplen > max_len:
                    max_len = tmplen
                    target_contour = cnt
        else:
            target_contour = contours[0]
    
        # Delete non-required dimension
        single_contour = np.squeeze(target_contour)
        ndim_contour = single_contour.ndim
        self.logfile.write("Acquired contour dimensions = %5d\n" % ndim_contour)

        return single_contour

    def drawContourOnTarget(self, contour, outimage):
        baseimg = copy.deepcopy(self.timg)

        for x,y in contour:
            cv2.circle(baseimg,(x,y),2,(0,0,255),1)
        cv2.imwrite(outimage, baseimg)

    def drawTopOnTarget(self, top_xy, outimage):
        baseimg = copy.deepcopy(self.timg)
        #baseimg = cv2.imread(self.target_file)
        x,y = top_xy
        cv2.circle(baseimg,(x,y),2,(0,0,255),3)
        cv2.imwrite(outimage, baseimg)

    def drawContourTop(self, contour, top_xy, outimage):
        print("drawContourTop")
        #baseimg = cv2.imread(self.target_file)
        baseimg = copy.deepcopy(self.timg)

        for x,y in contour:
            cv2.circle(baseimg,(x,y),1,(0,0,255),1)

        topx, topy = top_xy
        #print topx, topy
        cv2.circle(baseimg,(topx,topy),3,(255,0,0),3)
        cv2.imwrite(outimage, baseimg)
        print("drawContourTop")

    def drawRasterSquare(self, xmin, xmax, ymin, ymax, xcen, ycen, outimage):
        #baseimg = cv2.imread(self.target_file)
        baseimg = copy.deepcopy(self.timg)

        #print xmin, xmax, ymin, ymax
        corner1 = (int(xmin), int(ymin))
        corner2 = (int(xmax), int(ymax))
        cv2.rectangle(baseimg, corner1, corner2, (255,0,0),3)
        cv2.circle(baseimg, (xcen, ycen), 1, (255,255,0),3)
        cv2.imwrite(outimage, baseimg)

    # 190514 coded by K.Hirata
    # New function for INOCC
    def getROIcontour(self, loop_size):
        # loop size は、ROIの横幅の長さ
        self.roi_pix_len = self.calcPixLen(loop_size)
        self.full_contour = self.getContour()
        self.isContourFull = True
        # No contour was found
        if len(self.full_contour) == 0:
            raise MyException("CIP.getCenterInfo could not find any contours.")
        # Loop top coordinate
        self.top_xy = self.find_top_x(self.full_contour)
        self.isTopXY = True
        # ROI for centering
        self.roi_cont = self.selectHoriROI(self.full_contour, self.top_xy, self.roi_pix_len)
        self.isContourROI = True
        
        # ROI log picture
        self.drawContourOnTarget(self.roi_cont, self.roi_pic)

        return self.roi_cont

    def getMinArea(self, loop_size = 400.0, filepath = "min.png"):
        baseimg = copy.deepcopy(self.timg)

        if self.isContourROI == False:
            self.roi_cont = self.getROIcontour(loop_size)
        rect = cv2.minAreaRect(self.roi_cont)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        baseimg = cv2.drawContours(baseimg,[box],0,(0,0,255),2)
        cv2.imwrite(filepath, baseimg)
        return box

    # CV2 area function
    def getAreaCV2(self, loop_size = 400.0):
        if self.isContourROI == False:
            self.roi_cont = self.getROIcontour(loop_size)
        area = cv2.contourArea(self.roi_cont)
        return area

    # My area function
    def getArea(self, loop_size = 400.0):
        if self.isContourROI == False:
            self.roi_cont = self.getROIcontour(loop_size)
        self.logfile.write("top_xy = %s\n" % self.top_xy)
        self.logfile.write("ROI Min/Max = %5d/%5d\n"% (self.roi_xmin, self.roi_xmax))
        #print "MIN:MAX", self.roi_xmin, self.roi_xmax

        # Sort along 'x'
        roi_xy_sorted = sorted(self.roi_cont, key=lambda x: x[0],reverse=False)

        # Loop2
        ymin_flag = False
        ymax_flag = False
        area = 0
        ymax = 0
        ymin = 99999
        for xwork in range(self.roi_xmin, self.roi_xmax+1):
            for x,y in roi_xy_sorted:
                if x > xwork:
                    break
                if xwork == x:
                    if y >= ymax:
                        ymax_flag = True
                        ymax = y
                    if y <= ymin:
                        ymin_flag = True
                        ymin = y
            area += ymax - ymin
        return area

    # 190514 coded by K.Hirata
    # New function directly called from INOCC 
    # option: 'gravity' or 'top'
    def getCenterInfo(self, loop_size=600.0, option = "gravity"):
        roi_pix_len = self.calcPixLen(loop_size)
        try:
            if self.isContourROI == False:
                self.roi_cont = self.getROIcontour(loop_size)
        except MyException as ttt:
            raise MyException(ttt)

        # Area of the ROI contour
        area = cv2.contourArea(self.roi_cont)
        self.logger.info("area of ROI: %8.3f" % area)

        # Check if the loop is out of scene.
        if option == "top":
            topx, topy = self.top_xy
            if topx <= self.xmin_top or topy <= self.ymin_top:
                hamidashi_flag = True
            elif topx >= self.xmax_top or topy >= self.ymax_top:
                hamidashi_flag = True
            else:
                hamidashi_flag = False
            return topx, topy, area, hamidashi_flag

        # Option = "gravity center of the point distant from 'loop_size' from the loop top
        # Find centering point
        try:
            target_x, target_y = self.findCenteringPoint(self.roi_cont, self.roi_pix_len, self.top_xy)
        except MyException as ttt:
            raise MyException("CIP.getCenterInfo could not find any centering target.")

        # Hamidashi flag
        top_x = self.top_xy[0]
        hamidashi_flag = False

        # All direction hamidashi
        left_flag, right_flag, lower_flag, upper_flag, n_true = self.isTouchedToEdge(self.roi_cont)
        if n_true >= 2:
            hamidashi_flag = True
        else:
            hamidashi_flag = False

        return target_x, target_y, area, hamidashi_flag

    # The previous code was not suitable to cover all range of the loop.
    # This was coded to fix the problem on 2019/06/12
    # Homework: this function is very similar to 'getRasterArea'.
    # Also, both function should give same results for centering. -> should be merged together?
    def findCenteringPoint(self, roi_xy, roi_pix_len, top_xy):
        baseimg = copy.deepcopy(self.timg)
        x, y, w, h = cv2.boundingRect(roi_xy)
        roi_xmin = x
        roi_xmax = x + w
        roi_ymin = y
        roi_ymax = y + h
        roi_cenx = int((roi_xmin + roi_xmax) / 2.0)
        roi_ceny = int((roi_ymin + roi_ymax) / 2.0)

        if self.debug == True:
            baseimg = copy.deepcopy(self.timg)
            cv2.circle(baseimg, (roi_cenx, roi_ymin), 1, (255, 255, 0), 3)
            cv2.circle(baseimg, (roi_cenx, roi_ymax), 1, (255, 255, 0), 3)
            cv2.circle(baseimg, (roi_cenx, roi_ceny), 1, (255, 255, 0), 3)
            cv2.imwrite("find_center.png", baseimg)

        return (roi_cenx, roi_ceny)

    def getRasterArea(self, contour, rasterPic = "rasterArea.png"):
        baseimg = copy.deepcopy(self.timg)
        x, y, w, h = cv2.boundingRect(contour)
        roi_xmin = x
        roi_xmax = x + w
        roi_ymin = y
        roi_ymax = y + h
        roi_cenx = int((roi_xmin + roi_xmax) / 2.0)
        roi_ceny = int((roi_ymin + roi_ymax) / 2.0)

        # ROI length
        hori_um = w * self.pix_size
        vert_um = h * self.pix_size

        # Writing raster square image
        log2 = "ROI square(H, V) = (%5.2f, %5.2f)[um]"%(hori_um, vert_um)

        cv2.rectangle(baseimg, (roi_xmin, roi_ymin), (roi_xmax, roi_ymax), (127, 255, 0), 2)
        cv2.circle(baseimg, (roi_cenx, roi_ceny),2, (255, 0, 0), 2)
        cv2.putText(baseimg, log2, (10, 450), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0, 0, 0), lineType=cv2.LINE_AA)
        cv2.imwrite(rasterPic, baseimg)

        return roi_xmin, roi_xmax, roi_ymin, roi_ymax, roi_cenx, roi_ceny

    def calcYdistAgainstGoniometer(self, ymm):
        if self.gonio_direction == "FROM_RIGHT":
            return -1.0 * ymm
        else:
            return ymm

    # 2021/01/21 Gamma correction and contour\
    def getContour(self):
        baseimg = cv2.imread(self.target_file)
        # debugging file
        cv2.imwrite("%s/blur.png"%self.logdir, self.blur)
        # debugging file
        bin_name = os.path.join(self.logdir, "bin.png")
        cv2.imwrite(bin_name, self.bin_image)

        # Contour finding
        cont1, hi1 = cv2.findContours(self.bin_image,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(cont1) == 0:
            self.logfile.write("No contour was found in getContour()\n")
            return cont1

        if self.debug == True:
            self.logfile.write("the first element of 'cont1' = %s\n" % cont1[0])
            self.logfile.write("a shape of the element = %5d\n" % len(cont1))
            #print "a shape of the element = ", len(cont1)

        # This 'squeezing' makes a single contour of numpy.array(NPOINTS,2)
        cnt = self.squeeze_contours(cont1)

        if self.debug == True:
            print("Hierarchy:",hi1)
            print("Contour  :",cont1)
            print("Contour type, length=",type(cont1),len(cont1))
            #for c in cnt:
                #print c

        # debugging file
        cv2.drawContours(baseimg,cont1,-1,(0,255,0),3)
        cv2.imwrite("%s/cont.png" % self.logdir, baseimg)

        return cnt
    
    def ana_contours(contours):
        for contour in contours:
            if len(contour.shape) == 1:
                print(contour)
                continue
            else:
                ndata,dummy=contour.shape
                for i in range(0,ndata):
                    print(contour[i])

    def find_top_x(self, contours):
        # Gonio from right 
        if self.gonio_direction == "FROM_RIGHT":
            xmin = 9999
            ytop = 9999
            for contour in contours:
                if len(contour.shape) == 1:
                    x,y=contour
                    #print x
                    if xmin > x:
                        xmin = x
                        ytop = y
                else:
                    ndata,dummy=contour.shape
                    for i in range(0,ndata):
                        x,y=contour[i]
                        if xmin > x:
                            xmin = x
                            ytop = y
            return xmin,ytop
        # Gonio from Left
        else:
            xmax = 0
            for contour in contours:
                if len(contour.shape) == 1:
                    x,y=contour
                    if xmax <= x:
                        xmax = x
                        ytop = y
                else:
                    ndata,dummy=contour.shape
                    for i in range(0,ndata):
                        x,y=contour[i]
                        if xmax <= x:
                            xmax = x
                            ytop = y
            return xmax, ytop
    
    # This routine selects ROI in horizontal direction
    # len_from_top [pix]
    def selectHoriROI(self, contours, top_xy, len_pix):
        roi_xy=[]
        top_x, ytop = top_xy
        # gonio direction
        # "FROM_RIGHT" : BL32XU, BL41XU
        if self.gonio_direction == "FROM_RIGHT":
            xmin = top_x
            xmax = xmin + len_pix
        # "FROM_LEFT" : BL45XU
        else:
            xmax = top_x
            xmin = top_x - len_pix

        def isInRange(x):
            if x >= xmin and x <= xmax:
                return True
            else:
                return False
        for contour in contours:
            if len(contour.shape) == 1:
                x,y=contour
                if isInRange(x):
                    roi_xy.append((x,y))
                continue
            else:
                ndata,dummy=contour.shape
                for i in range(0,ndata):
                    x,y=contour[i]
                    if isInRange(x):
                        roi_xy.append((x,y))
        self.roi_xmin = xmin
        self.roi_xmax = xmax
        return np.array(roi_xy)

    # A squeezed single contour should be given.
    # contour : (N, 2) numpy array
    def isTouchedToEdge(self, contour):
        # edge region
        left_edge = self.xmin
        upper_edge = self.ymin
        lower_edge = self.ymax
        right_edge = self.xmin

        # Flags
        left_flag = False
        right_flag = False
        upper_flag = False
        lower_flag = False

        # Edge detection
        n_true = 0
        for x,y in contour:
            if x < left_edge:
                left_flag = True
            if x > right_edge:
                right_flag = True
            if y > lower_edge:
                lower_flag = True
            if y < upper_edge:
                upper_flag = True

        if left_flag == True: n_true += 1
        if right_flag == True: n_true += 1
        if lower_flag == True: n_true += 1
        if upper_flag == True: n_true += 1

        self.logger.info("Touched: L:%s R:%s LOWER:%s UPPER:%s"% (left_flag, right_flag, lower_flag, upper_flag))

        return left_flag, right_flag, lower_flag, upper_flag, n_true

    def checkExistence(self, contour):
        left_flag, right_flag, lower_flag, upper_flag = self.isTouchedToEdge(contour)
        if (left_flag == False and right_flag == False and 
                lower_flag == False and upper_flag == False):
            print("No loop was detected.")
            return False
        return True

    def find_lower_edge(roi_xy):
        lower_edge=[]
        # Loop 1
        for xscan in range(self.xmin,self.xmax):
            ymax=0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    if y > ymax:
                        ymax=y
                        xsave=x
                        ysave=y
                    else:
                        continue
                else:
                    continue
            #print "CONTOUR=",xsave,ysave
            lower_edge.append((xsave,ysave))
    
        return lower_edge

    def getXrangeFromROI(self, roi_xy):
        xmin = 9999
        xmax = 0
        for x,y in roi_xy:
            if x >= xmax:
                xmax = x
            if x <= xmin:
                xmin = x
        return xmin, xmax

    # New function inspired from find_middle_line
    # coded on 2019/04/30 (Last coding in Heisei)
    def findMiddleLine(self, roi_xy):
        middle_line=[]
        xmin, xmax = self.getXrangeFromROI(roi_xy)
        for xscan in range(xmin, xmax+1):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    #print "xscan,y=",xscan,y
                    if y >= ymax:
                        ymax = y
                    if y <= ymin:
                        ymin = y
            # Middle point of ymin, ymax
            ymean = int((ymin + ymax)/2.0)
            middle_line.append((xscan,ymean))
    
        return middle_line

    # this finds a neck of the targeted loop
    def findLoopNeck(self, roi_xy):
        width_x_ywidth=[]
        xmin, xmax = self.getXrangeFromROI(roi_xy)
        for xscan in range(xmin, xmax+1):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    #print "xscan,y=",xscan,y
                    if y >= ymax:
                        ymax = y
                    if y <= ymin:
                        ymin = y
            # width of Y direction
            ywidth = int(np.fabs(ymin - ymax))
            width_x_ywidth.append((xscan,ywidth))

        ywa = np.array(width_x_ywidth)
        #ywa = sorted(ywa, key=lambda x: x[1],reverse=False)

        for x,y in ywa:
            print("DEDED:",x,y)
    
        return width_x_ywidth
    
    # This is old version
    # ROI is set in the 'initizalization' of this class
    # This means that the ROI is very wide and not suitable
    # for finding middle line
    # This code should be removed if this is not required
    def find_middle_line(self, roi_xy):
        middle_line=[]
        # scanning along 'horizontal axis' of ROI
        # 'roi_xy' includes contour of the target
        # at the same value of 'x'(horizontal pixel) 
        # there might be 2 or more 'y' values
        # this function calculates 'middle line' of
        # ymin and ymax in ROI x region.
        for xscan in range(self.xmin, self.xmax):
            # No meaning values for searching ymin & ymax
            ymin = 1000
            ymax = 0
            xsave=ysave=0
            # Loop2
            for x,y in roi_xy:
                if xscan==x:
                    if y > ymax:
                        ymax = y
                    elif y <= ymin:
                        ymin = y
                    else:
                        continue
                else:
                    continue
            # Middle point of ymin, ymax
            ymean = int((ymin + ymax)/2.0)
            middle_line.append((xscan,ymean))
    
        return middle_line
    
    def find_upper_edge(roi_xy):
        upper_edge=[]
        for xscan in range(self.xmin,self.xmax):
            ymin=999
            xsave=ysave=0
            for x,y in roi_xy:
                if xscan==x:
                    if y < ymin:
                        ymin=y
                        xsave=x
                        ysave=y
                    else:
                        continue
                else:
                    continue
            #print "CONTOUR=",xsave,ysave
            upper_edge.append((xsave,ysave))
    
        return upper_edge
    
    # Fitting 1D for X,Y of lower-edge of the loop
    # from side view camera
    def fitting_pix_line(self, xy_array):
        # Making X,Y numpy array
        xlist=[]
        ylist=[]
        for x,y in xy_array:
            #print "OBS=,",x,y
            xlist.append(x)
            ylist.append(y)
        
        xa=np.array(xlist)
        ya=np.array(ylist)
    
        # Linear arregression
        a,b=np.polyfit(xa,ya,1)
        ab = a,b
        print("A,B = ",ab)
        
        # scoring the fitting
        score=0.0
        
        # Print log
        fitted_array = []
        for x,y in zip(xa,ya):
            fitted_y = int(a*x+b)
            residual=(a*x+b)-y
            score+=residual*residual
            fitted_array.append((x, fitted_y))
    
        final_score=score/float(len(xa))
    
        meany = ya.mean()
        angle=np.degrees(np.arctan(a))
        
        return fitted_array,angle,final_score,meany
    
    def analyzeWidth(lower_contour, upper_contour):
        dy_list = []
        for each_lc in lower_contour:
            lx,ly = each_lc
            for each_uc in upper_contour:
                ux,uy = each_uc
                if ux == lx:
                    dy = uy - ly
                    dy_list.append(dy)
                    continue
    
        dya = np.array(dy_list)
        thick_mean = dya.mean()
        thick_std = dya.std()
        print("Thick mean = ",thick_mean,thick_std)
        return thick_mean, thick_std
    
    def printROI(self, roi_xy):
        for x,y in roi_xy:
            print(x,y)

    # Evaluate dekoboko of the line
    def calculateGradient(self, xy_data):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)
    
        xna = np.array(xa)
        yna = np.array(ya)
        dy = np.gradient(yna)
        
        x_dy_array = []
        for x,y,dy in zip(xna,yna,dy):
            print("GRAD:",x,y,dy)
            x_dy_array.append((x,dy))
    
        return x_dy_array

    def calcSmoothHenkyokuten(self, xy_data):
        #return x_ysmooth_grad_array, x_ysmooth_array

        # calculate a smoothen line of loop shape
        xy_smooth_grad, xy_smooth = self.calcSmoothGrad(xy_data)

        # calculate a smoothen nijibibun
        xy_smooth_grad2, xy_smooth2 = self.calcSmoothGrad(xy_smooth_grad)

        for i in range(0, len(xy_smooth_grad)):
            print(i)
            x = xy_smooth_grad[i][0]
            yg = xy_smooth_grad[i][1]
            ys = xy_smooth[i][1]
            yss = xy_smooth2[i][1]
            ygg = xy_smooth_grad2[i][1]
            print("SSSS:",x,ys,yg,yss,ygg)

    def calcSmoothLine(self, xy_data, nsmooth = 15):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)

        v = np.ones(nsmooth)/5.0 # 'nsmooth' averages
        y2a = np.convolve(ya, v, mode='same')

        for x,y in zip(xa, y2a):
            print("SMOOTH:",x,y)

    #def calcYdistAgainstGoniometer

    # smoothing and calculate gradients
    def calcSmoothGrad(self, xy_data, nsmooth = 15):
        # Calculate gradient of the line
        xa=[]
        ya=[]
        for x,y in xy_data:
            xa.append(x)
            ya.append(y)

        v = np.ones(nsmooth)/5.0 # 'nsmooth' averages
        y2a = np.convolve(ya, v, mode='same')

        xna = np.array(xa)
        yna = np.array(ya)
        dy = np.gradient(yna)
        dys = np.gradient(y2a)
        
        x_ysmooth_array = []
        x_ysmooth_grad_array = []
        for x,y,ysmooth,dy,dys in zip(xna,yna,y2a,dy,dys):
            print("SMS:",x,y,ysmooth,dy,dys)
            x_ysmooth_array.append((x,int(ysmooth)))
            x_ysmooth_grad_array.append((x,int(dys)))
        
        #return x_ysmooth_array
        return x_ysmooth_grad_array, x_ysmooth_array
    
if __name__=="__main__":
    cip = CryImageProc()
    
    # set Target/Back images
    #testimage = "Data/test03.ppm" # upper hamideteru
    testimage = sys.argv[1]
    #testimage = "../test.ppm"
    cip.setImages(testimage,"/isilon/users/target/target/PPPP/10.Zoo/BackImages/back-2004082221.ppm")

    prefix = "ono_ke"
    cont = cip.getContour()
    #cip.printROI(roi_xy)

    #roi_len_pix = cip.setRegionFromTop(300.0)

    top_xy = cip.find_top_x(cont)
    #xmax = xtop + roi_len_pix
    #print "XTOP = ",xtop
    roi_len_um = 200.0
    roi_xy = cip.selectHoriROI(cont, top_xy, roi_len_um)

    print(type(roi_xy))
    print(roi_xy)

    outimage = "con_check.png"
    cip.drawContourOnTarget(roi_xy, outimage)
    outimage = "top_check.png"
    cip.drawTopOnTarget(top_xy, outimage)

    # ROI
    left_flag, right_flag, lower_flag, upper_flag, n_true = cip.isTouchedToEdge(roi_xy)
    print("LEFT = ",left_flag)
    print("RIGH = ",right_flag)
    print("LOWE = ",lower_flag)
    print("UPPE = ",upper_flag)

    # Defining raster area
    roi_xmin, roi_xmax, roi_ymin, roi_ymax, roi_cenx, roi_ceny = cip.getRasterArea(roi_xy)
    outimage = "raster.png"
    #cip.drawRasterSquare(xmin, xmax, ymin, ymax, outimage)
    #cip.drawRasterSquare(xmin, xmax, ymin, ymax, outimage)

    # ALL
    roi_xy = cip.selectHoriROI(cont, top_xy, 10000)
    #left_flag, right_flag, lower_flag, upper_flag = cip.isTouchedToEdge(roi_xy)
    #print "LEFT = ",left_flag
    #print "RIGH = ",right_flag
    #print "LOWE = ",lower_flag
    #print "UPPE = ",upper_flag
    outimage = "con_check2.png"
    cip.drawContourOnTarget(roi_xy, outimage)
    outimage = "top_check2.png"
    cip.drawTopOnTarget(top_xy, outimage)

    conf = open("contour.dat","w")
    for xy in roi_xy:
        x,y = xy
        conf.write("%8d %8d\n"%( x,y))
    conf.close()

    # middle line of target ROI
    #middleLine=cip.find_middle_line(roi_xy)
    #l_angle,l_score,l_meany=cip.fitting_pix_line(middleLine)
    #print l_angle, l_score, l_meany
  
    """
    l_text = "Lower angle = %5.1f score = %5.1f meany = %5.3f"%(l_angle,l_score,l_meany)
    cv2.putText(baseimg, l_text, (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255,255,255), thickness=1)

    line_start_x = xmin
    line_end_x = xmax
    l_line_start_y = int(l_meany)
    xlen = xmax - xmin

    l_diff_y = int(xlen*np.tan(np.radians(l_angle)))

    cv2.line(baseimg, (xmin,l_line_start_y), (xmax,l_line_start_y+l_diff_y),(0,0,255),3)
    cv2.imwrite("%s_ana.png"%prefix,baseimg)
    """
