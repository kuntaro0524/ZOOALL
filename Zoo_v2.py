import os,sys,glob
import time, datetime
import numpy as np
import socket
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import logging
import logging.config

# 150722 AM4:00
# Debug: when SPACE has some troubles Zoo stops immediately

bss_srv="192.168.215.2" # BL41XU

bss_port=5555

class Zoo:
    def __init__(self,emulator=True):
        self.isConnect=False
        #self.SPACE=SPACE.SPACE()
        self.isEmu=emulator
        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("Zoo")

    def connect(self):
        self.bssr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(0,20):
            try:
                self.bssr.connect((bss_srv, bss_port))
                self.isConnect=True
                return True
            except MyException, ttt:
                print "connect: failed. %s"%ttt.args[0]
                time.sleep(20.0)
        return False

    def disconnect(self):
        time.sleep(3.0)
        if self.isConnect:
            command="put/bss/disconnect"
            self.bssr.sendall(command)
            recstr=self.bssr.recv(8000)
            print recstr
            self.bssr.close()
        return True

    def disconnectServers(self):
        query_com="put/device_server/disconnect"
        if self.isConnect==False:
            print "Connection first!"
            return False
        else:
            self.bssr.sendall(query_com)
            recstr=self.bssr.recv(8000)
            print recstr

    def connectServers(self):
        query_com="put/device_server/connect"
        if self.isConnect==False:
            print "Connection first!"
            return False
        else:
            self.bssr.sendall(query_com)
            recstr=self.bssr.recv(8000)
            print recstr

    def getSampleInformation(self):
        query_com="get/sample/information"
        if self.isConnect==False:
            print "Connection first!"
            return False
        else:
            self.bssr.sendall(query_com)
            recstr=self.bssr.recv(8000)
            self.logger.info("getSampleInformation:%s" % recstr)
        cols=recstr.split('/')[3].split('_')
        idx=0
        self.tray_list=[]
        for col in cols:
            if idx%2==0:
                self.tray_list.append(col)
            idx+=1
        #print self.tray_list
        return self.tray_list

    def mountSample(self,trayID,pinID):
        print trayID,pinID
        com="put/sample/mount_%s_%s"%(trayID,pinID)
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        try:
            self.waitSPACE()
        except MyException, ttt:
            raise MyException("mountSample: failed. %s"%ttt.args[0])

    def exchangeSample(self,trayID,pinID):
        print trayID,pinID
        com="put/sample/exchange_%s_%s"%(trayID,pinID)
        print com
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        try:
            self.waitTillReady()
        except MyException, ttt:
            raise MyException("exchangeSample: failed. %s"%ttt.args[0])

    def isMounted(self):
        com="get/sample/on_gonio"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        puck_pin=self.getSVOC_C(recstr)
        puck_char,pin_char=puck_pin.split('_')
        puck_id=puck_char
        pin_id=int(pin_char)
        if pin_id==0:
            print "Currently no pin is mounted"
            return False
        else:
            return True

    # coded for a new double arm SPACE
    def exchangePin(self, trayID, pinID):
        mount_flag = self.isMounted()
        if mount_flag == False:
            print "Currently no pin is mounted"
            self.mountSample(trayID,pinID)
            return puck_id, pin_id
        else:
            self.exchangeSample(trayID, pinID)

    def dismountSample(self,trayID,pinID):
        self.logger.info("Dismounting %s-%s" % (trayID,pinID))
        com="put/sample/unmount_%s_%s"%(trayID,pinID)
        self.logger.debug("Sending command: %s" % com)
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        self.logger.info("The 1st received string from BSS RECSTR=%s" % recstr)
        try:
            print "Entering waiting loop for SPACE..."
            self.waitSPACE()
        except MyException, ttt:
            print "Exception=",ttt
            raise MyException("mountSample: failed. %s"%ttt.args[0])

    def getCurrentPin(self):
        com="get/sample/on_gonio"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        self.logger.info("getCurrentPin.RECSTR=%s" % recstr)
        puck_pin=self.getSVOC_C(recstr)
        puck_char,pin_char = puck_pin.split('_')
        puck_id = puck_char
        pin_id = int(pin_char)
        if pin_id == 0:
            return 0,0
        else:
            return puck_id,pin_id

    def exchange(self, puck_id, pin_id):
        puck_id_prev, pin_id_prev=self.getCurrentPin()
        if pin_id_prev == 0:
            print "None is mounted"

    def dismountCurrentPin(self):
        puck_id,pin_id=self.getCurrentPin()
        self.logger.debug("dismounting the current pin %s-%s" % (puck_id, pin_id))

        if pin_id==0:
            print "Already none"
        else:
            self.logger.debug("Sending command to SPACE..")
            self.dismountSample(puck_id,pin_id)

    def cleaning(self):
        com="put/sample/cleaning"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        try:
            self.waitSPACE()
        except MyException, ttt:
            print "TTT=", ttt
            raise MyException("cleaning: failed. %s"%ttt.args[0])

    def capture(self,filename):
        command="put/video/capture_%s"%filename
        print "Capturing %s"%filename
        self.bssr.sendall(command)
        recstr=self.bssr.recv(8000)

    def getSVOC_C(self,recmes):
        ## ['measurement', 'get', '17475_pxbl_server', 'ready', '0']
        ## ready is targeto
        ## column number = 3
        cols=recmes.split("/")
        return cols[3]

    def ZoomUp(self):
        com="put/video/zoomer_1"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def ZoomDown(self):
        com="put/video/zoomer_-1"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def isBusy(self):
        if self.isConnect==False:
            print "Connection first!"
            return False
        else:
            command="get/measurement/query"
            self.bssr.sendall(command)
            recstr=self.bssr.recv(8000)
            #print "Received buffer in isBusy: %s"%recstr
            svoc_c=self.getSVOC_C(recstr)
            if svoc_c.rfind("ready")!=-1:
                print "isBusy:RECBUF=",recstr
                return False
            elif svoc_c.rfind("fail")!=-1:
                raise MyException("Something failed.")
            else:
                return True

    def doRaster(self,jobfile):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com="put/measurement/start_1_3_1_schedule_%s"%jobfile
        print com
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def waitTillReady(self):
        while (1):
            try:
                if self.isBusy():
                    print "Now busy..."
                    time.sleep(2.0)
                else:
                    break
            except MyException, ttt:
                raise MyException("waitTillReady: Some error occurred : %s"%ttt.args[0])

    def isBusy(self):
        if self.isConnect==False:
            print "Connection first!"
            return False
        else:
            command="get/measurement/query"
            self.bssr.sendall(command)
            recstr=self.bssr.recv(8000)
            #print "Received buffer in isBusy: %s"%recstr
            svoc_c=self.getSVOC_C(recstr)
            if svoc_c.rfind("ready")!=-1:
                print "isBusy:RECBUF=",recstr
                return False
            elif svoc_c.rfind("fail")!=-1:
                raise MyException("Something failed.")
            else:
                return True

    def waitSPACE(self):
        if self.isConnect==False:
            print "Connection first!"
            return False
        while (1):
            query_command = "get/measurement/query"
            self.bssr.sendall(query_command)
            recstr = self.bssr.recv(8000)
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
                error_code = recstr.split('/')[4]
                self.logger.debug("ErrorCode= %5d" % error_code)
                if error_code == '-1005000001':
                    message = "Failed to connect to the SPACE server"
                elif error_code == '-1005000002':
                    message = "Failed to get Tray ID"
                elif error_code == '-1005000003':
                    message = "Failed to mount the designated pin. (CODE=%s)" % error_code
                elif error_code == '-1005000004':
                    message = "Failed to dismount the designated pin."
                elif error_code == '-1005000005':
                    message = "Failed to get information on goniometer"
                elif error_code == '-1005000006':
                    message = "Failed in cleaning SPACE"
                elif error_code == '-1005000007':
                    message = "Failed in clearing the warning flag."
                elif error_code == '-1005100001':
                    message = "Warning!! Check existence of the designated pin.(CODE=%s)" % error_code
                elif error_code == '-1005000008':
                    message = "Failed in cleaning SPACE"
                elif error_code == '-1000000000':
                    message = "Busy for doing something. Really???"
                    self.logger.info(message)
                    self.logger.info("waiting for 2 seconds and retry...")
                    time.sleep(2.0)
                    continue
                else:
                    message = "unknown error code. (code = %s)" % error_code
                raise MyException(message)
            else:
                print "waiting..."
                time.sleep(2.0)


    def waitTillReadySeconds(self,time_thresh=1000.0):
        while (1):
            try:
                if self.isBusy():
                    print "Now busy..."
                    time.sleep(2.0)
                else:
                    break
            except MyException, ttt:
                raise MyException("Some error occurred : %s"%ttt.args[0])

    def doDataCollection(self,jobfile):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com="put/measurement/start_1_3_1_schedule_%s"%jobfile
        print "Submitting command: %s"%com
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def stop(self):
        # JOB FILE NAME MUST NOT INCLUDE "_"
        com="put/measurement/stop"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def setPhi(self,phi_abs):
        com="put/gonio_spindle/abs_%fdegree"%phi_abs
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print com

    def autoCentering(self):
        com="put/sample/autocenter"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print com

    def skipSample(self):
        com="put/sample/clear_warning"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)

    def waitTillFinish(self, query_command):
        if self.isConnect == False:
            print "Connection first!"
            return False

        while (1):
            self.bssr.sendall(query_command)
            recstr=self.bssr.recv(8000)
            print "Received buffer in isBusy: %s"%recstr
            svoc_c=self.getSVOC_C(recstr)
            if svoc_c.rfind("ready")!=-1:
                print "waitTillFinish:RECBUF=",recstr
                break
            elif svoc_c.rfind("fail")!=-1:
                raise MyException("Something failed.")
            else:
                time.sleep(2.0)
                continue

    def getBeamsize(self):
        print datetime.datetime.now()
        com = "get/beamline/beamsize"
        for i in range(0,10):
            self.bssr.sendall(com)
            recstr=self.bssr.recv(8000)
            print recstr
            cols = recstr.split('/')
            if cols[3].isdigit() == True:
                beamsize_index = int(cols[3])
                return beamsize_index
            else:
                time.sleep(1.0)
                continue
        raise MyException("getBeamsize: failed. Check beamsize.config")

    def getWavelength_old(self):
        print datetime.datetime.now()
        com = "get/beamline/wavelength"

        for i in range(0,10):
            self.bssr.sendall(com)
            recstr=self.bssr.recv(8000)
            self.logger.info("RECSTR=%s"%recstr)
            cols = recstr.split('/')
            #print cols
            if cols[3].rfind("angstrom") != -1:
                phrase = cols[3].replace("angstrom", "")
                try:
                    wavelength = round(float(phrase), 5)
                    return wavelength
                except:
                    continue
            else:
                time.sleep(1.0)
                continue
        raise MyException("getWavelength: failed. Check beamsize.config")

    def getWavelength(self):
        print datetime.datetime.now()
        com = "get/beamline/wavelength"

        while(1):
            self.bssr.sendall(com)
            recstr=self.bssr.recv(8000)
            self.logger.info("RECSTR=%s"%recstr)
            cols = recstr.split('/')
            #print cols
            if cols[3].rfind("angstrom") != -1:
                phrase = cols[3].replace("angstrom", "")
                try:
                    wavelength = round(float(phrase), 5)
                    self.logger.info("Wavelength from BSS is %8.5f A" % wavelength)
                    return wavelength
                except:
                    continue
            else:
                self.logger.info("Wavelength cannot be obtained...")
                time.sleep(2.0)
                continue
        raise MyException("getWavelength: failed. Check beamsize.config")

    def setWavelength(self, wavelength):
        com = "put/beamline/wavelength_%7.5fA" % wavelength
        query_command = "get/beamline/query"

        try:
            self.bssr.sendall(com)
            recstr=self.bssr.recv(8000)
            self.waitTillFinish(query_command)
        except:
            raise MyException("getWavelength: failed. Check beamsize.config")

    def onlyQuery(self):
        com = "get/beamline/query"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def onlySampleQuery(self):
        com = "get/sample/query"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print recstr

    def getBeamsizeQuery(self):
        com = "get/beamline/query"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print "getBeamsizeQuery.command = ",com
        print "GETBEAMSIZE=",recstr

    def setBeamsize(self, beamsize_index):
        com = "put/beamline/beamsize_%d" % beamsize_index
        #self.getBeamsizeQuery()
        print "changing"
        self.bssr.sendall(com)
        recstr=self.bssr.recv(8000)
        print "setBeamsize:result=", recstr
        self.waitTillReady()

