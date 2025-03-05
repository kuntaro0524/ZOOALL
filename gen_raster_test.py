import sys, os, math, socket, time
import numpy as np
import datetime
import LoopMeasurement

beamline = "BL45XU"

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    root_dir ="/isilon/users/admin45/admin45/2020B/201102_ZOO_test/RasterTest/"
    scan_id = "2d"
    lm = LoopMeasurement.LoopMeasurement(ms, root_dir, scan_id)

    cxyz = [1.7601, -6.1756, 0.6280]
    phi = 0.00
    scan_id = "beam10_thresh10_true"
    trayid = 1
    pinid = 1
    beamsize = 10.0
    wavelength = 0.9
    startphi = 0.0
    endphi = 90.0
    osc_width = 0.1
    flux = 1.3E13
    gxyz = [-1.1595, 9.1836, 0.1850]
    logfile = open("logfile.log", "w")
    cond={"wavelength":1.0}
    cond['dist_raster']=500.0
    cond['exp_raster']=0.02
    cond['att_raster']=10.0
    cond['raster_roi']=1
    cond['raster_vbeam']=10.0
    cond['raster_hbeam']=10.0
    cond['cover_scan_flag']=1
    lm.raster_dir = os.path.join(root_dir, "scan01")
    lm.rasterMaster(scan_id, "2D", gxyz, 250, 250, 20, 20, 182, cond, flag10um=True, beamsize_thresh_10um=10.0)
