#!/bin/env python 
import sys
import socket
import time

from Motor import *


class Zoom:
    def __init__(self, server):
        self.s = server
        self.axis = "bl_32in_st2_coax_1_zoom"
        self.zoom = Motor(self.s, self.axis, "pulse")

        self.qcommand = "get/" + self.axis + "/" + "query"

        self.in_lim = "0"  # pulse
        # self.out_lim="-48000" # pulse
        # self.out_lim="-45000" # pulse  YK@210302
        self.out_lim = "-38000"  # pulse  230217 Image was deteriorated by the contamination

    def go(self, pvalue):
        self.zoom.nageppa(pvalue)

    def move(self, pvalue):
        self.zoom.move(pvalue)

    def zoomIn(self):
        self.zoom.move(self.in_lim)

    def getPosition(self):
        return self.zoom.getPosition()[0]

    def zoomOut(self):
        self.zoom.move(self.out_lim)

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
    # host = '192.168.163.1'
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    zoom = Zoom(s)

    start = zoom.getPosition()
    print(start)

    #zoom.move(-20000)

    end = zoom.getPosition()
    print(end)
    # zoom.zoomIn()
    # zoom.zoomOut()
    # time.sleep(5)
    s.close()

"""
	zoom.stop()

	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
	time.sleep(.1)
	end=zoom.getPosition()
	print start,end
#
"""
