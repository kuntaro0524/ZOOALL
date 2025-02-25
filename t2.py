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
    lm.prepDataCollection(6)

    logf=open("logfile.dat","w")
    face_angle=162.0
    h2=HEBI.HEBI(zoo,lm,logf)

    left_xyz=(0.9802,-10.1597,-0.8232)
    right_xyz=(0.9822,-9.8497,-0.6872)
    ds_prefix="TEST"
    phosec_meas=9E15

    sch_file=h2.doHelical(left_xyz,right_xyz,conds[0],face_angle,ds_prefix,phosec_meas)

    #raspath="/isilon/users/target/target/Staff/kuntaro/181127-HEBITEST/HEL-01/scan00/2d/"
    #scan_id="2d"
    #h2.mainLoop(raspath,scan_id,face_angle,conds[0],precise_face_scan=True)

    #scan_prefix_2dface="2d"
    #h2.mainLoop(scan_path_2dface,scan_prefix_2dface,face_agnel)
    #print h2.anaVscan("helical_test/lv-fin-00/","lv-fin-00",0.0)
    #print h2.anaVscan("helical_test/lv-fin-00/","lv-fin-00",0.0)
    #print h2.ana2Dscan("helical_test/rface-00/","rface-00",0.0,method="right_upper")
    #print h2.ana2Dscan("helical_test/lface-00/","lface-00",0.0,method="left_lower")

    # DEBUGGIN
    
