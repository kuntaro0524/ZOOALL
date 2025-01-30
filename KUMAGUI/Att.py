import sys
import socket
import time
import math
from numpy import *

# My library
from Motor import *


class Att:
    def __init__(self, server):
        self.s = server
        self.att = Motor(self.s, "bl_32in_st2_att_1_rx", "pulse")
        self.bssconfig = "/blconfig/bss/bss.config"
        self.isInit = False
        self.pulse_noatt = 3500
        self.isDebug = False

    # 140611 read configure file from BSS.CONFIG
    # Get Thick - Index - Pulse
    def init(self):
        confile = open(self.bssconfig, "r")
        lines = confile.readlines()
        confile.close()

        self.att_idx = []
        self.att_thick = []
        self.att_pulse = []

        # For no attenuator
        self.att_idx.append(0)
        self.att_thick.append(0.0)
        self.att_pulse.append(self.pulse_noatt)

        for line in lines:
            if line.find("Attenuator_Menu_Label") != -1:
                line = line.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
                cols = line.split()
                ncols = len(cols)
                if ncols == 4:
                    if cols[2].find("um") != -1:
                        tmp_thick = float(cols[2].replace("um", ""))
                        tmp_attidx = int(cols[3])
                        # storage
                        self.att_idx.append(tmp_attidx)
                        self.att_thick.append(tmp_thick)

        for line in lines:
            if line.find("Attenuator1_") != -1:
                cols = line.split()
                ncols = len(cols)

                # Attenuator thickness = 0.0
                if line.rfind("_0") != -1:
                    continue

                elif (ncols == 4):
                    tmp_pulse = int(cols[3])
                    self.att_pulse.append(tmp_pulse)

        self.att_idx = array(self.att_idx)
        self.att_thick = array(self.att_thick)
        self.att_pulse = array(self.att_pulse)

        if self.isDebug:
            for i, thick, pulse in zip(self.att_idx, self.att_thick, self.att_pulse):
                print i, thick, pulse
        # flag on
        self.isInit = True

    def setAttThick(self, thick):
        if self.isInit == False:
            self.init()
        for t_conf, p_conf in zip(self.att_thick, self.att_pulse):
            if thick == t_conf:
                print "Set thickness to %5d [um]" % thick
                self.move(p_conf)
                return True
        print "No attenuator in the list"
        return False

    def getAttList(self):
        if self.isInit == False:
            self.init()
        return self.att_thick

    def getBestAtt(self, wl, transmission):
        if not self.isInit:
            self.init()
        attlist = self.att_thick
        cnfac = self.cnFactor(wl)
        mu = self.calcMu(wl, cnfac)
        thickness = (-1.0 * math.log(transmission) / mu) * 10000

        print "IDEAL thickness: %8.1f[um]" % thickness

        idx = 0
        for att in attlist:
            if thickness < att:
                if att - thickness < 1000.0:
                    return att
                else:
                    return attlist[idx - 1]
            idx += 1

    def getBestExpCondition(self, wl, transmission):
        if self.isInit == False:
            self.readBSSconfig()
        attlist = self.att_thick
        cnfac = self.cnFactor(wl)
        mu = self.calcMu(wl, cnfac)
        thickness = (-1.0 * math.log(transmission) / mu) * 10000

        print "IDEAL thickness: %8.1f[um]" % thickness

        near_idx = 0
        for att in attlist:
            if thickness < att:
                break
            near_idx += 1

        for i in range(near_idx - 2, near_idx + 1):
            if i >= len(attlist):
                i = len(attlist) - 1
            # print "Aimed:",transmission
            curr_trans = self.calcAttFac(wl, attlist[i])
            exptime = transmission / curr_trans
            if exptime <= 1.5 and exptime > 0.2:
                print attlist[i], curr_trans, exptime
                return attlist[i], exptime

    def getAttBefore(self, althick):
        if self.isInit == False:
            self.readBSSconfig()
        attlist = self.att_thick

        idx = 0
        for att in attlist:
            if althick == att:
                return attlist[idx - 1]
            idx += 1

    def setAttTrans(self, wl, trans):
        best_att = self.getBestAtt(wl, trans)
        print "Set Al thickness to ", best_att, "[um]"
        self.setAtt(best_att)
        return best_att

    def move(self, pls_bss):
        self.att.move(-pls_bss)

    def getAttIndexConfig(self, t):
        if t == 0.0:
            return 0
        if self.isInit == False:
            self.init()
        for i, thick in zip(self.att_idx, self.att_thick):
            if thick == t:
                return i
        print "Something wrong: No attenuator at this beamline"
        return -9999

    def cnFactor(self, wl):
        cnfac = 0.028 * math.pow(wl, 5) - 0.188 * math.pow(wl, 4) + 0.493 * math.pow(wl, 3) - 0.633 * math.pow(wl,
                                                                                                               2) + 0.416 * math.pow(
            wl, 1) + 0.268
        return cnfac

    def calcMu(self, wl, cnfac):
        mu = 38.851 * math.pow(wl, 3) - 2.166 * math.pow(wl, 4) + 1.3 * cnfac
        return mu

    def calcAttFac(self, wl, thickness, material="Al"):
        # thickness [um]
        if material == "Al":
            cnfac = self.cnFactor(wl)
            mu = self.calcMu(wl, cnfac)
            attfac = math.exp(-mu * thickness / 10000)
            return attfac
        else:
            return -1

    def calcThickness(self, wl, transmission, material="Al"):
        # thickness [um]
        if material == "Al":
            cnfac = self.cnFactor(wl)
            mu = self.calcMu(wl, cnfac)
            thickness = (-1.0 * math.log(transmission) / mu) * 10000
            return thickness
        else:
            return -1

    def isMoved(self):
        isAtt = self.att.isMoved()

        if isAtt == 0:
            return True
        if isAtt == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    att = Att(s)
    att.init()
    # att.setAttThick(0)
    # att.move(3500)
    # print att.setAttTrans(1.0,0.5)
    # print att.getBestAtt(1.0000,0.2127)
    # print att.getBestExpCondition(1.0000,0.02)
    # print att.getBestExpCondition(1.4586,0.02)
    # print att.getBestExpCondition(0.6888,0.02)

    # Attenuator
    #print att.calcAttFac(1.2,1000)
    # print att.calcThickness(1.0,0.01)
    # att.att1000um()
    # att.att0um()
    # att.att200um()
    att.setAttThick(1000)
    # att.readBSSconfig()
    # print att.getAttIndexConfig(5000)

    s.close()
