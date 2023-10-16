#!/bin/env python 
import sys
import socket
import time
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

from Motor import *

class Zoom:
    def __init__(self, server):
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

    def go(self, pvalue):
        self.zoom.nageppa(pvalue)

    def move(self, pvalue):
        self.zoom.move(pvalue)

    def zoomIn(self):
        self.zoom.move(self.in_lim)

    def getPosition(self):
        return self.zoom.getPosition()[0]

    def zoomOut(self):
        self.zoom.move(self.pulse_minzoom)

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
    host = '172.24.242.57'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    zoom = Zoom(s)

    start = zoom.getPosition()
    print(start)

    zoom.zoomOut()

    s.close()

