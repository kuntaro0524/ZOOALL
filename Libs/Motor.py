import sys
import socket
import time

from Received import *
from ScanAxis import *
from Count import *


# from CounterInfo import *

class Motor(ScanAxis):
    def __init__(self, srv, motor, unit):
        # parent class
        ScanAxis.__init__(self)
        # server
        self.srv = srv
        # motor name
        self.motor = motor
        # command for query
        self.qcommand = "get/" + self.motor + "/" + "query"
        # unit
        self.unit = unit


    # String/Bytes communication via a socket
    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.srv.sendall(sending_command)
        recstr = self.srv.recv(8000)
        return repr(recstr)

    #### Moving #####
    def move(self, value):
        # in the case: pulse
        if self.unit == "pulse":
            tmpvalue = int(value)
        else:
            tmpvalue = float(value)
        # making a sending command
        strvalue = str(tmpvalue) + self.unit
        # print "Moving %s to %s" % (self.motor,strvalue)
        command = "put/" + self.motor + "/" + strvalue
        # print "COMMAND:"+command

        ######	sending move command
        tmpstr = self.communicate(command)

        while True:
            #### Get query information
            recbuf = self.communicate(self.qcommand)
            rrrr = Received(recbuf)
            if rrrr.checkQuery():
                # print "Finished: current status="+rrrr.readQuery()
                return 1
            # print "waiting"
            time.sleep(0.1)

    def nageppa(self, value):
        # in the case: pulse
        if self.unit == "pulse":
            tmpvalue = int(value)
        else:
            tmpvalue = float(value)
        # making a sending command
        strvalue = str(tmpvalue) + self.unit
        command = "put/" + self.motor + "/" + strvalue
        tmpstr = self.communicate(command)  # dummy acquisition

    def relmove(self, value):
        curr_value = self.getPosition()[0]
        final_value = curr_value + value
        self.move(final_value)

    def preset(self, value):
        # command
        com = "put/%s_preset/%d%s" % (self.motor, value, self.unit)
        recbuf = self.communicate(com)
        print(recbuf)

    def getApert(self):
        com = "get/" + self.motor + "/aperture"
        recbuf = self.communicate(com)
        tmpf = Received(recbuf)
        position = tmpf.readQuery()

        # print position
        if position.find("mm") != -1:
            value = float(position.replace("mm", ""))
            return (value, "mm")
        elif position.find("pulse") != -1:
            value = int(position.replace("pulse", ""))
            return (value, "pulse")
        elif position.find("deg") != -1:
            value = float(position.replace("deg", ""))
            return (value, "deg")
        elif position.find("um") != -1:
            value = float(position.replace("um", ""))
            return (value, "um")
        else:
            print("Unknown value")

    ##  position ####
    def getPosition(self):
        com = "get/" + self.motor + "/position"
        recbuf = self.communicate(com)
        tmpf = Received(recbuf)
        position = tmpf.readQuery()
        # print "debug::", position

        # print position
        if position.find("mm") != -1:
            value = float(position.replace("mm", ""))
            return (value, "mm")
        elif position.find("pulse") != -1:
            value = int(position.replace("pulse", ""))
            return (value, "pulse")
        elif position.find("deg") != -1:
            value = float(position.replace("deg", ""))
            return (value, "deg")
        elif position.find("um") != -1:
            value = float(position.replace("um", ""))
            return (value, "um")
        else:
            print("Unknown value")
            return (0, 0)

    def findMax(self, cnt_ch, cnt_time, sense=1):
        # Initialize Counter class
        counter = Count(self.srv, cnt_ch, 0)

        # maximum count
        maxcnt = [0] * 2
        maxval = [0] * 2

        diff = self.scan_end - self.scan_start
        ndata = int(round(diff / self.scan_step) + 1)

        # Exception 
        try:
            self.checkScanCondition()
        except MyException as ttt:
            print(ttt)
            raise ttt

        # save current position
        saved_position = list()
        saved_position = self.getPosition()

        for x in range(0, ndata):
            current_x = self.scan_start + x * self.scan_step

            if (self.unit == "pulse"):
                current_x = int(current_x)

                # print current_x,cnt_time
                self.move(current_x)
                # Counter channel
                value1, value2 = counter.getCount(cnt_time)

            print("%12.5f ch1: %12d, ch2:%12d" % (current_x, value1, value2))
            line = "12345 %12.5f %8d %8d\n" % (current_x, value1, value2)

            ## maximum count
            if maxcnt[0] < value1:
                maxcnt[0] = value1
                maxval[0] = current_x

            ## set this axis to the initial position
            self.move(saved_position[0])
        return maxcnt[0], maxval[0]

    def axisScan(self, ofile, cnt_ch, cnt_ch2, cnt_time, sense=1):

        # Initialize Counter class
        counter = Count(self.srv, cnt_ch, cnt_ch2)

        # maximum count
        maxcnt = [0] * 2
        maxval = [0] * 2

        of = file(ofile, "w")
        diff = self.scan_end - self.scan_start
        ndata = int(round(diff / self.scan_step) + 1)

        # Exception 
        try:
            self.checkScanCondition()
        except MyException as ttt:
            raise ttt

        saved_position = list()
        saved_position = self.getPosition()

        for x in range(0, ndata):
            current_x = self.scan_start + x * self.scan_step

            if (self.unit == "pulse"):
                current_x = int(current_x)

                # print current_x,cnt_time
                self.move(current_x)
                # Counter channel
                value1, value2 = counter.getCount(cnt_time)
            # value1=1
            # value2=2

            print("%12.5f ch1: %12d, ch2:%12d" % (current_x, value1, value2))
            line = "12345 %12.5f %8d %8d\n" % (current_x, value1, value2)

            ## maximum count
            if maxcnt[0] < value1:
                maxcnt[0] = value1
                maxval[0] = current_x
                # print "1:FIND!!! MAXVALUE="+str(maxcnt[0])+" "+str(maxval[0])
            if maxcnt[1] < value1:
                maxcnt[1] = value1
                maxval[1] = current_x
                # print "2:FIND!!! MAXVALUE="+str(maxcnt[0])+" "+str(maxval[0])

            of.write(line)

        of.close()
        ## set this axis to the initial position
        print("%5d%s" % (saved_position[0], saved_position[1]))
        self.move(saved_position[0])
        return maxval

    def query(self):
        recbuf = self.communicate(self.qcommand)
        rrrr = Received(recbuf)
        return rrrr.readQuery()

    def isMoved(self):
        recbuf = self.communicate(self.qcommand)
        rrrr = Received(recbuf)
        return rrrr.checkQuery()

    def moveGravity(self, outfile):
        ana = AnalyzeData(outfile)
        grav = int(ana.analyze(1, 2, "gauss")[1])

        self.move(grav)

    def moveFWHMcenter(self, outfile):
        ana = AnalyzeData(outfile)
        fwhm_center = int(ana.analyze(1, 2, "peak")[1])

        self.move(fwhm_center)

    ### For Monochromator only

    def getEnergy(self):
        # recbuf = self.communicate(self.qcommand)
        com = "get/" + self.motor + "/energy"
        recbuf = self.communicate(com)

        rrrr = Received(recbuf)
        position = rrrr.readQuery()

        if position.find("kev") != -1:
            value = float(position.replace("kev", ""))
            return (value, "kev")
        else:
            print("Unknown value")
            print(position)
            return (NULL, NULL)

    def getRamda(self):
        com = "get/" + self.motor + "/wavelength"
        recbuf = self.communicate(self.qcommand)
        tmpf = Received(recbuf)
        position = tmpf.readQuery()

        if position.find("angstrome") != -1:
            value = float(position.replace("angstrome", ""))
            return (value, "angstrome")
        else:
            print("Unknown value")
            return (NULL, NULL)

    def getAngle(self):
        com = "get/" + self.motor + "/angle"
        recbuf = self.communicate(com)
        tmpf = Received(recbuf)
        position = tmpf.readQuery()

        if position.find("degree") != -1:
            value = float(position.replace("degree", ""))
            return (value, "degree")
        else:
            print("Unknown value")
            return (NULL, NULL)


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    axis = "bl_32in_tc1_stmono_1_dtheta1"

    s.connect((host, port))

    test = Motor(s, axis, "pulse")

    time1 = datetime.datetime.now()
    print(time1)
    print(test.move(-89000))
    print(test.move(-87000))
    time2 = datetime.datetime.now()
    print(time2)

    print("Time: %8.5f sec" % (time2 - time1).seconds)

    print(test.move(-89000))