if __name__ == "__main__":
    zoo=Zoo()
    zoo.connect()
    print zoo.getSampleInformation()

    #while(1):
    #zoo.skipSample()
    #zoo.dismountCurrPin()
    #zoo.sampleQuery()
    #zoo.stop()
    #time.sleep(10.0)
    #zoo.disconnectServers()
    #time.sleep(5.0)
    #zoo.connectServers()
    #zoo.reconnectHSserver()
    #zoo.autoCentering()
    #zoo.dismountSample("CPS1019",12)
    #print zoo.getCurrentPin()
    #zoo.skipSample()
    #zoo.dismountCurrentPin()

    #try:
    #zoo.mountSample("CPS0294",1)
    #zoo.waitTillReady()
    #except MyException, ttt:
    #print "Sample mounting failed. Contact BL staff!"
    #sys.exit(1)
    #"""

    #time.sleep(60)
    #zoo.dismountCurrentPin()
    zoo.waitTillReady()
    #try:
    #zoo.mountSample("CPS0294",1)
    #zoo.waitTillReady()
    #except MyException, ttt:
    #print "Sample mounting failed. Contact BL staff!"
    #sys.exit(1)
    #time.sleep(60)
    #zoo.dismountCurrentPin()
    #zoo.waitTillReady()
    #zoo.mountSample("CPS1968",3)
    #zoo.waitTillReady()
    #zoo.waitTillReady()
    #zoo.capture("pppp.ppm")
    #zoo.ZoomUp()
    #zoo.ZoomDown()
    #schfile="/isilon/users/target/target/Staff/kuntaro/171118-PH/PH5deg-CPS0293-11/data/multi.sch"
    #schfile="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
    #schfile="/isilon/users/target/target/Staff/ZooTest//lys07/data///lys07.sch"
    #zoo.setPhi(140.0)
    #schfile_hirata="/isilon/users/target/target/Staff/ZooTest/Schedule/test.sch"
    #schfile_yaruzo="/isilon/users/target/target/Staff/ZooTest/Schedule/yaruzo.sch"
    #time.sleep(10.0)
    #zoo.doRaster(sys.argv[1])
    #zoo.doRaster(sys.argv[1])
    #zoo.doRaster("/isilon/users/target/target/AutoUsers/160509/Xiangyu/Xi-KLaT005-01/scan/Xi-KLaT005-01.sch")
    #zoo.doDataCollection(sys.argv[1])
    #zoo.doDataCollection("/isilon/users/target/target/Staff/kuntaro/160715/Auto/KUN10-CPS1013-07/data/cry01.sch")
    #zoo.doDataCollection(schfile)
    #zoo.doDataCollection("/isilon/users/target/target/AutoUsers/kuntaro/161218/RR-test//mbeam09-CPS1716-02/data//multi.sch")
    #zoo.waitTillReady()
    zoo.disconnect()
