<<<<<<< HEAD
import sys,os,math


lines=open(sys.argv[1],"r").readlines()

for line in lines:
    cols = line.split()
    print("%s = cond['%s']"% (cols[0], cols[0]))

=======
import sys
import AnaHeatmap
import LoopCrystals

scan_path = sys.argv[1]

ahm = AnaHeatmap.AnaHeatmap(scan_path)
# Min & Max score value to pick up crystals
min_score = 20
max_score = 200

# print min_score, max_score
ahm.setMinMax(min_score, max_score)

# output image: 'background' = black
# 1 um pixel crystal map from SHIKA heatmap
binimage_name = "%s/bin_summary.png" % scan_path
origin_xyz, vert_koma, hori_koma = ahm.makeBinMap("2d", binimage_name)
# Raster scan horizontal step [um]
raster_resol_um = 20.0
# color_inverse = True: when the back ground color is black
lc = LoopCrystals.LoopCrystals(binimage_name, origin_xyz, vert_koma, hori_koma, raster_resol_um, color_inverse=True)
# Log image files are output to 'scan_path' directory.
lc.setOutPath("./")
lc.prep()
lc.analyze()
dc_blocks = lc.getFinalCenteringInfo()

print(dc_blocks)
>>>>>>> zoo45xu/main
