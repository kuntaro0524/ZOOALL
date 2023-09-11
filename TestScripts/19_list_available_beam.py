import sys, os
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")

import BeamsizeConfig

if __name__ == "__main__":
    config_dir = "/isilon/blconfig/bl32xu/"
    bsc = BeamsizeConfig.BeamsizeConfig(config_dir)
    # bsc.readConfig()
    tw, th, bs, ff = bsc.getBeamParamList()
    print("Available beam size =",len(bs))
    for b in bs:
        p, q, r = b
        print("%5d %5.1f (V) x %5.1f (H)um" % (p, r, q))
