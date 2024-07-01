import cv2,sys,datetime

lines = open(sys.argv[1],"r").readlines()

for filename in lines:
    timg = cv2.imread(filename.strip())
    mean_value = timg.mean()
    if mean_value < 100:
        print "Lower bad file = %s" % filename
    if mean_value > 200:
        print "Higher bad file = %s" % filename
    #print filename.strip(),timg.mean()
