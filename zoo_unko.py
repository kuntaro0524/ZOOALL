import sys,math,numpy,os
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import Zoo
import ZooNavigator
import socket

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    esa_csv=sys.argv[1]

    navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=True)
    navi.goAround()
    zoo.disconnect()
    ms.close()
