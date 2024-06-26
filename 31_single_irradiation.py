import os,sys
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import AnaHeatmap
import CrystalList

raspath = "/isilon/users/admin45/admin45/AutoUsers/190711_BL45XU_Ose/YAO0006-04/scan00/2d/"
center_xyz = 0,0,0
sphi=270.0

ahm = AnaHeatmap.AnaHeatmap(raspath, center_xyz, sphi)
ahm.setMinMax(10, 100)

scan_id = "2d"
crystal_array = ahm.searchPixelBunch(scan_id, naname_include=True)
n_crystals = len(crystal_array)

crystals = CrystalList.CrystalList(crystal_array)
raster_cxyz = crystals.getBestCrystalCode()

print "Final=",raster_cxyz
