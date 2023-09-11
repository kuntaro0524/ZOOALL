import sys,math,numpy,os,socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import datetime
import LoopMeasurement
import Zoo
import MyException
import AnaHeatmap
import CrystalList
import KUMA
import ESA
import HEBI


if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    esa=ESA.ESA("zoo.db")
    esa_csv="181127-hel.csv"
    is_renew_db=True
    esa.makeTable("zoo.db",esa_csv,force_to_make=is_renew_db)
    conds=esa.getDict()
    #return self.conds

    root_dir="/isilon/users/target/target/Staff/kuntaro/181127-HEBITEST/"
    prefix="TEST"
    lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
    lm.prepDataCollection(5)

    logf=open("logfile.dat","w")
    face_angle=162.0
    h2=HEBI.HEBI(zoo,lm,logf)
    raspath="/isilon/users/target/target/Staff/kuntaro/181127-HEBITEST/HEL-01/scan00/2d/"
    scan_id="2d"
    h2.mainLoop(raspath,scan_id,face_angle,conds[0],precise_face_scan=True)