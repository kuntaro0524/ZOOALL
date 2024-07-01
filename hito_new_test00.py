import sys,math,numpy,os,socket
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import DiffscanMaster

if __name__ == "__main__":
    zoo=1
    lm=2
    face_angle = 90.0
    phosec=1E12

    dm = DiffscanMaster.NOU(zoo, lm, face_angle, phosec)
    prefix="2d"
    cond={'score_min':20, 'score_max': 100, 'maxhits':10, 'raster_hbeam':20.0}
    dc_blocks = dm.junbiSuru(sys.argv[1], cond, prefix)
    print dc_blocks
