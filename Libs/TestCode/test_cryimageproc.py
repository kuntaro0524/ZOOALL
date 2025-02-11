import CryImageProc
import sys

if __name__=="__main__":
    cip = CryImageProc()
    
    # set Target/Back images
    #testimage = "Data/test03.ppm" # upper hamideteru
    testimage = sys.argv[1]
    #testimage = "../test.ppm"
    cip.setImages(testimage,"/staff/bl44xu/BLsoft/TestZOO/BackImages/back.ppm")

    cont = cip.getContour()
    top_xy = cip.find_top_x(cont)
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
