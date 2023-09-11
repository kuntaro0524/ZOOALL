import sys
import AnaHeatmap
import LoopCrystals
import logging

FORMAT = '%(asctime)-15s %(module)s: <%(lineno)5s> [%(funcName)s] %(message)s'
logging.basicConfig(filename="./all_analysis.log", level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger('HITO')

scan_path = sys.argv[1]
ahm = AnaHeatmap.AnaHeatmap(scan_path)

# Fixed value
dist_thresh = 0.015
min_score = 10
max_score = 100

ahm.setMinMax(min_score, max_score)

prefix = "2d"

# output image: 'background' = black
# 1 um pixel crystal map from SHIKA heatmap
binimage_name = "bin_summary.png"
origin_xyz, vert_koma, hori_koma = ahm.makeBinMap(prefix, binimage_name)

print("Making bin map finished.")

# color_inverse = True: when the back ground color is black
lc = LoopCrystals.LoopCrystals(binimage_name, origin_xyz, vert_koma, hori_koma, color_inverse=True)
lc.prep()
print("Prep finished.")

lc.analyze()

print("analysis finished.")

simple_blocks = lc.getFinalCenteringInfo()

print("NUMBER_OF_CRYSTAL_BLOKCS=", len(simple_blocks))

for block in simple_blocks:
    print("EEEEEEEEEEEEEEEECHHHHHHHHHHHHHHHHHHHCRRRRRRRRRRRRRRR")
    for key in list(block.keys()):
        print(key, block[key], type(block[key]))
