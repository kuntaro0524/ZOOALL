import sys,math,numpy,os
<<<<<<< HEAD
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
=======
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
>>>>>>> zoo45xu/main
import Zoo
import ZooNavigator
import socket

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
<<<<<<< HEAD
    ms.connect(("172.24.242.41", 10101))
=======
    ms.connect(("172.24.242.59", 10101))
>>>>>>> zoo45xu/main
    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.skipSample()
    ms.close()
