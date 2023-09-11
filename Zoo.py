import os, sys, glob
import time, datetime
import numpy as np
import socket

from MyException import *
import logging
import logging.config
from configparser import ConfigParser, ExtendedInterpolation

# 150722 AM4:00
# Debug: when SPACE has some troubles Zoo stops immediately

class Zoo:
    def __init__(self, emulator=True):
        # Get information from beamline.ini file.
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path="%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        config.read(config_path)

        self.bss_srv=config.get("server", "bss_server")
        self.bss_port=config.getint("server", "bss_port")

        self.isConnect = False
        self.isEmu = emulator
        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("Zoo")

        # Wait option
        self.wait_flag = True

    # String to bytes
    def communicate(self, comstr):
        sending_command = comstr.encode()
        # print(sending_command)
        if self.isConnect == False:
            print("Connection first!")
            return False
        else:
            self.bssr.sendall(sending_command)
            recstr = self.bssr.recv(8000)

            return repr(recstr)

    def connect(self):
        self.bssr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(0, 20):
            try:
                self.bssr.connect((self.bss_srv, self.bss_port))
                self.isConnect = True
                return True
            except MyException as ttt:
                print("connect: failed. %s" % ttt.args[0])
                time.sleep(20.0)
        return False

    def disconnect(self):
        time.sleep(3.0)
        if self.isConnect:
            command = "put/bss/disconnect"
            recstr = self.communicate(command)
            # print(recstr)
            self.bssr.close()
        return True

    def disconnectServers(self):
        query_com = "put/device_server/disconnect"
        if self.isConnect == False:
            print("Connection first!")
            return False
        else:
            recstr = self.communicate(query_com)
            print(recstr)

    def connectServers(self):
        query_com = "put/device_server/connect"
        if self.isConnect == False:
            print("Connection first!")
            return False
        else:
            recstr = self.communicate(query_com)
            print(recstr)

    def getSampleInformation(self):
        query_com = "get/sample/information"
        recstr = self.communicate(query_com)
        self.logger.info("getSampleInformation:%s" % recstr)
        cols = recstr.split('/')[3].split('_')
        idx = 0
        self.tray_list = []
        for col in cols:
            if idx % 2 == 0:
                self.tray_list.append(col)
            idx += 1

        return self.tray_list

    def mountSample(self, trayID, pinID):
        self.logger.debug("--Starting--")
        com = "put/sample/mount_%s_%s" % (trayID, pinID)
        recstr = self.communicate(com)
        try:
            # 210415 K.Hirata (strange answer from BSS)
            if self.wait_flag: time.sleep(0.5)
            self.waitSPACE()
        except MyException as ttt:
            self.logger.info("Received message=%s" % ttt)
            message = ttt.args[0]
            raise MyException(ttt.args[0])

    def exchangeSample(self, trayID, pinID):
        # print(trayID, pinID)
        com = "put/sample/exchange_%s_%s" % (trayID, pinID)
        recstr = self.communicate(com)
        try:
            self.waitTillReady()
        except MyException as ttt:
            raise MyException("exchangeSample: failed. %s" % ttt.args[0])

    def isMounted(self):
        com = "get/sample/on_gonio"
        recstr = self.communicate(com)
        puck_pin = self.getSVOC_C(recstr)
        puck_char, pin_char = puck_pin.split('_')
        puck_id = puck_char
        pin_id = int(pin_char)
        if pin_id == 0:
            print("Currently no pin is mounted")
            return False
        else:
            return True

    # coded for a new double arm SPACE
    def exchangePin(self, trayID, pinID):
        mount_flag = self.isMounted()
        if mount_flag == False:
            print("Currently no pin is mounted")
            self.mountSample(trayID, pinID)
            return puck_id, pin_id
        else:
            self.exchangeSample(trayID, pinID)

    def dismountSample(self, trayID, pinID):
        self.logger.info("Dismounting %s-%s" % (trayID, pinID))
        com = "put/sample/unmount_%s_%s" % (trayID, pinID)
        recstr = self.communicate(com)
        self.logger.info("The 1st received string from BSS RECSTR=%s" % recstr)
        try:
            # 210415 K.Hirata (strange answer from BSS)
            if self.wait_flag: time.sleep(0.5)
            print("Entering waiting loop for SPACE...")
            self.waitSPACE()
        except MyException as ttt:
            raise MyException("mountSample: failed. %s" % ttt.args[0])

    def getCurrentPin(self):
        com = "get/sample/on_gonio"
        recstr = self.communicate(com)
        self.logger.info("getCurrentPin.RECSTR=%s" % recstr)
        if recstr.rfind("fail") != -1:
            self.logger.info("Something failed to get current pin")
            error_code = recstr.split('/')[-1]
            self.logger.info("Error code = %s" % error_code)
            if int(error_code) == -1005000009:
                self.logger.error("SPACE server does not know current pin information")
                raise MyException("SPACE server does not know the current pin information")

        puck_pin = self.getSVOC_C(recstr)
        puck_char, pin_char = puck_pin.split('_')
        puck_id = puck_char
        pin_id = int(pin_char)
        if pin_id == 0:
            return 0, 0
        else:
            return puck_id, pin_id

    def exchange(self, puck_id, pin_id):
        puck_id_prev, pin_id_prev = self.getCurrentPin()
        if pin_id_prev == 0:
            print("None is mounted")

    def dismountCurrentPin(self):
        puck_id, pin_id = self.getCurrentPin()
        self.logger.debug("dismounting the current pin %s-%s" % (puck_id, pin_id))

        if pin_id == 0:
            print("Already none")
        else:
            self.logger.debug("sendall command to SPACE..")
            self.dismountSample(puck_id, pin_id)

    def cleaning(self):
        com = "put/sample/cleaning"
        recstr = self.communicate(com)
        try:
            # 210415 K.Hirata (strange answer from BSS)
            if self.wait_flag: time.sleep(0.5)
            self.waitSPACE()
        except MyException as ttt:
            print("TTT=", ttt)
            raise MyException("cleaning: failed. %s" % ttt.args[0])

    def capture(self, filename):
        command = "put/video/capture_%s" % filename
        print("Capturing %s" % filename)
        recstr = self.communicate(command)

    def getSVOC_C(self, recmes):
        ## ['measurement', 'get', '17475_pxbl_server', 'ready', '0']
        ## ready is targeto
        ## column number = 3
        cols = recmes.split("/")
        return cols[3]

    def ZoomUp(self):
        com = "put/video/zoomer_1"
        recstr = self.communicate(com)

    def ZoomDown(self):
        com = "put/video/zoomer_-1"
        recstr = self.communicate(com)
        print(recstr)

    def isBusy(self):
        if self.isConnect == False:
            print("Connection first!")
            return False
        else:
            command = "get/measurement/query"
            recstr = self.communicate(command)
            svoc_c = self.getSVOC_C(recstr)
            if svoc_c.rfind("ready") != -1:
                print("isBusy:RECBUF=", recstr)
                return False
            elif svoc_c.rfind("fail") != -1:
                raise MyException("Something failed.")
            else:
                return True

    def doRaster(self, jobfile):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com = "put/measurement/start_1_3_1_schedule_%s" % jobfile
        recstr = self.communicate(com)
        self.logger.debug("a received message: %s" % recstr)

    def waitTillReady(self):
        while (1):
            try:
                if self.isBusy():
                    print("Now busy...")
                    time.sleep(2.0)
                else:
                    break
            except MyException as ttt:
                raise MyException("waitTillReady: Some error occurred : %s" % ttt.args[0])

    def isBusy(self):
        if self.isConnect == False:
            print("Connection first!")
            return False
        else:
            command = "get/measurement/query"
            recstr = self.communicate(command)
            svoc_c = self.getSVOC_C(recstr)
            if svoc_c.rfind("ready") != -1:
                print("isBusy:RECBUF=", recstr)
                return False
            elif svoc_c.rfind("fail") != -1:
                raise MyException("Something failed.")
            else:
                return True

    def waitSPACE(self):
        self.logger.debug("waiting SPACE processing...")
        if self.isConnect == False:
            print("Connection first!")
            return False
        while (1):
            query_command = "get/measurement/query"
            recstr = self.communicate(query_command)
            self.logger.debug("Sent command= %s" % query_command)
            self.logger.debug("Received buffer = %s" % recstr)
            # print "Received buffer in isBusy: %s"%recstr
            svoc_c = self.getSVOC_C(recstr)
            if svoc_c.rfind("ready") != -1:
                self.logger.debug("Ready was detected= %s" % recstr)
                self.logger.info("SPACE has finished the job.")
                break
            elif svoc_c.rfind("fail") != -1:
                self.logger.debug("'fail' was detected RECBUF3= %s" % recstr)
                # Suddenly, this code is required for processing error from SPACE.
                # 2023/06/08 A log string includes a special characeter "'" in 
                # error code "-1005100001" like "-100510001'".
                # Then the next line is required to get rid of "'" from the string.
                recstr = recstr.replace('\'','')
                error_code = int(recstr.split('/')[4])
                self.logger.debug("ErrorCode= %5d" % error_code)
                if error_code == -1005000001:
                    message = "Failed to connect to the SPACE server"
                elif error_code == -1005000002:
                    message = "Failed to get Tray ID"
                elif error_code == -1005000003:
                    message = "Failed to mount the designated pin. CODE:%s" % error_code
                elif error_code == -1005000004:
                    message = "Failed to dismount the designated pin."
                elif error_code == -1005000005:
                    message = "Failed to get information on goniometer"
                elif error_code == -1005000006:
                    message = "Failed in cleaning SPACE"
                elif error_code == -1005000007:
                    message = "Failed in clearing the warning flag."
                elif error_code == -1005100001:
                    message = "Warning!! Check existence of the designated pin. CODE:%s" % error_code
                elif error_code == -1005000008:
                    message = "Failed in cleaning SPACE"
                elif error_code == -1000000000:
                    message = "Busy for doing something. Really???"
                    self.logger.info(message)
                    self.logger.info("waiting for 2 seconds and retry...")
                    time.sleep(2.0)
                    continue
                else:
                    message = "unknown error code. (code = %s)" % error_code
                self.logger.error(message)
                raise MyException(message)
            else:
                print("waiting...")
                time.sleep(5.0)

    def waitTillReadySeconds(self, time_thresh=1000.0):
        while (1):
            try:
                if self.isBusy():
                    print("Now busy...")
                    time.sleep(2.0)
                else:
                    break
            except MyException as ttt:
                raise MyException("Some error occurred : %s" % ttt.args[0])

    def doDataCollection(self, jobfile):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com = "put/measurement/start_1_3_1_schedule_%s" % jobfile
        print("Submitting command: %s" % com)
        recstr = self.communicate(com)
        print(recstr)

    def stop(self):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com = "put/measurement/stop"
        recstr = self.communicate(com)

    def setPhi(self, phi_abs):
        com = "put/gonio_spindle/abs_%fdegree" % phi_abs
        recstr = self.communicate(com)

    def autoCentering(self):
        com = "put/sample/autocenter"
        recstr = self.communicate(com)

    def skipSample(self):
        com = "put/sample/clear_warning"
        recstr = self.communicate(com)
        self.logger.debug("recstr = %s" % recstr)

    def waitTillFinish(self, query_command):
        if self.isConnect == False:
            print("Connection first!")
            return False

        while (1):
            recstr = self.communicate(query_command)
            # print "Received buffer in isBusy: %s"%recstr
            svoc_c = self.getSVOC_C(recstr)
            if svoc_c.rfind("ready") != -1:
                # print "waitTillFinish:RECBUF=",recstr
                break
            elif svoc_c.rfind("fail") != -1:
                raise MyException("Something failed.")
            else:
                time.sleep(2.0)
                continue

    def getBeamsize(self):
        # wait a bit
        self.logger.info("Waiting loop for debugging. 1.0 sec...")
        time.sleep(1.0)

        self.logger.info("getting beam size from BSS.")
        com = "get/beamline/beamsize"
        for i in range(0, 10):
            self.logger.info("sendall command: %s" % com)
            self.logger.info("waiting for a reply")
            recstr = self.communicate(com)
            self.logger.info("received log: %s" % recstr)

            cols = recstr.split('/')
            if cols[3].isdigit() == True:
                beamsize_index = int(cols[3])
                return beamsize_index
            else:
                time.sleep(1.0)
                self.logger.info("Go to the next loop...")

                continue
        raise MyException("getBeamsize: failed. Check beamsize.config")

    def getWavelength(self):
        self.logger.info("getting wavelength from BSS.")

        com = "get/beamline/wavelength"

        # wait a bit
        self.logger.info("Waiting loop for debugging. 1.0 sec...")
        time.sleep(1.0)
        # Reset recstr
        recstr = ""

        while (1):
            self.logger.info("sendall command: %s" % com)
            recstr = self.communicate(com)
            self.logger.info("received message: %s" % recstr)
            cols = recstr.split('/')
            # print cols
            if cols[3].rfind("angstrom") != -1:
                phrase = cols[3].replace("angstrom", "")
                try:
                    wavelength = round(float(phrase), 5)
                    self.logger.info("Wavelength from BSS is %8.5f A" % wavelength)
                    return float(wavelength)
                except:
                    continue
            else:
                self.logger.info("Wavelength cannot be obtained...")
                self.logger.info("Go to the next loop...")
                time.sleep(2.0)
                continue
        raise MyException("getWavelength: failed. Check beamsize.config")

    def setWavelength(self, wavelength):
        com = "put/beamline/wavelength_%7.5fA" % wavelength
        query_command = "get/beamline/query"

        try:
            recstr = self.communicate(com)
            self.waitTillFinish(query_command)
        except:
            raise MyException("getWavelength: failed. Check beamsize.config")

    def onlyQuery(self):
        com = "get/beamline/query"
        self.bssr.sendall(com)
        recstr = self.communicate(com)
        # print(recstr)

    def onlySampleQuery(self):
        com = "get/sample/query"
        recstr = self.communicate(com)
        # print(recstr)

    def getBeamsizeQuery(self):
        com = "get/beamline/query"
        recstr = self.communicate(com)
        print("getBeamsizeQuery.command = ", com)
        print("GETBEAMSIZE=", recstr)

    def setBeamsize(self, beamsize_index):
        com = "put/beamline/beamsize_%d" % beamsize_index
        recstr = self.communicate(com)
        print("setBeamsize:result=", recstr)
        self.waitTillReady()


