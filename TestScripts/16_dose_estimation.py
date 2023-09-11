import sys, os, math, time, tempfile, datetime
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import Raddose

if __name__ == "__main__":
    e = Raddose.Raddose()
    en = float(sys.argv[1])

    print("Usage: python 16_dose_estimation.py ENERGY[keV] BeamH[um] BeamV[um] Flux[phs/sec]")

    beam_h = float(sys.argv[2])
    beam_v = float(sys.argv[3])
    flux = float(sys.argv[4])

    dose = e.getDose(beam_h, beam_v, flux, 1.0, energy=en)

    print("Dose = %8.3f MGy" % dose)
    #print "10 MGy exposure time = " % (10.0/dose)

    print("Raster scan exposure   0.02 sec : Dose/grid = %5.2f MGy" % (dose * 0.02))
    print("Raster scan exposure   0.01 sec : Dose/grid = %5.2f MGy" % (dose * 0.01))
    att_fac = 0.2 / (dose * 0.02) * 100.0
    print("Helical data collection : 2 times 100 kGy (200 kGy total): Trans = %5.2f percent" % att_fac)
    att_fac = att_fac / 2.0
    print("Helical data collection : 2 times  50 kGy (100 kGy total): Trans = %5.2f percent" % att_fac)
