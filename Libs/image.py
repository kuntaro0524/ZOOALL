import cv2,sys
import matplotlib.pyplot as plt
import numpy as np
import copy
from MyException import *

class TEST:
    def __init__(self, target_file, back_file):
        self.target_file = target_file
        self.back_file = back_file
        self.timg = cv2.imread(target_file)
        self.bimg = cv2.imread(back_file)

    def do(self):
        print "TRY1"
        self.tgrey = cv2.cvtColor(self.timg, cv2.COLOR_BGR2GRAY)
        self.bgrey = cv2.cvtColor(self.bimg, cv2.COLOR_BGR2GRAY)
        print "TRY2"
        self.dimg=cv2.absdiff(self.tgrey,self.bgrey)

        self.im_height = self.timg.shape[0]
        self.im_width = self.timg.shape[1]

        print self.im_height, self.im_width

        # target image on the memory for debug image
        self.target_save = copy.deepcopy(self.timg)

        # min - max in XY directions
        self.xmin = 10
        self.xmax = self.im_width - 10
        self.ymin = 10
        self.ymax = self.im_height - 10

        self.dimg = self.deleteTopLines(self.dimg, 5)
        for x in range(0, self.im_height):
            for y in range(0, self.im_width):
                print x,y,self.dimg[x,y]

        #if self.pad_top == True:

    def deleteTopLines(self, cvimage, ntop):
        for height in range(0, ntop):
            cvimage[height,] = 0

        """
        for x in range(0, self.im_height):
            for y in range(0, self.im_width):
                print x,y,cvimage[x,y]
        """

        return cvimage

if __name__ == "__main__":
    t = TEST("test.ppm", "back_190514.ppm")
    t.do()
