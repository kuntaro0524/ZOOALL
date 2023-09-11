import sys, os
import socket
import numpy as np
from scipy import interpolate

import BeamsizeConfig

if __name__ == "__main__":
    config_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
    bsc = BeamsizeConfig.BeamsizeConfig(config_dir)
    # bsc.readConfig()
    tw, th, bs, ff = bsc.getBeamParamList()

    index = 1
    logf = open("dose.dat","w")
    for b in bs:
        p, q, r = b
        flux = bsc.getFluxAtWavelength(q,r,1.0)
        flux_density = flux / q / r
        logf.write( "%5.1f x %5.1f um DENSITY=%5.2e" % (q,r,flux_density))
        dose_1sec = flux_density / 2E10 * 10.0
        logf.write( " dose_1sec= %5.2f MGy"  % ( dose_1sec))
        logf.write( " dose_0.01sec= %5.2f kGy" % (dose_1sec/100.0*1000))
        logf.write( " dose_0.02sec= %5.2f kGy\n" % (dose_1sec/50.0*1000))
