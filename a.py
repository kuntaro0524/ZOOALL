import sys,os,math,cv2,socket,time,copy
import traceback
import logging
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
from MyException import *
import StopWatch
import Condition
import Device
import HEBI,HITO
import DumpRecover
import AnaHeatmap
import ESA
import KUMA
import CrystalList
from html_log_maker import ZooHtmlLog

scan_id="scan00"
raster_path="/isilon/users/target/target/Staff/kuntaro/181127-esa2/test4/CPS1991-02/scan00/"

cxyz=(1.0255,-10.2731,-0.5250)
# Crystal size setting

# getSortedCryList copied from HEBI.py
sphi=136.29
ahm=AnaHeatmap.AnaHeatmap(raster_path,cxyz,sphi)
min_score=10
max_score=80
ahm.setMinMax(min_score,max_score)

# Crystal size setting
cry_size_mm=30/1000.0 #[mm]

# Analyze heatmap and get crystal list
crystal_array=ahm.searchMulti(scan_id,cry_size_mm)

print "FIST=",len(crystal_array)
crystals=CrystalList.CrystalList(crystal_array)

glist=crystals.getSortedPeakCodeList()

#for cry in crystals:
    #cry.printAll()

print len(glist)
