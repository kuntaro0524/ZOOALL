import sys
import socket
import time
import datetime
import math

import Device

from AttFactor import *
from File import *

if __name__ == "__main__":
    host = '172.24.242.59'

    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #port = 10101
    #s.connect((host,port))

    dev = Device.Device(host)
    dev.init()

    # Usage
    attfac = AttFactor()
    f = File("./")
    count_time = 1.0

    # prep scan
    dev.prepScan()

    # Condition
    energy = dev.mono.getE()
    wave = 12.3984 / energy

    # start,end,step
    # GAIN3: 2500-3300 pls
    # GAIN4: 1500-2500 pls
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    step = int(sys.argv[3])

    # Full flux count
    print "Attenuator is set to NONE"
    dev.att.move(0)
    ch0, ch1 = dev.simpleCountBack(1, 0, count_time, 1)
    print ch0
    maxI = float(ch0)

    idx = 0
    n_count = 1
    filename = "%03d_attenuator.dat" % (f.getNewIdx3())
    ofile = open(filename, "w")
    for pls in arange(start, end, step):  # Short measurements?
        print "Att %5d pls" % pls,
        dev.att.move(pls)
        ch0, ch1 = dev.simpleCountBack(1, 0, count_time, n_count)
        value = float(ch0)
        if value > 10.0:
            trans = value / maxI
            print "Transmission=", trans
            thick = attfac.calcThickness(wave, trans)
            ofile.write("%5d %10.5f %10.1f\n" % (pls, trans, thick))
            print"%5d %10.5f %10.1f\n" % (pls, trans, thick)
            ofile.flush()
        else:
            print "Intensity none"
            print "Skipping"
        continue
        idx += 1

    #dev.closeShutters()

    ofile.close()
    s.close()
