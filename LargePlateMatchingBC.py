# from opencv.cv import LoadImageM
# from opencv.highgui import *

# import Image
import os, glob
import sys
import cv2


# 2018/11/08 23:00 K.Hirata coded
# Back camera

class LargePlateMatchingBC:
    def __init__(self):
        # self.template_path=template_path
        # self.template_prefix=template_prefix
        self.isSeiri = False

        self.base_imgdir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
        self.backimg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/bcbg.png"
        self.bc_otehon_bin = "%s/bc_otehon_bin.png" % self.base_imgdir
        # Circular holder template picture

    def setNewTarget(self, target_ppm):
        self.target_ppm = target_ppm

    def basicProc(self, target_pic, gauss=5, prefix="test"):
        # Reading images
        timg = cv2.imread(target_pic)
        bimg = cv2.imread(self.backimg)

        # GRAY SCALE First this is modified from BL32XU version
        gim = cv2.cvtColor(timg, cv2.COLOR_BGR2GRAY)
        gbk = cv2.cvtColor(bimg, cv2.COLOR_BGR2GRAY)
        dimg = cv2.absdiff(gim, gbk)

        # Gaussian blur
        blur = cv2.GaussianBlur(dimg, (3, 3), 0)
        sgb = cv2.threshold(blur, 30, 150, 0)[1]

        cv2.imwrite("./diff.jpg", sgb)

        # 2 valuize
        cv2.imwrite("./bin.jpg", sgb)

        return sgb

    def getROI(self, th_cv2_img):
        # ROI
        self.roi = th_cv2_img[self.ystart:self.yend, self.xstart:self.xend]
        cv2.imwrite("%s_binroi.jpg" % (prefix), self.roi)
        return self.roi

    def simple(self, target_pic, template_pic):
        template = cv2.imread(template_pic, 0)
        target = cv2.imread(target_pic, 0)
        result = cv2.matchTemplate(template, target, cv2.TM_CCOEFF_NORMED)
        cv2.imwrite("result0.jpg", result)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)

        result = cv2.imread(target_pic)
        cv2.rectangle(result, top_left, bottom_right, (255, 0, 0), 2)
        cv2.imwrite("result.jpg", result)

    def getPosition(self, target_image, phi=0.0):
        if self.isSeiri == False:
            self.fileSeiri()
        zero_template = self.template_list[0][0]
        target_cvimage = cv2.imread(target_image, 0)
        template = cv2.imread(zero_template, 0)

        cv2.imwrite("zero.png", template)
        cv2.imwrite("target.png", target_cvimage)

        result = cv2.matchTemplate(template, target_cvimage, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        result = cv2.imread(target_image)
        cv2.rectangle(result, top_left, bottom_right, (255, 0, 0), 2)
        cv2.imwrite("result.jpg", result)

        print("MAX_LOC=", max_loc)
        return max_loc

    # Modified on 2018/11/08 K.Hirata
    def getHoriVer_old(self, target_image):
        tmp = cv2.imread(self.bc_otehon_bin)
        template = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        h, w = template.shape[0], template.shape[1]

        # Basic process for getting binarized image
        bin_target = self.basicProc(target_image, gauss=5, prefix="test")

        result = cv2.matchTemplate(template, bin_target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # print "MAX_LOC=",max_loc
        # print top_left,bottom_right
        cv2.rectangle(bin_target, top_left, bottom_right, (255, 0, 0), 2)
        cv2.imwrite("result.jpg", bin_target)

        return max_loc

    # Modified on 2021/06/08 K.Hirata
    def getHoriVer(self, cvimg_bin):
        tmp = cv2.imread(self.bc_otehon_bin)
        template = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        h, w = template.shape[0], template.shape[1]

        # Basic process for getting binarized image
        bin_target = self.basicProc(target_image, gauss=5, prefix="test")

        result = cv2.matchTemplate(template, bin_target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # print "MAX_LOC=",max_loc
        # print top_left,bottom_right
        cv2.rectangle(bin_target, top_left, bottom_right, (255, 0, 0), 2)
        cv2.imwrite("result.jpg", bin_target)

        return max_loc

    def getSimilarity(self, target_cvimage, template_pic):
        template = cv2.imread(template_pic, 0)
        result = cv2.matchTemplate(template, target_cvimage, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_val

    def fileSeiri(self):
        lll = "%s/%s*template*" % (self.template_path, self.template_prefix)
        # print lll
        filelist = glob.glob(lll)
        # print filelist
        self.template_list = []
        for f in filelist:
            filename = f.split('/')[-1]
            ppp = filename.replace(self.template_prefix, "")
            phi = float(ppp.split('_')[0])
            self.template_list.append((f, phi))

        self.template_list = sorted(self.template_list, key=lambda x: x[1], reverse=False)

    def match(self, target_pic):
        print("Matching")
        if self.isSeiri == False:
            self.fileSeiri()
        # print self.template_list
        max_sim = 0.0
        ok_phi = -99999.99999
        ok_file = ""
        for f, phi in self.template_list:
            max_val = self.getSimilarity(target_pic, f)
            # print f,max_val
            if max_val > max_sim:
                max_sim = max_val
                ok_file = f
                ok_phi = phi

        print(ok_file, max_sim)
        return ok_file, ok_phi, max_sim

    def comp(self, pinimg, back, template_image):
        th = self.basicProc(pinimg, back)
        # cv2.imwrite("th.png",th)

        template = cv2.imread(template_image, 0)
        cv2.imwrite("cam1_comp_th.jpg", th)

        result = cv2.matchTemplate(template, th, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)

        result = cv2.imread(pinimg)
        cv2.rectangle(result, top_left, bottom_right, (255, 0, 0), 2)
        cv2.imwrite("result1.jpg", result)

        print("Max value=", max_val, "TOP_LEFT=", top_left)
        return max_val, top_left


if __name__ == "__main__":
    tm = LargePlateMatching("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/", "holder01")
    # tm.simple(sys.argv[1],sys.argv[2])
    pinimg = sys.argv[1]
    back = sys.argv[2]
    template = sys.argv[3]

    tm.comp(pinimg, back, template)
