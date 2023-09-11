import os, sys, numpy, logging
import cv2
# My modules
import AnaPictureMap, PixelCrystal, LogString

# LoopCrystals: holds a list of 'PixelCrystal'
# 'PixelCrystal' is a bunch of grids of found 'contour' by opencv function.
# 'contour' would roughly shows a shape of crystal I believe.
class LoopCrystals():
    def __init__(self, one_micron_picture, gonio_ovec, gonio_vvec, gonio_hvec, color_inverse=False):
        self.image_name = one_micron_picture
        self.color_inverse = color_inverse

        # Goniometer origin/vertical/horizontal vectors
        self.govec = gonio_ovec
        self.gvvec = gonio_vvec
        self.ghvec = gonio_hvec

        # Logging setting
        FORMAT = '%(asctime)-15s %(module)s %(lineno)s %(funcName)s %(message)s'
        logging.basicConfig(filename="./loop_crystals.log", level=logging.DEBUG, format=FORMAT)

        self.logger = logging.getLogger('HITO').getChild("LoopCrystals")

        # Initialization flag
        self.isPrep = False
        self.outpath = "./"

        # Threshold of distance between 2 crystals in vertical direction
        # (allowed 'gap' distance viewed from X-ray)
        self.allowed_dist = 30.0

    # Change a threshold value of a gap between 2 crystals
    def setAllowedDist(self, allowed_dist):
        self.allowed_dist = allowed_dist

    def prep(self):
        # For logging
        logs = LogString.LogString()

        # Image name
        apm = AnaPictureMap.AnaPictureMap(self.image_name)
        apm.setOutpath(self.outpath)

        # opencv contours acquisition
        contours = apm.anaInclinedRect(color_inverse=self.color_inverse)

        # Get the shape of the input picture
        img = cv2.imread(self.image_name)
        self.shape = img.shape

        self.logger.debug("Image shape: %s" % logs.intArray2str(img.shape, "Image shape=", isReturn=False))

        index = 0
        # A list of crystals: a list of 'PixelCrystal'
        self.crystal_list = []
        # h_min and h_max of all crystals
        h_min_all = 99999
        h_max_all = 0
        # Working-loop for analysing each contour corresponding to a 'pixel crystals'.
        for c_index, contour in enumerate(contours):
            crystal = PixelCrystal.PixelCrystal(contour)
            crystal.setOutPath(self.outpath)
            self.crystal_list.append(crystal)
            self.logger.info("########### Crystal index = %5d #############" % c_index)
            # crystal.prepInfo()
            crystal.prepPolyDP(c_index, self.shape)
            crystal.setShape(self.shape)
            crystal.addEdgeToImage()
            outimg_path = os.path.join(self.outpath, "cry%02d_edge.png" % index)
            crystal.writeLogImage(outimg_path)
            hmin, hmax = crystal.getHminHmax()
            self.logger.info("Cry(index=%2d) hmin=%3d hmax=%3d" % (c_index, hmin, hmax))
            # Find min horizontal pixel coordinate
            if hmin < h_min_all: h_min_all = hmin
            if hmax > h_max_all: h_max_all = hmax
            index += 1

        gcolor = 10
        # Spatial correlation among crystals on the loop
        # The number of found crystals on the loop
        n_crystals = len(self.crystal_list)
        # The number of comparisons
        n_compare = 0
        # Souatari analysis among crystals
        for cry1_index, cry1 in enumerate(self.crystal_list[:n_crystals - 1]):
            self.logger.info("#### CRYSTAL AT ORIGIN %2d ####" % cry1_index)
            self.logger.info("contour codes =====")
            # cry1.printAll()
            # The horizontal X range of 1st crystal
            x1min, x1max = cry1.getHminHmax()
            self.logger.info("CRY1 X[%5d - %5d]" % (x1min, x1max))
            # The second crystal to be compared to the first one
            for cry2_index, cry2 in enumerate(self.crystal_list):
                if cry2_index <= cry1_index: continue
                x2min, x2max = cry2.getHminHmax()
                self.logger.info("CRY2 X[%5d - %5d]" % (x2min, x2max))
                # Comparison
                # All patterns (5 patterns) for 2 crystal alignment
                # No overlap
                if x1max < x2min or x2max < x1min:
                    pattern = "Z"  # Zero overlap
                    k_min = 0
                    k_max = 0
                # Pattern A
                elif (x2min < x1max and x1max < x2max and x1min < x2min):
                    pattern = "A"
                    k_min = x2min
                    k_max = x1max
                # Pattern B
                elif x1min <= x2min and x2max <= x1max:
                    pattern = "B"
                    k_min = x2min
                    k_max = x2max
                # Pattern C
                elif x1min < x2max and x2max < x1max and x2min < x1min and x1min < x2max:
                    pattern = "C"
                    k_min = x1min
                    k_max = x2max
                # Pattern D
                elif x1min >= x2min and x1max <= x2max:
                    pattern = "D"
                    k_min = x1min
                    k_max = x1max
                else:
                    pattern = "Unknown"
                    k_min = 0
                    k_max = 0

                # Crystals have no overlaps along a rotation axis
                if k_min == 0 or k_max == 0:
                    self.logger.info("No overlap!! CRY%5d and CRY%5d" % (cry1_index, cry2_index))
                    self.logger.info("A recognized pattern = %s" % pattern)
                    self.logger.info("########################")
                    continue
                # Prepare log image
                # Currently just a class to draw log image.
                self.prepPic(self.shape)

                # Logging the results
                self.logger.info("Overlapped region crystal(%d & %d) %5d - %5d" % \
                            (cry1_index, cry2_index, k_min, k_max))
                # Extract contours in X region in (k_min, k_max)
                array1 = cry1.getXYinHrange(k_min, k_max)
                if len(array1) == 0:
                    self.logger.info("No overlaps!")
                    continue
                # Extract contours in X region in (k_min, k_max)
                array2 = cry2.getXYinHrange(k_min, k_max)
                if len(array2) == 0:
                    self.logger.info("No overlaps!")
                    continue

                # Draw extracted contour code of Crystal1
                self.drawPoints(array1, (255, gcolor, 125))
                gcolor += 30
                # Draw extracted contour code of Crystal2
                self.drawPoints(array2, (255, gcolor, 255))

                # Calculate 'minimum' distance between crystal1 and 2.
                # cry1_v: the nearest grid to crystal2 on the contour on the crystal1
                # cry2_v: the nearest grid to crystal1 on the contour on the crystal2
                cry1_v, cry2_v, distance = self.calcVlength(array1, array2, k_min, k_max)

                # Store the 'spatial' relationship here
                cry1.addSpatialRelation(pattern, cry2_index, (k_min, k_max), array1, distance)
                cry2.addSpatialRelation(pattern, cry1_index, (k_min, k_max), array2, distance)

                self.logger.info("C1 Nearest grid to C2: %s" % logs.intArray2str(cry1_v, ""))
                self.logger.info("C2 Nearest grid to C1: %s" % logs.intArray2str(cry2_v, ""))
                vimage_comment = "%d-%d\nd=%5d" % (cry1_index, cry2_index, distance)
                self.addLineTo(cry1_v, cry2_v, (0, 0, 255), vimage_comment)
                range_comment = "%d-%d\n[%3d-%3d]" % (cry1_index, cry2_index, k_min, k_max)
                self.addLineTo((k_min, gcolor), (k_max, gcolor), (125, 125, 125), range_comment)
                self.writeLogImage("vert%02d.png" % n_compare)
                self.prepPic(self.shape)
                n_compare += 1
                gcolor += 30
                self.logger.info("######################")

        self.n_crystal = len(self.crystal_list)
        self.isPrep = True

    def getColorCode(self, distance):
        if distance < 30:
            return (255,0,0)
        elif distance < 60:
            return (125,125,0)
        elif distance < 90:
            return (0,255,0)
        elif distance < 150:
            return (0, 255, 125)
        elif distance < 250:
            return (0, 125, 180)
        else:
            return (0,0,255)

    def setOutPath(self, outpath):
        self.outpath = outpath

    def analyze(self):
        if self.isPrep == False: self.prep()

        # Entire log file to visualize spatial relationships of crystals
        logimg = numpy.zeros(self.shape, dtype=numpy.float32)
        osc_info = []
        for cry_index, crystal in enumerate(self.crystal_list):
            # Re-do checking crystal configuration.
            # 'judge_vector' has a 1-D vector including a list of the shortest distance
            # between another crystal(PixelCrystal class).
            judge_vector = crystal.checkOverlap()
            min_x = crystal.min_x
            # crystal.findFullHelicalRegion()
            print("OSC_VECTOR %5d" % cry_index)
            osc_vec = crystal.storeOscVector(self.allowed_dist)
            # The minimum horizontal grid coordinate
            osc_info.append(osc_vec)

            self.logger.info(">>>> Checking crystal %02d <<<<<" % cry_index)
            self.logger.info("Overlapped crystals: %5d" % (len(crystal.sporel)))
            # Draw crystal shape of the target
            cv2.drawContours(logimg, crystal.contour, -1, (255, 255, 255), 1)

            # Class variant 'sporel' is a 'dictionary' to store spatial relationship
            # with another crystal (index, overlap_xrange, vlen_min, pattern)
            for i, spdic in enumerate(crystal.sporel):
                cry2_index = spdic['cry_index']
                xmin, xmax = spdic['overlap_xrange']
                vlen_min = spdic['vlen_min']
                pattern = spdic['pattern']
                self.logger.info("pattern %s: cry%02d: %5d - %5d dist = %5d"
                            % (pattern, cry2_index, xmin, xmax, vlen_min))
                # Contour color
                rgb = self.getColorCode(vlen_min)
                # This contour is not 'opencv' contour. Just a list of XY coordinates.
                comments = "%d:%d = %s" % (cry_index, cry2_index, pattern)
                self.drawPointsToCVimg(spdic['contour'], logimg, rgb, comments=comments)

            out_name = os.path.join(self.outpath, "name%02d.png" % cry_index)
            cv2.imwrite(out_name, logimg)

    def getFinalCenteringInfo(self):
        # Entire log file to visualize spatial relationships of irradiation points
        logimg = numpy.zeros(self.shape, dtype=numpy.float32)

        # Crystal vectors of data collection
        final_centering_info = []
        for cry_index, crystal in enumerate(self.crystal_list):
            # Minimum horizontal grid coordinate
            min_x = crystal.min_x
            # rotation information of this crystal
            rot_info = crystal.osc_vector
            # horizontal range
            hmin, hmax = crystal.getHminHmax()
            # checking crystal size
            cry_size = hmax - hmin +1 # [um]
            # Information is not stored if crysta size is smaller than 5 um.
            if cry_size < 5.0:
                self.logger.info("Crystal is smaller than 5.0 um : skipped to make contours")
                continue
            # Crystal size is larger than 5.0 um.
            else:
                cv2.drawContours(logimg, crystal.contour, -1, (255,255,255), 1)

                self.logger.info("CCCCCCCCCCCCCCCCC CRYINDEX=%5d RRRRRRRRRRRRRRRRRRRRRR" % cry_index)
                # dc_blocks: a 'list' of 'crystal blocks' for same 'data collection parameters'
                # dc_block in 'dc_blocks' is a 'dictionary' for storing data collectino parameters for each crystal volume
                # 'dc_block' will be referred from a module which makes a schedule file.
                dc_blocks= crystal.classifyModesOnCrystal()
                final_centering_info.append((cry_index, dc_blocks))

        # simple crystal volume array
        simple_blocks = []
        for cry_index, dc_blocks in final_centering_info:
            for block_index, dc_block in enumerate(dc_blocks):
                # If 'not_collect' flag is set -> skipped.
                if dc_block['mode'] == 'not_collect':
                    self.logger.info("crystal %5d: part %5d is not collected." % (cry_index, block_index))
                    continue
                elif dc_block['mode'].rfind("multi")!=-1 or dc_block['mode'].rfind("single")!=-1:
                    (hcenter, vcenter) = dc_block['c_hv']
                    self.logger.info("MODE_MULTI: center(%5d,%5d)" % (hcenter, vcenter))
                    dc_block['cxyz'] = self.calcGxyzFromHV(hcenter, vcenter)
                    # comment = "C%02d-B%02d: %8.3f" % (cry_index, block_index, dc_block['osc_range'])
                    cv2.circle(logimg, (hcenter, vcenter), 5, (255,255,0))
                    # cv2.putText(logimg, comment, (hcenter+10, vcenter+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), thickness=1)
                    simple_blocks.append(dc_block)
                else: # Helical data collection
                    print(dc_block)
                    lh, lv = dc_block['l_hv']
                    rh, rv = dc_block['r_hv']
                    self.logger.info("MODE_HELICAL: L(%5d,%5d) - R(%5d, %5d)" % (lh, lv, rh, rv))
                    # comment = "C%02d-B%02d: %8.3f" % (cry_index, block_index, dc_block['osc_range'])
                    # cv2.putText(logimg, comment, (lh, lv), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), thickness=1)
                    lvec = self.calcGxyzFromHV(lh, lv)
                    rvec = self.calcGxyzFromHV(rh, rv)
                    dc_block['lxyz'] = lvec
                    dc_block['rxyz'] = rvec
                    comment = "L %8.3f %8.3f %8.3f" % (lvec[0], lvec[1], lvec[2])
                    cv2.putText(logimg, comment, (lh, lv), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), thickness=1)
                    comment = "R %8.3f %8.3f %8.3f" % (rvec[0], rvec[1], rvec[2])
                    cv2.putText(logimg, comment, (rh, rv+10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), thickness=1)

                    cv2.line(logimg, (lh, lv), (rh, rv), (255,0,255), 3)
                    print("FINAL_dc_block=", dc_block)
                    simple_blocks.append(dc_block)

        out_name = os.path.join(self.outpath, "hito.png")
        cv2.imwrite(out_name, logimg)

        self.checkCornerXYZ()

        return simple_blocks

    def calcGxyzFromHV(self, h, v):
        # Goniometer origin/vertical/horizontal vectors
        # horizontal grid coordinate is left-right opposite between SHIKA heatmap and 'pixel map'

        nh_on_pixmap = self.shape[1]
        h_grid_on_shikamap = nh_on_pixmap - h
        final_xyz = self.govec + float(h_grid_on_shikamap) * self.ghvec + float(v) * self.gvvec
        self.logger.info("FINAL_XYZ: %9.4f %9.4f %9.4f" % (final_xyz[0], final_xyz[1], final_xyz[2]))

        return final_xyz

    def checkCornerXYZ(self):
        nh_pix = self.shape[1]
        nv_pix = self.shape[0]
        # Right & Upper
        origin = self.govec
        # Right & lower
        right_lower = self.govec + float(nv_pix) * self.gvvec
        # Left & upper
        left_upper = self.govec + float(nh_pix) * self.ghvec
        # Left & lower
        left_lower = self.govec + float(nv_pix) * self.gvvec + float(nh_pix) * self.ghvec

        print("ORI=", origin)
        print("RL=", right_lower)
        print("LU=", left_upper)
        print("LL=", left_lower)

    def prepPic(self, shape):
        self.shape = shape
        # Log image
        self.logimg = numpy.zeros(self.shape, dtype=numpy.float32)

    def addCircleTo(self, cen, rgb=(255,255,255)):
        cen_text = "[%d,%d]" % (cen[0],cen[1])
        text_xpos = cen[1]+10
        text_ypos = cen[0]+10
        cv2.putText(self.logimg, cen_text, (text_ypos, text_xpos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, thickness=2)
        cv2.circle(self.logimg, cen, 5, rgb)

    def addLineTo(self, left_edge, right_edge, rgb=(255,255,255), comment=""):
        cv2.line(self.logimg, left_edge, right_edge, rgb, 3)
        cen_text = (left_edge[0]+100, left_edge[1])
        if comment != "":
            cv2.putText(self.logimg, comment, cen_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, thickness=1)

    def drawPoints(self, xy_array, rgb=(255,255,255), comments=""):
        for xy in xy_array:
            cv2.drawMarker(self.logimg, xy, rgb,
                           markerType=cv2.MARKER_CROSS, thickness=1, line_type=cv2.LINE_8,
                           markerSize=1)

    def drawPointsToCVimg(self, xy_array, cvimg, rgb=(255,255,255), comments = ""):
        # print "RGB=", rgb
        for xy in xy_array:
            cv2.drawMarker(cvimg, xy, rgb,
                           markerType=cv2.MARKER_CROSS, thickness=1, line_type=cv2.LINE_8,
                           markerSize=5)
        cv2.putText(cvimg, comments, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, thickness=1)

    def writeLogImage(self, logimage_name):
        out_name = os.path.join(self.outpath, logimage_name)
        cv2.imwrite(out_name, self.logimg)

    # xy_array1, xy_array2: contour coordinates consist of 'XY' tuple arrays
    # currently "X" range of two arrays are identical
    def calcVlength(self, xy_array1, xy_array2, xmin, xmax):
        vlen_min = 999999

        lgs = LogString.LogString()
        # print "**************** calcVlength ******************"
        # print xy_array1
        # print xy_array2

        for xwork in range(xmin, xmax):
            # From crystal1
            for x1,y1 in xy_array1:
                if xwork == x1:
                    yset = y1
                    for x2,y2 in xy_array2:
                        if xwork == x2:
                            yset2 = y2
                            self.logger.debug("C1: %5d,%5d: C2 XY=%5d,%5d" % (x1,y1, x2, y2))
                            diff_v = numpy.fabs(y2-y1)
                            # print "DIFF=", diff_v
                            if vlen_min > diff_v:
                                vlen_min = diff_v
                                cry1_vpoint = (x1,y1)
                                cry2_vpoint = (x2,y2)
                                # print x1,y1
                                # print x2,y2
                                # print "DIFF=%5d" % vlen_min
        return cry1_vpoint, cry2_vpoint, vlen_min

if __name__=="__main__":
    lc = LoopCrystals(sys.argv[1], color_inverse=False)
    lc.prep()
    lc.analyze()
