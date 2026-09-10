import sys
import AnaHeatmap

if __name__ == "__main__":
    phi = 0.0
    prefix = "2d"
    scan_path = sys.argv[1]
    ahm = AnaHeatmap.AnaHeatmap(scan_path)
    ahm.prep(prefix)

    min_score = 10
    max_score = 9999
    dist_thresh = 0.02

    # Helical crystal
    # cry_size=float(sys.argv[2])
    # ahm.setMinMax(min_score,max_score)
    ahm.setMinMax(min_score, max_score)
    ahm.searchPixelBunch(prefix, True)