import sys, os
import socket

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")

import BeamsizeConfig
import Zoo

if __name__ == "__main__":
    config_dir = "/isilon/blconfig/bl32xu/"
    bsc = BeamsizeConfig.BeamsizeConfig(config_dir)
    tw, th, bs, ff = bsc.getBeamParamList()
 
    zoo = Zoo.Zoo()
    zoo.connect()

    # input beam size
    vsize = float(sys.argv[1])
    hsize = float(sys.argv[2])

    beam_index = bsc.getBeamIndexHV(hsize, vsize)

    print("Beamsize index should be %5d" % beam_index)

    zoo.setBeamsize(beam_index)
    zoo.disconnect()
