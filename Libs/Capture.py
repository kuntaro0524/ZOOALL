#!/bin/env python 
import errno
import sys
import socket
import time
import datetime
import os
import numpy
from socket import error as socket_error
from MyException import *
from configparser import ConfigParser, ExtendedInterpolation


class Capture:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 10101
        self.open_sig = False  # network connection to videoserv
        self.isPrep = False
        self.user = os.environ["USER"]
        self.isDark = False

        # Read configure file
        # Get information from beamline.ini file.
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path="%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        print(config_path)
        self.config.read(config_path)

        self.contrast_default=self.config.getint("capture", "contrast_default")
        self.bright_default=self.config.getint("capture", "bright_default")
        self.gain_default=self.config.getint("capture", "gain_default")

        # Dark experiment
        # beamline.ini has a flag for dark experiment
        # If it is True, the default bright and gain values are changed
        # section: "special_setting", option: "isDark", value type: boolean
        self.isDark = self.config.getboolean("special_setting", "isDark")

        if self.isDark == True:
            self.bright_default = self.config.getint("capture","bright_default_dark")
            self.gain_default = self.config.getint("capture", "gain_default_dark")

        # Command for BL45XU
        # VIDEOSRV name for searching process via 'ps'
        self.videosrv = "videosrv"
        # Is videosrv running?"
        self.check_running = "ps -el > ./tmp"
        # Kill command
        self.kill_com = "killall videosrv"
        # Start command
        # BL32XU previous
        # self.start_com = "videosrv --v4l2 &"
        # BL32XU 2020.09.25 CCD camera of coax-camera is replaced.
        self.start_com = "/usr/local/bss/videosrv3 --load_json=/blconfig/video/vg51/vg51.json --grab_mode opencv &"

    # String to bytes
    def communicate(self, comstr):
        sending_command = comstr.encode()
        print(sending_command)
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    # modified on 2023/05/08
    def setDark_tobo_obsoleted(self):
        self.isDark = True
        self.bright_default = self.config.get("capture","bright_default_dark")
        self.gain_default = self.config.get("capture", "gain_default_dark")

        # Set brightness 190418
        self.setBright(self.bright_default)
        # Set contrast 190418
        self.setContrast(self.contrast_default)
        # Set gain 201002
        self.setGain(self.gain_default)

    def prep(self):
        if self.open_sig == True:
            print("SDFDSFSDFSDFSDFSDFSDFSDFSDFDSFSDFSDFSDFSDFSDFSDF")
            self.isPrep = True
            # Set brightness 190418
            self.setBright(self.bright_default)
            # Set contrast 190418
            self.setContrast(self.contrast_default)
            # Set gain 201002
            self.setGain(self.gain_default)
            time.sleep(0.2)
            return True
        # Connection failed
        else:
            # while(1):
            #     if self.checkRunning(): break
            #     else:
            #         self.start_com
            while (1):
                isConnect = self.connect()
                if isConnect == True:
                    self.isPrep = True
                    # Set brightness 190418
                    self.setBright(self.bright_default)
                    # Set contrast 190418
                    self.setContrast(self.contrast_default)
                    # Set gain 201002
                    self.setGain(self.gain_default)
                    time.sleep(0.2)
                    return True
                else:
                    self.restartVideoSrv()
                    time.sleep(3.0)

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.host, self.port))
            self.open_sig = True
        except socket_error as serr:
            return False
        return True

    def checkRunning(self):
        os.system(self.check_running)
        lines = open("./tmp", "r").readlines()

        for line in lines:
            print(("searching %s" % self.videosrv))
            if line.rfind(self.videosrv) != -1:
                return True
        return False

    def restartVideoSrv(self):
        # Kill videosrv
        os.system(self.kill_com)
        os.system(self.start_com)

    def disconnect(self):
        if self.open_sig == True:
            self.open_sig = False
            self.isPrep = False
            print("Closing the port...")
            self.s.close()

    def setBright(self, bright=40000):
        # set brightness
        com_bright = "put/video_brightness/%d" % bright
        recbuf = self.communicate(com_bright)
        print("setBright:", recbuf)

    def setCross(self):
        com1 = "put/video_cross/on"
        recbuf = self.communicate(com1)

    def unsetCross(self):
        com1 = "put/video_cross/off"
        recbuf = self.communicate(com1)
        print(recbuf)

    def setContrast(self, contrast):
        com1 = "put/video_contrast/%d" % contrast
        recbuf = self.communicate(com1)
        print("setContrast:", recbuf)

    def setGain(self, gain):
        com1 = "put/video_color/%d" % gain
        recbuf = self.communicate(com1)
        print("setGain:", recbuf)

    # Quick capture : 190419
    # def capture(self, filename, speed=150, cross=False):
    # speed is not required except for BL32XU, probablly. K. Hirata 190419
    def capture(self, filename, speed=150, cross=False):
        if self.isPrep == False:
            print("Preparation is called from capture function")
            self.prep()

        # Unset cross
        if cross == False:
            self.unsetCross()
        else:
            self.setCross()
        com1 = "get/video_grab/%s" % filename
        print(com1)
        try:
            recbuf = self.communicate(com1)
        except socket.error as e:
            raise MyException("capture failed!")

    def setShutterSpeed(self, speed):
        """ for BL32XU only
        command="ssh -l %s %s \"echo %d > /sys/class/video4linux/video0/shutter_width\""%(self.user,self.host,speed)
        os.system(command)
        """
        print("BL41XU skipped")

    def setBinning(self, binning):
        """
        if self.isPrep==0:
            self.prep()
        if self.open_sig==0:
            while (1):
                if self.connect()==True:
                    break
                else:
                    print "Retry Connection"
                    time.sleep(5)

        com1="put/video_prompt/on"
        self.s.sendall(com1)
        recbuf=self.s.recv(8000)
        #print "debug::",recbuf
        com1="put/video_binning/%d"%binning
        self.s.sendall(com1)
        recbuf=self.s.recv(8000)
        #print "debug::",recbuf
        """
        print("BL41XU skipped")

    def getBinning(self):
        if self.isPrep == False:
            self.prep()
        if self.open_sig == False:
            while (1):
                if self.connect() == True:
                    break
                else:
                    print("Retry Connection")
                    time.sleep(5)

        com1 = "get/video_binning/"
        recbuf = self.communicate(com1)
        print("debug::", recbuf)
        sp = recbuf.split("/")
        if len(sp) == 5:
            return int(sp[-2])


if __name__ == "__main__":
    cap = Capture()
    # cappath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/"
    cappath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages"
    # cappath = "/isilon/users/target/target/"

    print("START-connect from main")
    # print cap.checkRunning()

    # cap.setGain(1500)
    # print "END  -connect from main"
    filename = os.path.join(cappath, "%s.ppm" % (sys.argv[1]))
    cap.capture(filename)