if __name__ == "__main__":
    # Logging setting

    logname = "./temp.log"
    beamline = "BL32XU"
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline,
                              defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo = Zoo()
    zoo.connect()
    print(zoo.getSampleInformation())
    # print zoo.getWavelength()
    # print zoo.getBeamsize()

    print(zoo.getCurrentPin())

    # while(1):
    zoo.skipSample()
    # zoo.dismountCurrPin()
    # zoo.sampleQuery()
    # zoo.stop()
    # time.sleep(10.0)
    # zoo.disconnectServers()
    # time.sleep(5.0)
    # zoo.connectServers()
    # zoo.reconnectHSserver()
    # zoo.autoCentering()
    # zoo.dismountSample("CPS1019",12)
    # print zoo.getCurrentPin()
    # zoo.skipSample()
    # zoo.dismountCurrentPin()

    # try:
    # zoo.mountSample("CPS0294",1)
    # zoo.waitTillReady()
    # except MyException, ttt:
    # print "Sample mounting failed. Contact BL staff!"
    # sys.exit(1)
    # """

    # time.sleep(60)
    # zoo.dismountCurrentPin()
    zoo.waitTillReady()
    # try:
    # zoo.mountSample("CPS0294",1)
    # zoo.waitTillReady()
    # except MyException, ttt:
    # print "Sample mounting failed. Contact BL staff!"
    # sys.exit(1)
    # time.sleep(60)
    # zoo.dismountCurrentPin()
    # zoo.waitTillReady()
    # zoo.mountSample("CPS1968",3)
    # zoo.waitTillReady()
    # zoo.waitTillReady()
    # zoo.capture("pppp.ppm")
    # zoo.ZoomUp()
    # zoo.ZoomDown()
    # schfile="/isilon/users/target/target/Staff/kuntaro/171118-PH/PH5deg-CPS0293-11/data/multi.sch"
    # schfile="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
    # schfile="/isilon/users/target/target/Staff/ZooTest//lys07/data///lys07.sch"
    # zoo.setPhi(140.0)
    # schfile_hirata="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
    # schfile_yaruzo="/isilon/users/target/target/Staff/ZooTest/Schedule/yaruzo.sch"
    # time.sleep(10.0)
    # zoo.doRaster(sys.argv[1])
    # zoo.doRaster(sys.argv[1])
    # zoo.doRaster("/isilon/users/target/target/AutoUsers/160509/Xiangyu/Xi-KLaT005-01/scan/Xi-KLaT005-01.sch")
    # zoo.doDataCollection(sys.argv[1])
    # zoo.doDataCollection("/isilon/users/target/target/Staff/kuntaro/160715/Auto/KUN10-CPS1013-07/data/cry01.sch")
    # zoo.doDataCollection(schfile)
    # zoo.doDataCollection("/isilon/users/target/target/AutoUsers/kuntaro/161218/RR-test//mbeam09-CPS1716-02/data//multi.sch")
    # zoo.waitTillReady()
    zoo.disconnect()
