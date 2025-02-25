import sys,math,numpy,os,socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import datetime, logging
import LoopMeasurement
import Zoo
import ESA
import DiffscanMaster

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    esa=ESA.ESA("zoo.db")
    esa_csv=sys.argv[1]
    is_renew_db=True
    esa.makeTable(esa_csv,force_to_make=is_renew_db)

    # Logging setting
    beamline = "BL32XU"
    logname = "hito.log"
    prefix = "hhhh"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    conds=esa.getDict()
    cond = conds[0]

    root_dir="/isilon/users/target/target/AutoUsers/200706/kuntaro/TEST3/"

    lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
    lm.prepDataCollection()

    phosec = 5E13
    face_angle= 130.0

    dm = DiffscanMaster.NOU(zoo, lm, face_angle, phosec)
    prefix="2d"

    scan_path = sys.argv[2]
    dc_blocks = dm.junbiSuru(scan_path, cond, prefix)

    print dc_blocks

