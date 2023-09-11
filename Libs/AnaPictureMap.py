import sys, os, math, numpy, scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import DiffscanLog
import SummaryDat
import Crystal
import cv2
import copy

class AnaPictureMap:
    def __init__(self, imgname):
        self.imgname = imgname
        self.outpath = "./"

    def setOutpath(self, outpath):
        self.outpath = outpath

    def vectorTest(self):
        # original vector
        junk0, junk1, x0, y0, z0, score = self.heatmap[0, 0, :]
        vec0 = numpy.array((x0, y0, z0))

        # vertical 'unit' vector
        junk0, junk1, xv, yv, zv, score = self.heatmap[1, 0, :]
        v_vec = numpy.array((xv, yv, zv)) - vec0

        # vertical 'unit' vector
        junk0, junk1, xh, yh, zh, score = self.heatmap[0, 1, :]
        h_vec = numpy.array((xh, yh, zh)) - vec0

        final_1_1_vec = vec0 + 25*v_vec + 25*h_vec

        print(final_1_1_vec)

        junk0, junk1, x,y,z, score = self.heatmap[25,25,:]
        vec_orig = numpy.array((x,y,z))

        dist = numpy.linalg.norm((final_1_1_vec-vec_orig))
        print("DIFF=", dist)

    def vectorTest2(self):
        import EnlargedHeatmap
        xyz_orig = self.getGonioXYZat(0,0)
        xyz_vert_edge = self.getGonioXYZat(self.nv-1,0)
        xyz_hori_edge = self.getGonioXYZat(0, self.nh-1)

        print(xyz_orig)
        print(xyz_vert_edge)
        print(xyz_hori_edge)

        em = EnlargedHeatmap.EnlargedHeatmap(xyz_orig, xyz_vert_edge, xyz_hori_edge)
   
        v_um = 150.0
        h_um = 100.0

        em.getGonioCode(v_um, h_um)
        nv = int(v_um / 15.0)
        nh = int(h_um / 10.0)

        print("HEATMAP", self.heatmap[nv,nh,:])

    # Judge uchigawa points in contour
    def makeUchigawaPoints(self, cv_image, contour, prefix):
        # Make a empty image to visualize 'points' in the points
        uchigawa_img = numpy.empty(cv_image.shape, dtype=numpy.float32)

        height, width = cv_image.shape[:2]
        print("CONTOURS=", type(contour), contour.shape, cv_image.shape)

        for i in range(height):
            for j in range(width):
                value = cv2.pointPolygonTest(contour, (j, i), True)
                uchigawa_img[i, j] = value

        print("SHAPE_UCHIGAWEA=" , uchigawa_img.shape)
        # Min/Max values
        minVal, maxVal, min_loc, max_loc = cv2.minMaxLoc(uchigawa_img)
        minVal = abs(minVal)
        maxVal = abs(maxVal)

        # Draw image
        print("HEIGHT,WIDTH=", height, width)
        dw_img = numpy.zeros((height, width, 3), dtype=numpy.uint8)
        for y in range(height):
            for x in range(width):
                # print "x,y=",x,y
                if uchigawa_img[y, x] < 0:
                    # SOTOGAWA
                    v = int(255.0 - abs(cv_image[y, x] * 255.0 / minVal))
                    dw_img[y, x] = (0, v, v)
                elif uchigawa_img[y, x] > 0:
                    # UCHIGAWA
                    v = 255 - cv_image[y, x] * 255 / maxVal
                    dw_img[y, x] = (0, 0, v)
                else:
                    dw_img[y, x] = (255, 255, 255)

        outimage = os.path.join(self.outpath, "%s.png" % prefix)
        cv2.imwrite(outimage, dw_img)

    def anaInclinedRect(self, color_inverse=False):
        # Read image
        rimg = cv2.imread(self.imgname, 0)
        # cv2.imwrite("grey.png", rimg)

        # binirization1
        if color_inverse == True:
            tmpimg = cv2.bitwise_not(rimg)
            result1 = cv2.threshold(tmpimg, 200, 200, cv2.THRESH_BINARY_INV)[1]
            outimage = os.path.join(self.outpath, "binbin.png")
            cv2.imwrite(outimage, result1)
        else:
            result1 = cv2.threshold(rimg, 200, 200, cv2.THRESH_BINARY_INV)[1]
            outimage = os.path.join(self.outpath, "binbin.png")
            cv2.imwrite(outimage, result1)

        # Find contours in the grey-scaled image
        cont1, hi1 = cv2.findContours(result1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Printing each contour in 'contours'
        index = 0
        return_contours = []
        norm_col_img = cv2.imread(self.imgname)
        for cont in cont1:
            # Inclined rectangular shape
            inc_rect = cv2.minAreaRect(cont)
            box = cv2.boxPoints(inc_rect)
            box = numpy.int0(box)
            ttt = copy.deepcopy(rimg)
            outimg = copy.deepcopy(norm_col_img)
            iii = cv2.drawContours(outimg, [box], 0, (255,0,0), 2)
            outimage = os.path.join(self.outpath, "inc_rect%02d.png" %  index)
            cv2.imwrite(outimage, iii)

            index += 1
        return cont1

    def polygonSearch(self, color_inverse=False):
        # Read image
        rimg = cv2.imread(self.imgname, 0)
        cv2.imwrite("grey.png", rimg)

        # binirization1
        if color_inverse == True:
            result1 = cv2.threshold(rimg, 200, 200, cv2.THRESH_BINARY_INV)[1]
            cv2.imwrite("binbin.png", result1)
        else:
            result1 = cv2.threshold(rimg, 200, 200, cv2.THRESH_BINARY_INV)[1]
            cv2.imwrite("binbin.png", result1)

        # On mac osx?
        # images, cont1, hi1 = cv2.findContours(result1 ,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # on KAKI cluster
        cont1, hi1 = cv2.findContours(result1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Printing each contour in 'contours'
        index = 0
        norm_col_img = cv2.imread(self.imgname)
        for cont in cont1:
            tmpimg = copy.deepcopy(norm_col_img)
            c = cv2.convexHull(cont)
            cv2.drawContours(tmpimg, cont, -1, (255, 255, 0), 3)
            ## calculation of parameters
            # Aspect ratio
            x, y, w, h = cv2.boundingRect(cont)
            aspect_ratio = float(w) / h

            ## Extent
            area = cv2.contourArea(cont)
            x, y, w, h = cv2.boundingRect(cont)
            rect_area = w * h
            extent = float(area) / rect_area
            # Drawing bounding rectangular shape
            imgname = "rect%02d.png" % index
            ttt = copy.deepcopy(norm_col_img)
            iii = cv2.rectangle(ttt, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.imwrite(imgname, iii)

            # Inclined rectangular shape
            inc_rect = cv2.minAreaRect(cont)
            box = cv2.boxPoints(inc_rect)
            box = numpy.int0(box)
            ttt = copy.deepcopy(rimg)
            outimg = copy.deepcopy(norm_col_img)
            iii = cv2.drawContours(outimg, [box], 0, (255,0,0), 2)
            cv2.imwrite("inc_rect%02d.png" % index, iii)
            self.makeUchigawaPoints(ttt, box, "inc_rect_uchigawa_%02d" % index)

            # Minimum circle
            (x, y), radius = cv2.minEnclosingCircle(cont)
            center = (int(x), int(y))
            radius = int(radius)
            ttt = copy.deepcopy(norm_col_img)
            iii = cv2.circle(ttt, center, radius, (255, 0, 0), 2)
            cv2.imwrite("gaisetsu_en_%02d.png" % index, iii)

            # Ellipse fitting
            ellipse = cv2.fitEllipse(cont)
            ttt = copy.deepcopy(norm_col_img)
            iii = cv2.ellipse(ttt, ellipse, (255, 0, 0), 2)
            cv2.imwrite("ellipse%02d.png" % index, iii)

            ## Solidity
            hull = cv2.convexHull(cont)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area

            ## Equivalent Diameter
            equi_diameter = numpy.sqrt(4 * area / numpy.pi)

            ## Rinkaku Kinji
            epsilon = 0.02 * cv2.arcLength(cont, True)
            approx = cv2.approxPolyDP(cont, epsilon, True)
            print(approx)
            ttt = copy.deepcopy(norm_col_img)
            iii = cv2.drawContours(ttt, [approx], 0, (255, 0, 0), 1)
            cv2.imwrite("rinkaku_kinji%02d.png" % index, iii)
            print("rinkaku_kinji: isContourConvex=", cv2.isContourConvex(approx))

            ## Angle
            (x, y), (MA, ma), angle = cv2.fitEllipse(cont)

            logstr = "asp=%5.2f ext=%5.2f sol=%5.2f ed=%5.2f ang=%5.2f" \
                     % (aspect_ratio, extent, solidity, equi_diameter, angle)

            # Contour zahyou
            for cont_compo in cont:
                x, y = cont_compo[0]
                # print "CONT: ", index, x,y

            v_pos = 5 + 1 * index
            cv2.putText(tmpimg, logstr, (0, v_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (125, 125, 125), 1)
            imgname = "./kakudai_%02d.png" % (index)
            print("isContourConvex= %s" % cv2.isContourConvex(cont))
            print(logstr)
            cv2.imwrite(imgname, tmpimg)
            index += 1

    def test(self):
        rimg = cv2.imread(self.imgname, 0)
        for low_bin in [200,250,300]:
            result1 = cv2.threshold(rimg, low_bin, 200, 0)[1]
            cv2.imwrite("binbin_%d.png" % low_bin, result1)

if __name__ == "__main__":
    image_name = sys.argv[1]
    apm = AnaPictureMap(image_name)
    #apm.test()
    apm.polygonSearch(color_inverse=True)
