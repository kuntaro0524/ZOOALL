import os,sys,math,numpy,socket,datetime
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS

if __name__ == "__main__":
        blanc = '172.24.242.41'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))

        gonio=Gonio.Gonio(s)
        bs=BS.BS(s)
        inocc=IboINOCC.IboINOCC(gonio)

        starttime=datetime.datetime.now()
        # Recover Face angle
        bs.evacLargeHolder()
        inocc.recoverFaceAngle()

        # Precise facing
        inocc.rotateToFace()

        #inocc.translateToCenter()
        #inocc.translateToCenterROI()
        endtime=datetime.datetime.now()
        time_sec= (endtime-starttime).seconds

	print time_sec,"sec"
