#!/bin/env python 
import sys
import socket
import time
<<<<<<< HEAD
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation
import os
=======
>>>>>>> zoo45xu/main

from Motor import *

class Zoom:
    def __init__(self, server):
<<<<<<< HEAD
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline.ini 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH']) 

        self.s = server
        self.axis = "bl_44in_st1_video_2_zoom"
        zoom_name = self.config.get("axes", "zoom_x_axis")
        zoom_vme_name = "bl_%s_%s" % (self.bl_object, zoom_name)
        self.zoom = Motor(self.s, zoom_vme_name, "pulse")

        self.qcommand = "get/" + self.axis + "/" + "query"

        # Minimum zoom ratio
        self.pulse_minzoom = self.bssconf.getPulse4MinZoomRatio()

        self.in_lim = "0"  # pulse
        # self.out_lim = "-38000"  # pulse  230217 Image was deteriorated by the contamination
=======
        self.s = server
        self.axis = "bl_45in_st2_coax_1_zoom"
        self.zoom = Motor(self.s, self.axis, "pulse")

        self.qcommand = "get/" + self.axis + "/" + "query"

        self.in_lim = "4830"  # pulse Maximum zoom
        self.out_lim = "1440"  # pulse
>>>>>>> zoo45xu/main

    def go(self, pvalue):
        self.zoom.nageppa(pvalue)

    def move(self, pvalue):
        self.zoom.move(pvalue)

    def zoomIn(self):
        self.zoom.move(self.in_lim)

    def getPosition(self):
        return self.zoom.getPosition()[0]

    def zoomOut(self):
<<<<<<< HEAD
        self.zoom.move(self.pulse_minzoom)
=======
        self.zoom.move(self.out_lim)
>>>>>>> zoo45xu/main

    def isMoved(self):
        isZoom = self.zoom.isMoved()

        if isZoom == 0:
            return True
        if isZoom == 1:
            return False

    def stop(self):
        command = "put/" + self.axis + "/stop"
        self.s.sendall(command)
        tmpstr = self.s.recv(8000)


if __name__ == "__main__":
<<<<<<< HEAD
    host = '172.24.242.57'
=======
    # host = '192.168.163.1'
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    zoom = Zoom(s)
<<<<<<< HEAD

    start = zoom.getPosition()
    print(start)

    zoom.zoomOut()

    s.close()

=======
    start = zoom.getPosition()
    print start
    #zoom.move(2500)
    zoom.zoomOut()
    # zoom.inZoom()
    # time.sleep(5)
    s.close()
>>>>>>> zoo45xu/main
