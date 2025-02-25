import cv2,sys
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")
import CryImageProc
import Capture

if __name__=="__main__":
    cap = Capture.Capture()
    cip = CryImageProc.CryImageProc()
    
    # set Target/Back images
    testimage = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/test.ppm"
    backimage = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/back_190515.ppm"
    cap.capture(testimage)
    cip.setImages(testimage,backimage)
    prefix = "ana"

    # Get contour
    cont = cip.getContour()
    # Find top coordinate
    top_xy = cip.find_top_x(cont)
    left_flag, right_flag, lower_flag, upper_flag, n_true = cip.isTouchedToEdge(cont)

    print "LEFT = ",left_flag
    print "RIGH = ",right_flag
    print "LOWE = ",lower_flag
    print "UPPE = ",upper_flag

    # ROI of the contour defined by 'horizontal' pixel range
    roi_len = 300.0 # [um]
    roi_len_pix = cip.calcPixLen(roi_len)
    roi_xy = cip.selectHoriROI(cont, top_xy, roi_len_pix)

    # Output the images
    outimage = "%s_check01.png"%prefix
    cip.drawContourTop(roi_xy, top_xy, outimage)

    # Finding centering point at X of 'half of horizontal ROI length'
    ox, oy = cip.findCenteringPoint(roi_xy, roi_len_pix, top_xy)

    print "OX,OY=",ox,oy
      
    outimage = "raster_new.png"
    nlen = len(roi_xy)
    tmp_xy = np.reshape(roi_xy, [nlen, 1, 2])
    xmin,xmax,ymin,ymax,cenx,ceny = cip.getRasterArea(tmp_xy)
    print xmin, xmax, ymin, ymax, cenx, ceny

    """
    def getRasterArea(self, contour):
    """

    """

    # ALL
    cont_all = cip.selectHoriROI(cont, top_xy, 10000)
    left_flag, right_flag, lower_flag, upper_flag = cip.isTouchedToEdge(cont_all)
    print "LEFT = ",left_flag
    print "RIGH = ",right_flag
    print "LOWE = ",lower_flag
    print "UPPE = ",upper_flag
    outimage = "%s_check02.png"%prefix
    cip.drawContourTop(cont_all, top_xy, outimage)

    #conf = open("contour.dat","w")
    #for xy in roi_xy:
        #x,y = xy
        #conf.write("%8d %8d\n"%( x,y))
    #conf.close()

    print cip.checkExistence(roi_xy)

    # middle line of target ROI
    middleLine=cip.findMiddleLine(roi_xy)

    #print middleLine
    #for x,y in middleLine:
        #print "middle=",x,y

    cip.drawContourOnTarget(middleLine, "middle_obs.png")

    # fitting middle line on linear function
    fitted_array,l_angle,l_score,l_meany=cip.fitting_pix_line(middleLine)
    cip.drawContourOnTarget(fitted_array, "middle_fit.png")
    print l_angle, l_score, l_meany

    # Find a neck of loop shape
    x_vs_width_list = cip.findLoopNeck(roi_xy)
    x_ysmooth_grad, x_ysmooth = cip.calcSmoothGrad(x_vs_width_list)
    #x_ysmooth = cip.calculateGradient(x_vs_width_list)
    cip.drawContourOnTarget(x_ysmooth, "width.png")
    #cip.calculateGradient(x_ysmooth)
    cip.calcSmoothHenkyokuten(x_vs_width_list)

    #for x,y in x_ysmooth:
        #print "smooth=",x,y
    """
  
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
