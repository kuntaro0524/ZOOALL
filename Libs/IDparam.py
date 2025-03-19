import math
from AnalyzePeak import *


class IDparam:
    def __init__(self):
        # self.p1=-3.90483
        # self.p2=23.37527
        # self.p3=9.75211

        # 102015 determined
        # self.p1=-3.59798
        # self.p2=22.583
        # self.p3=9.38048

        # 100217 determined (scanned with 1um resolution)
        # self.p1=-3.62198
        # self.p2=22.6115
        # self.p3=9.37671

        # 101115 determined (scanned with 1um resolution)
        # self.p1=-3.54831
        # self.p2=22.4791
        # self.p3=9.36296

        # 101209 test (scanned with 1um resolution)
        # Fit this curve to the splined observed data
        self.p1 = -3.573
        self.p2 = 22.493
        self.p3 = 9.3401

    # a               = -3.573           +/- 0.00292      (0.08172%)
    # b               = 22.493           +/- 0.007316     (0.03253%)
    # c               = 9.34013          +/- 0.002375     (0.02543%)

    # Energy (keV)
    def getGapObsoleted(self, energy):
        # print self.p2/energy-1
        if (energy >= 23.2):
            gap = 45.0
        else:
            gap = self.p1 * math.log(self.p2 / energy - 1) + self.p3

        gapchar = "%12.3f" % gap
        # print "gap=%12.5f\n"%float(gapchar)
        return float(gapchar)

    ##################################################################################
    # Energy (keV)
    # 2010/05/11 kuntaro modified
    # bss.config has a suitable gap table of BL32XU.
    # BSS estimated the best gap for the set Energy by splining the data table.
    # The PYTHON script library should have a same table for changine energy
    # Table data was collected on 2010/11/15. The table was allocated in
    # /isilon/BL32XU/BLsoft/PPPP/07.IDparams/id32xu.tbl
    # The new 'getGap' function acts as same as BSS.
    ##################################################################################

    def getGap(self, energy):
        ana = AnalyzePeak("/isilon/BL32XU/BLsoft/PPPP/07.IDparams/id32xu.tbl")
        px, py = ana.prepData2(0, 1)
        en_list, gap_list = ana.spline(px, py, 100000)

        i = 0
        for e in en_list:
            if math.fabs(energy - e) < 0.0001:
                rtn_gap = round(gap_list[i], 3)
                return rtn_gap
            else:
                i += 1


if __name__ == "__main__":
    p = IDparam()
    test = [8.005, 12.3984, 12.3985, 13.50050, 15.0099]

    for en in test:
        print(p.getGap(float(en)))
