import sys
import socket
import time
from Received import *
from Motor import *
from IDparam import *


class ID:
    def __init__(self, srv):
        self.srv = srv  # server
        self.id = Motor(srv, "bl_32in_id_gap", "mm")

    def getGap(self):
        return self.id.getPosition()[0]

    def getE(self, energy):
        return IDparam().getGap(energy)

    def getGapAtE(self, energy):
        return IDparam().getGap(energy)

    def moveE(self, energy):
        gap = IDparam().getGap(energy)
        if gap < 7.4:
            print("Gap should be set more than 7.4mm")
            print("In this time, 7.4mm is set to ID")
            gap = 7.4
        # print gap
        self.move(gap)

    def isLocked(self):
        qcommand = "get/bl_32in_id_gap/query"
        self.srv.sendall(qcommand)
        recbuf = self.srv.recv(8000)
        print(recbuf)
        bufs = recbuf.split('/')
        buf = bufs[len(bufs) - 2]
        cols = buf.split('_')
        # print cols
        if cols[0] == "fail":
            return 2
        elif cols[0] == "locked":
            return 1
        else:
            return 0

    # recbuf="bl_32in_id_gap/get/27354_blrs_bladmin_bl32aws/locked_44.999000mm/0"

    def move(self, gap):
        # float gap -> yuukou suuji 3 keta
        gap = float(str("%8.3f" % gap))
        self.id.move(gap - 0.01)
        # Constructer
        for x in range(1, 10):
            self.id.move(gap)
            current_value = float(self.id.getPosition()[0])
            time.sleep(0.1)

            if current_value == gap:
                return 1
            print("current value=%8.3f" % current_value)

    def tune(self, start, end, width, channel, time, ofile):
        maxvalue = -99999
        maxgap = 0.0

        of = open(ofile, "w")

        ndata = int((end - start) / width) + 1

        if ndata < 1:
            print("Abort!!!")
            sys.exit()

        for n in range(0, ndata):
            current = start + float(n) * width
            current = float(str("%8.4f" % current))

            if current < 7.4 or current > 45.0:
                print("Abort!!")
                sys.exit()

            print("moving %8.3f \n" % current)
            self.move(current)
            count = self.id.getCount(channel, time)
            if count > maxvalue:
                maxvalue = count
                maxgap = current

            of.write("12345 %12.5f %12d\n" % (current, count))

        of.close()
        return maxgap

    def findPeak(self, energy, prefix, cnt_ch):

        file1 = prefix + "_coarse_id.scn"
        file2 = prefix + "_fine_id.scn"
        file3 = prefix + "_superfine_id.scn"

        center = self.getE(energy)
        start = float(center) - 0.5
        end = float(center) + 0.5
        print("ID scan range %8.5f - %8.5f\n" % (start, end))
        max = self.tune(start, end, 0.1, cnt_ch, 0.2, file1)
        print("MAX:%12.5f\n" % max)

        # fine tune
        center = max
        start = float(center) - 0.1
        end = float(center) + 0.1

        max = self.tune(start, end, 0.005, cnt_ch, 0.2, file2)
        print("MAX:%12.5f\n" % max)

        # ultra fine tune
        center = max
        start = float(center) - 0.01
        end = float(center) + 0.01
        max = self.tune(start, end, 0.001, cnt_ch, 0.2, file3)
        print("MAX:%12.5f\n" % max)

        self.move(max)

    def findPeakLowEnergy(self, energy, prefix, cnt_ch):

        file1 = prefix + "_coarse_id.scn"
        file2 = prefix + "_fine_id.scn"
        file3 = prefix + "_superfine_id.scn"

        center = self.getE(energy)

        start = float(center) - 0.5
        if start < 7.4:
            start = 7.4

        end = float(center) + 0.5
        print("ID scan range %8.5f - %8.5f\n" % (start, end))
        max = self.tune(start, end, 0.1, cnt_ch, 0.2, file1)
        print("MAX:%12.5f\n" % max)

        # fine tune
        center = max
        start = float(center) - 0.1

        if start < 7.4:
            start = 7.4

        end = float(center) + 0.1

        max = self.tune(start, end, 0.005, cnt_ch, 0.2, file2)
        print("MAX:%12.5f\n" % max)

        # ultra fine tune
        center = max
        start = float(center) - 0.01
        if start < 7.4:
            start = 7.4

        end = float(center) + 0.01
        max = self.tune(start, end, 0.001, cnt_ch, 0.2, file3)
        print("MAX:%12.5f\n" % max)

        self.move(max)

    def scanID(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # Setting
        ofile = prefix + "_id.scn"

        # Condition
        self.id.setStart(start)
        self.id.setEnd(end)
        self.id.setStep(step)

        maxval = self.id.axisScan(ofile, cnt_ch1, cnt_ch2, time)

        return maxval

    def moveTillMove(self, gap, wait_interval=300, ntrial=150):
        for i in range(0, ntrial):
            if self.isLocked() == 1 or self.isLocked() == 2:
                tstr = datetime.datetime.now()
                print("ID %s: waiting for 'unlocked'" % tstr)
                time.sleep(wait_interval)
            else:
                self.move(gap)
                return True
        return False


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    id = ID(s)
    # print id.moveE(12.3984)
    status = id.isLocked()
    gap = 10.05
    id.moveTillMove(gap, wait_interval=10, ntrial=150)

    # dtheta.scanDt1("test",-89000,-87000,20,0,1,0.2)
    # print id.getGapAtE(20.0)
    # print id.move(float(sys.argv[1]))
    # print id.getGap()

    s.close()
