import sys, os, math, time, tempfile, datetime
import Raddose

if __name__ == "__main__":
    e = Raddose.Raddose()
    #6-30keV
    import numpy as np
    en_list = np.arange(6.0, 50.0, 0.5)

    ofile = open("dose_oxi.txt", "w")
    for en in en_list:
        dddd=e.getDose1sec(1.0, 1.0, 1.0, energy=en,sample="oxi")
        ppp = 10.0 / dddd
        ofile.write("%8.1f,%8.5e,%8.5e\n" % (en, dddd,ppp))
    ofile.close()
