import sys, os, math, socket, time
import numpy as np
import datetime

import LoopMeasurement

if __name__ == "__main__":
    import ESA

    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.54", 10101))

    # ESA
    esa = ESA.ESA("./zoo.db")
    esa.makeTable(sys.argv[1])
    ppp = esa.getDict()


    root_dir = "/isilon/users/admin41/admin41/220329_ZOOtest/002/data"

    cxyz = [-1.89489, -2.8889, -0.17120]
    phi = 0.00
    scan_id = "test01"
    trayid = 1
    pinid = 10
    beamsize = 10.0

    lm = LoopMeasurement.LoopMeasurement(ms, root_dir, scan_id)
    lm.prepDataCollection()

    wavelength = 0.9
    startphi = 0.0
    endphi = 90.0
    osc_width = 0.1
    flux = 8E13

    # BL41XU TEST
    center_xyz = [-1.89,-2.88,-0.17]
    prefix = "TEST"

    scanv_um = 100.0
    scanh_um = 150.0
    vstep_um = 10.0
    hstep_um = 15.0

    raster_schedule, raster_path = lm.rasterMaster("scanscan", "2D", center_xyz,
                                                            scanv_um, scanh_um, vstep_um, hstep_um,
                                                            startphi, ppp[0])

    print(raster_schedule)

    ms.close()
