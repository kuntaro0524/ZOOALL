import sys,os,math,numpy
import MyException
import time
import datetime
import DiffscanLog
import logging
import cv2
import LogString

class PixelCrystal:
    # initialize with 3D coordinate
    def __init__(self, contour):
        # Currently, contour should be rectangle shape
        self.contour = contour
        self.DEBUG=False
        # Information of spatial relationships
        self.sporel = []
        # Logging setting
        FORMAT = '%(asctime)-15s %(module)s %(levelname)-8s %(lineno)s %(message)s'
        logging.basicConfig(filename="./pixel_crystal.log", level=logging.INFO, format=FORMAT)
        self.logger = logging.getLogger('PixelCrystal')

        self.lgs = LogString.LogString()
        self.isCheckOverlap = False

        # A list of oscillation range for each crystal position
        self.isStoreOsc = True
        self.outpath = "./"

    def setOutPath(self, outdir):
        self.outpath = outdir

    def printAll(self):
        index=0
        for codes in self.contour:
            v,h = codes[0]
            self.logger.debug("contour codes(V,H)= %5d,%5d" % (v,h))

    def setShape(self, shape):
        self.shape = shape
        # Log image
        self.logimg = numpy.empty(self.shape, dtype=numpy.float32)
        cv2.drawContours(self.logimg, self.contour, -1, (255, 255, 0), 3)

    def writeLogImage(self, logimage_name):
        outname = os.path.join(self.outpath, logimage_name)
        cv2.imwrite(outname, self.logimg)

    def addEdgeToImage(self):
        self.addCircleTo(self.maxx)
        self.addCircleTo(self.minx)
        self.addCircleTo(self.miny)
        self.addCircleTo(self.maxy)

    # Add information of spatial relationship between 'i' th crystal.
    def addSpatialRelation(self, pattern, crystal_index, overlap_xrange, roi_cont, vlen_min):
        dict_info = {'pattern': pattern,                # Overlap pattern "X": no overlap
                     'cry_index': crystal_index,        # Partner crystal index
                     'overlap_xrange': overlap_xrange,  # horizontal range
                     'contour': roi_cont,               # Contour(ROI)
                     'vlen_min': vlen_min}              # minimum vertical distance from the partner crystal
        self.sporel.append(dict_info)

    def getHminHmax(self):
        # minimum of horizontal pixel
        min_h = self.minx[0]
        # maximum of horizontal pixel
        max_h = self. maxx[0]
        return min_h, max_h

    def addCircleTo(self, cen, rgb=(255,255,255)):
        cen_text = "[%d,%d]" % (cen[0],cen[1])
        # numpy array is okay
        center_pos = (cen[0], cen[1])
        text_vpos = cen[0]+10
        text_hpos = cen[1]+10
        cv2.putText(self.logimg, cen_text, (text_vpos, text_hpos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness=1)
        cv2.circle(self.logimg, center_pos, 5, (255,100,255))

    def prepPolyDP(self, cry_index, shape):
        # approx
        approx = cv2.approxPolyDP(self.contour, 0.04 * cv2.arcLength(self.contour, True), True)
        # Draw contour and approx
        check_polydp_img = numpy.zeros(shape, dtype=numpy.float32)
        cv2.drawContours(check_polydp_img, [approx], 0, (255,255,255), 2)
        cv2.drawContours(check_polydp_img, [self.contour], 0, (0,0,255), 3)
        out_name = os.path.join(self.outpath, "polycheck_%02d.png" % cry_index)
        cv2.imwrite(out_name, check_polydp_img)

        # Polydp coordinate analysis
        self.logger.info("%s shape = %s" % (type(approx), approx.shape))
        # lgs = LogString.LogString()
        # numpy.squeeze function reduces 'dimension' of numpy nd arrays.
        # Now, 'approx' array has '(4,1,2)' 3-D array in it.
        # This should be reduced to (4,2) for the following calculation
        approx = approx.squeeze()

        #Sort by vertical direction
        v_sorted_index = approx[:,1].argsort()
        for each_point in approx[v_sorted_index,:]:
            self.logger.debug("Vsort: %5d %5d" % (each_point[0], each_point[1]))

        # length of approx
        n_points = len(v_sorted_index)
        index_min = 0
        index_max = n_points - 1

        # Vmax point
        index_vmin = v_sorted_index[index_min]
        index_vmax = v_sorted_index[index_max]
        self.miny = approx[index_vmin]
        self.maxy = approx[index_vmax]

        h_sorted_index = approx[:,0].argsort()
        for each_point in approx[h_sorted_index,:]:
            self.logger.debug("Hsort: %5d %5d" % (each_point[0], each_point[1]))
        # Hmax point
        index_hmin = h_sorted_index[index_min]
        index_hmax = h_sorted_index[index_max]
        self.miny = approx[index_vmin]
        self.maxy = approx[index_vmax]

        self.minx = approx[index_hmin]
        self.maxx = approx[index_hmax]

        # Judge vector for overlapping
        self.min_x = self.minx[0]
        self.max_x = self.maxx[0]
        self.logger.info("Crystal [%5d-%5d]" % (self.min_x, self.max_x))

        self.cry_length = self.max_x - self.min_x + 1
        self.judge_vector = numpy.zeros(self.cry_length)

        self.logger.info("crystal length = %5d" % self.cry_length)

        self.logger.info(self.lgs.intArray2str(self.minx, "minx="))
        self.logger.info(self.lgs.intArray2str(self.maxx, "maxx="))
        self.logger.info(self.lgs.intArray2str(self.miny, "miny="))
        self.logger.info(self.lgs.intArray2str(self.maxy, "maxy="))

    def prepInfo(self):
        # Extract 4 corner points
        rect = cv2.minAreaRect(self.contour)
        box = cv2.boxPoints(rect)
        box = numpy.int0(box)
        self.box = box

        self.logger.info("Type of box= %s" % type(box))
        for box_code in box:
            self.logger.info("Box coordinates (from cv2.boxPoints)= %5d, %5d" % (box_code[0], box_code[1]))

        #Sort by vertical direction
        v_sorted_index = box[:,1].argsort()
        # Vmax point
        index_vmin = v_sorted_index[0]
        index_vmax = v_sorted_index[3]
        self.miny = box[index_vmin]
        self.maxy = box[index_vmax]

        for each_point in box[v_sorted_index,:]:
            self.logger.debug("Vsort: %5d %5d" % (each_point[0], each_point[1]))

        h_sorted_index = box[:,0].argsort()
        # Vmax point
        index_hmin = h_sorted_index[0]
        index_hmax = h_sorted_index[3]
        self.minx = box[index_hmin]
        self.maxx = box[index_hmax]

        for each_point in box[h_sorted_index,:]:
            self.logger.debug("Hsort: %5d %5d" % (each_point[0], each_point[1]))

        # Judge vector for overlapping
        self.min_x = self.minx[0]
        self.max_x = self.maxx[0]
        self.logger.info("Crystal [%5d-%5d]" % (self.min_x, self.max_x))

        # Check if this box coordinate is included in the contour of this pixel crystal
        self.logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        self.logger.info("Checking 'box' coordinate is included in the contour or not")
        self.getCodeAtH(self.min_x)
        self.getCodeAtH(self.max_x)
        self.logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        self.cry_length = self.max_x - self.min_x +1
        self.judge_vector = numpy.zeros(self.cry_length)

        self.logger.info("crystal length = %5d" % self.cry_length)

        self.logger.info(self.lgs.intArray2str(self.minx, "minx="))
        self.logger.info(self.lgs.intArray2str(self.maxx, "maxx="))
        self.logger.info(self.lgs.intArray2str(self.miny, "miny="))
        self.logger.info(self.lgs.intArray2str(self.maxy, "maxy="))

    # Check overlaps with other crystals
    def checkOverlap(self):
        # Making a log image
        # Check spatial relationships among found crystals
        # each overlap information is already stored in 'sporel' dictionary.
        for spo in self.sporel:
            xmin, xmax = spo['overlap_xrange']
            vlen = spo['vlen_min']

            xmin_work = xmin - self.min_x
            xmax_work = xmax - self.min_x

            # Initial values of 'judge_vector'  = 0.0
            # Searching the minimum 'vlen' on this crystal with others'
            # Finally, the minimum 'vlen' was stored to the 'judge_vector'
            for x_work in range(xmin_work, xmax_work+1):
                current_value = self.judge_vector[x_work]
                if current_value == 0:
                    self.judge_vector[x_work] = vlen
                elif current_value > vlen:
                    self.judge_vector[x_work] = vlen
                else:
                    continue
        self.isCheckOverlap = True
        return self.judge_vector

    # allowed_length: a permitted distance between 2 crystals
    # normally this value should be set around 2.0 * vertical_beamsize
    # to distinguish 2 crystals
    def storeOscVector(self, allowed_length=30.0):
        # print "############# STORE OSC VECTOR ###################"
        if self.isCheckOverlap == False:
            self.checkOverlap()
        # Vector for storing allowed oscillation range
        self.osc_vector = numpy.zeros(len(self.judge_vector))

        for index, vlen in enumerate(self.judge_vector):
            if vlen == 0:
                self.osc_vector[index] = 360.0
            else:
                distance_between_crystal = float(vlen)
                ratio = allowed_length / distance_between_crystal
                # The distance between crystals is already smaller than 'threshold' value of distance.
                # A small wedge data collection should be applied to this part.
                if ratio > 1.0:
                    # set -1.0 as a 'sign' for non-centering data collection
                    self.osc_vector[index] = -1.0
                    continue
                else:
                    permitted_dtheta_radians = numpy.arccos(ratio)
                    permitted_dtheta_deg = numpy.degrees(permitted_dtheta_radians)
                    # print "distance=%5d, theta_deg = %8.1f deg" % (distance_between_crystal, permitted_dtheta_deg)
                    self.osc_vector[index] = permitted_dtheta_deg

        # print self.osc_vector
        self.isStoreOsc = True
        return self.osc_vector

    def classifyModesOnCrystal(self):
        self.logger.info("==============classifyModesOnCrystal============")

        # inner crystal bunch
        dc_info = []

        saved_osc = self.osc_vector[0]
        left_edge_grid = 0

        self.logger.debug("First oscillation= %8.2f deg." % saved_osc)

        each_crystal_volume = {}
        for volume_index, osc_range in enumerate(self.osc_vector):
            # print volume_index, osc_range
            if volume_index == 0:
                continue
            if osc_range == saved_osc:
                right_edge_grid = volume_index
            else:
                self.logger.info("Left - right: %5d-%5d" % (left_edge_grid, right_edge_grid))
                each_crystal_volume['left_edge'] = left_edge_grid
                each_crystal_volume['right_edge'] = right_edge_grid
                # if 'saved_osc' is 0.0 deg -> that is okay for free rotation.
                if saved_osc == 0.0:
                    self.logger.info("this region does not overlap with other crystals.")
                    saved_osc = 360.0
                each_crystal_volume['osc_range'] = saved_osc
                each_crystal_volume['cry_length'] = right_edge_grid - left_edge_grid
                if each_crystal_volume['cry_length'] < 5.0:
                    self.logger.info("crystal size is too small for data collection. (Len=%8.1f)" \
                                     % each_crystal_volume['cry_length'] )
                else:
                    dc_info.append(each_crystal_volume)
                # initialization of this loop
                each_crystal_volume={}
                saved_osc = osc_range
                left_edge_grid = volume_index
                right_edge_grid = volume_index

        # This crystal is overlapped completely with another one.
        each_crystal_volume['left_edge'] = left_edge_grid
        each_crystal_volume['right_edge'] = right_edge_grid
        each_crystal_volume['osc_range'] = saved_osc
        each_crystal_volume['cry_length'] = right_edge_grid - left_edge_grid

        if each_crystal_volume['cry_length'] < 5.0:
            self.logger.info("crystal size is too small for data collection. (Len=%8.1f)" \
                             % each_crystal_volume['cry_length'])
        else:
            dc_info.append(each_crystal_volume)

        # The number of crystal blocks in this 'pixel crystal'
        self.logger.info("Crystal blocks in this crystal: %5d" % len(dc_info))

        for dc_block in dc_info:
            try:
                self.makeCrystalInfo(dc_block)
            except Exception as e:
                print("EEEEEEEEEEEEEEEE=",e.args)
                self.logger.info(e.args)
                continue

        # Combine large oscillation volumes together if oscillation range is over 60.0 degrees.
        num_dc = len(dc_info)
        # Only when the data collection blocks exist more than 2 points
        self.logger.info("Check if connecting the data collection blocks on the same crystal.")
        if num_dc > 1:
            # Get the 1st crystal to be evaluated
            for dc_index, dc_block in enumerate(dc_info):
                self.logger.info("<<< checking if merging ok or not: dc_block 1st >>>>")
                osc_this_block = dc_block['osc_range']
                cry_size_this_block = dc_block['cry_length']
                # The end of processing: this is the last 'cry_length'
                if dc_index + 1 == num_dc:
                    break
                # Check if connection between the next volume
                self.logger.info("<<< checking if merging ok or not: dc_block 2nd >>>>")
                dd_block = dc_info[dc_index + 1]
                osc_next_block = dd_block['osc_range']
                cry_size_next_block = dd_block['cry_length']
                mode_next = dc_info[dc_index+1]['mode']

                # dictionary parameter 'mode' : 'not_collect' is used as a flag to skip processing
                if mode_next == "not_collect":
                    self.logger.info("Evaluation is skipped because this is flagged as 'not_collect'")
                    continue
                # Connectable region: oscillation range is larger than 60.0 deg in both.
                if osc_this_block > 60.0 and osc_next_block > 60.0:
                    if osc_this_block == 360.0 and cry_size_this_block > 40.0:
                        self.logger.info("Leave this block because 360 region is very large.")
                        continue
                    if osc_next_block == 360.0 and cry_size_next_block > 40.0:
                        self.logger.info("Leave this block because 360 region is very large.")
                        continue
                    # A new combined parameters
                    # The next crystal volume dictionary (Left edge from the 1st crystal, right from the 2nd)
                    left_edge = dc_block['left_edge']
                    right_edge = dd_block['right_edge']
                    osc_new = min(osc_this_block, osc_next_block)
                    cry_length = right_edge - left_edge + 1
                    self.logger.info("two volumes are connectable")
                    self.logger.info("1st: %5d-%5d OSC=%8.2f deg" %(dc_block['left_edge'], dc_block['right_edge'], dc_block['osc_range']))
                    self.logger.info("2nd: %5d-%5d OSC=%8.2f deg" %(dd_block['left_edge'], dd_block['right_edge'], dd_block['osc_range']))
                    # Re-calculate gonio XYZ coordinates
                    self.dc_block_update(dd_block, left_edge, right_edge, osc_new, cry_length)
                    dd_block['cry_length'] = cry_length
                    print("NEW=",dd_block)
                    dc_block['mode'] = "not_collect"

                    self.logger.info("""NEW_CRYSTAL= %(left_edge)d-%(right_edge)d: %(osc_range).2f """ % dc_block)

        return dc_info

    # DC block information update
    # left_edge: index on the rotation vector (each crystal: 0 start)
    # right_edge: index on the rotation vector
    def dc_block_update(self, dc_block, left_edge, right_edge, osc_range, cry_length):
        self.logger.info("====makeCrystalInfo=====")
        # 'left_edge' and 'right_edge' are converted to 'HV coordinates' on a pixel crystal
        left_check = left_edge + self.min_x
        right_check = right_edge + self.min_x

        self.logger.info("%5d-%5d(%5d-%5d): Rot=%8.3f deg. Size=%8.2f [um]" %
                         (left_edge, right_edge, left_check, right_check, osc_range, cry_length))

        # Crystal grid
        if cry_length <= 5.0:
            dc_block['mode'] = "not_collect"
            raise MyException.CrystalIsTooSmall("Crystal is too small.")
        # 360 deg. rotation crystals
        elif osc_range == 360.0:
            if cry_length >= 40.0:
                mode="helical_full"
                osc_start = 0.0
                osc_end = 360.0
            if cry_length < 40.0:
                mode="single_full"
                osc_start = 60.0
                osc_end = 90.0
        # A bit wider gap with another crystal
        elif osc_range >= 50.0 and osc_range <= 90.0:
            if cry_length >= 40.0:
                mode="helical_part"
                int_osc = int(osc_range / 2.0)
                osc_start = -float(int_osc)
                osc_end = float(int_osc)
            elif cry_length >= 20.0:
                mode="single_part"
                int_osc = int(osc_range / 2.0)
                osc_start = -float(int_osc)
                osc_end = float(int_osc)
            elif cry_length < 20.0:
                mode="multi"
                osc_start = -5.0
                osc_end = 5.0
        elif osc_range < 50.0:
            if cry_length >= 40.0:
                mode = "helical_noalign"
                osc_start = -20.0
                osc_end = 20.0
            elif cry_length >= 20.0:
                mode = "single_noalign"
                osc_start = -10.0
                osc_end = 10.0
            else:
                mode = "multi"
                osc_start = -5.0
                osc_end = 5.0

        # Apply the parametes to a dictionary
        dc_block['mode'] = mode
        dc_block['osc_start']=osc_start
        dc_block['osc_end']=osc_end
        dc_block['osc_range']=osc_end - osc_start
        self.logger.info("This data collection block: %s" % mode)
        # Mode check and calculate goniometer coordinates
        if dc_block['mode'] == "not_collect":
            dc_block['l_hv'] = -999
            dc_block['r_hv'] = -999

        elif dc_block['mode'].rfind("single")!=-1 or dc_block['mode'].rfind("multi")!=-1:
            hcenter = int((float(left_edge + self.min_x) + float(right_edge + self.min_x)) / 2.0)
            vcenter = self.getVertCenterAtH(hcenter)
            self.logger.info(">>> Mode=%s (H,V)=(%5d,%5d)" % (dc_block['mode'], hcenter, vcenter))
            dc_block['c_hv'] = (hcenter, vcenter)

        elif dc_block['mode'].rfind("helical")!=-1:
            # Crystal left edge
            left_edge_inner = left_edge + 5 + self.min_x# [um]
            right_edge_inner = right_edge - 5 + self.min_x # [um]
            left_vcen = self.getVertCenterAtH(left_edge_inner)
            right_vcen = self.getVertCenterAtH(right_edge_inner)
            self.logger.info(">>> Mode=%6s L(H,V)=(%5d,%5d)" % (dc_block['mode'], left_edge_inner, left_vcen))
            self.logger.info(">>>                R(H,V)=(%5d,%5d)" % (right_edge_inner, left_vcen))
            dc_block['l_hv'] = (left_edge_inner, left_vcen)
            dc_block['r_hv'] = (right_edge_inner, right_vcen)
            self.logger.info("FINAL: %5d-%5d: Rot=%8.3f deg. Size=%8.2f [um]" % (left_edge, right_edge, osc_range, cry_length))

    def makeCrystalInfo(self, dc_block):
        self.logger.info("====makeCrystalInfo=====")
        left_edge = dc_block['left_edge']
        right_edge = dc_block['right_edge']
        osc_range = dc_block['osc_range']
        cry_length = dc_block['cry_length']
        self.dc_block_update(dc_block, left_edge, right_edge, osc_range, cry_length)

    # Draw uchigawa
    def makeUchigawaPoints(self, cv_image, cv_contour, prefix):
        # Make a empty image to visualize 'points' in the points
        uchigawa_img = numpy.zeros(cv_image.shape[:2], dtype=numpy.float32)
        height, width = cv_image.shape[:2]

        self.logger.debug("Type of 'cv_contour'=%s" % type(cv_contour))
        # Store information of distance from 'contour' line.
        for i in range(height):
            for j in range(width):
                value = cv2.pointPolygonTest(cv_contour, (j, i), True)
                uchigawa_img[i, j] = value
                # self.logger.info("UchigawaPoint: (%3d,%3d) = %5d" % (i, j, value))

        # Draw image
        dw_img = numpy.zeros((height, width, 3), dtype=numpy.uint8)
        for y in range(height):
            for x in range(width):
                # Out of 'contour'
                if uchigawa_img[y, x] < 0:
                    dw_img[y, x] = (0, 0, 0)
                # Inside of 'contour'
                elif uchigawa_img[y, x] > 0:
                    self.logger.info("This pixel is inner: (Y,X)=(%d,%d)" % (y, x))
                    index = x - self.min_x
                    rotation_range = self.osc_vector[index]
                    self.logger.debug("From Oscillation vector=%5.1f deg"%self.osc_vector[index])
                    color_height = int(rotation_range/360.0 * 255)
                    dw_img[y, x] = (color_height, color_height, color_height)
                # On the 'contour'
                else:
                    dw_img[y, x] = (255, 255, 255)

        out_name = os.path.join(self.outpath, "%s.png"%prefix)
        cv2.imwrite(out_name, dw_img)

    def getCodeAtH(self, htarget):
        min_v = 999999
        max_v = 0

        found_flag = False

        self.logger.info("Htarget: %5d" % htarget)
        for code in self.contour:
            h, v = code[0]
            if h == htarget:
                found_flag = True
                # self.logger.info("Found %5d,%5d" % (h, v))
                if min_v > v:
                    min_v = v
                if max_v < v:
                    max_v = v

        if found_flag == True:
            self.logger.debug("MIN_V, MAX_V= %5d, %5d" % (min_v, max_v))
            return min_v, max_v
        else:
            self.logger.info("Not found : H=%5d" % htarget)

    # Grid coordinate on the pixel map
    # this function is firstly coded to get HV coordinate of crystal
    # at both edges(left/right).
    def getVertCenterAtH(self, htarget):
        min_v = 999999
        max_v = 0

        is_min_found = False
        is_max_found = False

        self.logger.info("Htarget: %5d" % htarget)
        for code in self.contour:
            h, v = code[0]
            if h == htarget:
                if min_v > v:
                    is_min_found = True
                    min_v = v
                if max_v < v:
                    is_max_found = True
                    max_v = v

        if is_min_found == True and is_max_found == True:
            # Vertical grid coordinates are same at this horizontal position
            # in this case: situation is not so good.
            if min_v == max_v:
                self.logger.info("MIN_V and MAX_V is same coordinates!!")
                raise MyException.SameVerticalCordinates()
            else:
                self.logger.info("MIN_V, MAX_V= %5d, %5d" % (min_v, max_v))
        else:
            self.logger.info("Not found : H=%5d" % htarget)
            raise MyException.FailedToGetVcenter()

        # Crystal coordinate calculation
        medium_v = int((float(min_v) + float(max_v))/2.0)

        self.logger.info("Center position(H,V)=(%5d,%5d)" % (htarget, medium_v))

        return medium_v

    def getXYinHrange(self, hmin, hmax):
        return_code = []
        # print "Assessing %5d - %5d" % (hmin, hmax)
        for code in self.contour:
            h, v = code[0]
            # print h,v
            if h >= hmin and h <= hmax:
                return_code.append((h, v))

        return return_code

    def getCryHsize(self):
        if self.isPrep==False:
            self.prepInfo()
        return self.cry_hsize

    def getRoughEdges(self):
        if self.isPrep==False:
            self.prepInfo()
        print(self.cry_hsize,self.isSingle,self.score_total,self.edges)
        return self.edges

if __name__=="__main__":
    import AnaPictureMap
    import LoopCrystals

    # Logging setting
    FORMAT = '%(asctime)-15s %(module)s %(levelname)-8s %(lineno)s %(message)s'
    logging.basicConfig(filename="./pixel_crystal.log", level=logging.DEBUG, format=FORMAT)
    logger = logging.getLogger('PixelCrystal')

    # Image name
    image_name = sys.argv[1]
    apm = AnaPictureMap.AnaPictureMap(image_name)
    contours = apm.anaInclinedRect(color_inverse=False)

    img = cv2.imread(image_name)
    shape = img.shape

    index = 0
    crystal_list = []
    # h_min and h_max of all crystals
    h_min_all=99999
    h_max_all=0
    for c_index,contour in enumerate(contours):
        crystal = PixelCrystal(contour)
        crystal_list.append(crystal)
        logger.info("##############################")
        crystal.prepInfo()
        crystal.setShape(shape)
        crystal.addEdgeToImage()
        # logger.info("##############################")
        crystal.writeLogImage("log%02d.png" % index)
        hmin, hmax = crystal.getHminHmax()
        logger.info("index=%5d hmin=%5d hmax=%5d" % (c_index, hmin, hmax))
        # Find min horizontal pixel coordinate
        if hmin < h_min_all: h_min_all = hmin
        if hmax > h_max_all: h_max_all = hmax
        index += 1

    # Loop property
    print("MARIO MIN/MAX=", h_min_all, h_max_all)

    # For logging
    logs = LogString.LogString()
    gcolor=10
    # Spatial correlation on the loop
    n_crystals = len(crystal_list)
    # The number of comparisons
    n_compare = 0
    for cry1_index, cry1 in enumerate(crystal_list[:n_crystals-1]):
        logger.info("#### CRYSTAL AT ORIGIN %2d ####" % cry1_index)
        cry1.printAll()
        x1min, x1max = cry1.getHminHmax()
        logger.info("CRY1 X[%5d - %5d]" % (x1min, x1max))
        # The second crystal to be compared to the first one
        for cry2_index, cry2 in enumerate(crystal_list):
            if cry2_index <= cry1_index: continue
            x2min, x2max = cry2.getHminHmax()
            logger.info("CRY2 X[%5d - %5d]" % (x2min, x2max))
            # cry2.printAll()
            # Comparison
            # All patterns (4 + 2 patterns) for 2 crystal alignment
            # No overlap
            if x1max < x2min or x2max < x1min:
                pattern="Z" # Zero overlap
                k_min = 0
                k_max = 0
            # Pattern A
            elif (x2min < x1max and x1max < x2max and x1min < x2min):
                pattern="A"
                k_min = x2min
                k_max = x1max
            # Pattern B
            elif x1min <= x2min and x2max <= x1max:
                pattern="B"
                k_min = x2min
                k_max = x2max
            # Pattern C
            elif x1min < x2max and x2max < x1max and x2min < x1min and x1min < x2max:
                pattern="C"
                k_min = x1min
                k_max = x2max
            # Pattern D
            elif x1min >= x2min and x1max <= x2max:
                pattern="D"
                k_min = x1min
                k_max = x1max

            if k_min == 0:
                logger.info("No overlap!! %5d and %5d" % (cry1_index, cry2_index))
                continue

            # Prepare log image
            # Currently just a class to draw log image.
            lc = LoopCrystals.LoopCrystals(crystal_list)
            lc.prepPic(shape)

            # Logging the results
            logger.info("Overlapped region crystal(%d & %d) %5d - %5d" % \
                  (cry1_index, cry2_index, k_min, k_max))
            # Extract contours in X region in (k_min, k_max)
            array1 = cry1.getXYinHrange(k_min, k_max)
            # Extract contours in X region in (k_min, k_max)
            array2 = cry2.getXYinHrange(k_min, k_max)

            # logger.info("Cry1_extracted %s" % logs.intArray2str(array1, "comp=", isReturn=True))
            # logger.info("Cry2_extracted %s" % logs.intArray2str(cry1_v))

            # Draw extracted contour code of Crystal1
            lc.drawPoints(array1, (255, gcolor, 125))
            gcolor+=30
            # Draw extracted contour code of Crystal2
            lc.drawPoints(array2, (255, gcolor, 255))
            # Calculate 'minimum' distance between crystal1 and 2.
            # cry1_v: the nearest grid to crystal2 on the contour on the crystal1
            # cry2_v: the nearest grid to crystal1 on the contour on the crystal2
            cry1_v, cry2_v = lc.calcVlength(array1, array2, k_min, k_max)

            distance = numpy.fabs(cry1_v[1] - cry2_v[1])

            # Store the 'spatial' relationship here
            cry1.addSpatialRelation(pattern, cry2_index, (k_min,k_max), array1, distance)
            cry2.addSpatialRelation(pattern, cry1_index, (k_min,k_max), array2, distance)

            logger.info("C1 Nearest grid to C2: %s" % logs.intArray2str(cry1_v, ""))
            logger.info("C2 Nearest grid to C1: %s" % logs.intArray2str(cry2_v, ""))
            vimage_comment = "c%02d-c%02d: %5d" % (cry1_index, cry2_index, distance)
            lc.addLineTo(cry1_v, cry2_v, (0,0,255), vimage_comment)
            range_comment = "c%d - c%d [%3d-%3d]" % (cry1_index, cry2_index, k_min, k_max)
            lc.addLineTo((k_min, gcolor), (k_max,gcolor), (125,125,125), range_comment)
            lc.writeLogImage("vert%02d.png" % n_compare)
            lc.prepPic(shape)
            n_compare +=1
            gcolor += 30

    for cry_index, crystal in enumerate(crystal_list):
        logger.info(">>>> Checking crystal %02d <<<<<" % cry_index)
        logger.info("Overlapped crystals: %5d" % (len(crystal.sporel)))
        for i, spdic in enumerate(crystal.sporel):
            cry2_index = spdic['cry_index']
            xmin, xmax = spdic['overlap_xrange']
            vlen_min = spdic['vlen_min']
            pattern = spdic['pattern']
            logger.info("pattern %s: cry%02d: %5d - %5d dist = %5d"
                        % (pattern, cry2_index, xmin, xmax, vlen_min))
            # Prepare log image
            # Currently just a class to draw log image.
            lc = LoopCrystals.LoopCrystals(crystal_list)
            lc.prepPic(shape)
            lc.drawPoints(spdic['contour'], (255, gcolor, 125))
            lc.writeLogImage("cry%02d-%02d.png" % (cry_index, i))
            lc.prepPic(shape)
