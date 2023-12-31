import cv2, sys
import os, glob

TARGET_FILE = sys.argv[1]
IMG_DIR = "./"

target_img_path = TARGET_FILE
target_img = cv2.imread(target_img_path)

bf = cv2.BFMatcher(cv2.NORM_HAMMING)

detector = cv2.AKAZE_create()
(target_kp, target_des) = detector.detectAndCompute(target_img, None)

#print('TARGET_FILE: %s' % (TARGET_FILE))

files = glob.glob("./*ppm")
for file in files:
    if file == '.DS_Store' or file == TARGET_FILE:
        continue

    #print file
    comparing_img_path = IMG_DIR + file
    try:
        comparing_img = cv2.imread(comparing_img_path, cv2.IMREAD_GRAYSCALE)
        (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
        matches = bf.match(target_des, comparing_des)
        dist = [m.distance for m in matches]
        ret = sum(dist) / len(dist)
    except cv2.error:
        ret = 100000

    print("%20s %5.2f"%(file, ret))
