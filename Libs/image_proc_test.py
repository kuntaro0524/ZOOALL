import CryImageProc
import sys

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()
    
    # set Target/Back images
    #testimage = "Data/test03.ppm" # upper hamideteru
    testimage = sys.argv[1]
    #testimage = "../test.ppm"
    cip.setImages(testimage,"/staff/bl44xu/BLsoft/TestZOO/BackImages/back.ppm")
    cont = cip.getContour()


