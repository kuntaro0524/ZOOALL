import sys, os, math, time, tempfile, datetime


class Raddose():
    def __init__(self):
        self.energy = 12.3984
        self.vbeam_size_um = 10.0
        self.hbeam_size_um = 10.0
        self.phosec = 2E12
        self.exptime = 1.0
        self.common_dir = "/isilon/BL45XU/BLsoft/PPPP/RADDOSE/"
        self.con = 1500.0

    def setSalCon(self, con):
        self.con = con

    def setLogfile(self, logfile):
        self.logfile = logfile

    def setExpTime(self, exp_time):
        self.exptime = exp_time

    def setBeamsize(self, vbeam_um, hbeam_um):
        self.vbeam_size_um = vbeam_um
        self.hbeam_size_um = hbeam_um

    def setPhosec(self, phosec):
        self.phosec = phosec

    def writeCom(self):
        ttime = datetime.datetime.now()
        timestr = datetime.datetime.strftime(ttime, '%y%m%d%H%M%S')
        self.comfile = "%s/%s.com" % (self.common_dir, timestr)
        self.logfile = "%s/%s.log" % (self.common_dir, timestr)
        # beam size should be in 'mm'
        vbeam_mm = self.vbeam_size_um / 1000.0
        hbeam_mm = self.hbeam_size_um / 1000.0

        oxistr = """#!/bin/csh
/usr/local/bin/raddose << EOF  > %s
ENERGY %12.5f
CELL 180 178 209 90 90 90 
NRES 4000
NMON 4
PATM S 4 Fe 4 CU 4 ZN 2
BEAM  %8.4f %8.4f
CRYST 0.5 0.5 0.5
PHOSEC %8.1e
EXPO %6.3f
IMAGE 1
EOF
		""" % (self.logfile, self.energy, vbeam_mm, hbeam_mm, self.phosec, self.exptime)

        lysstr = """#!/bin/csh
/usr/local/bin/raddose << EOF > %s
ENERGY %12.5f
CELL 78 78 36 90 90 90"
NRES 129
NMON 8
SOLVENT 0.38
CRYST 0.5 0.5 0.05
BEAM  %8.4f %8.4f
PHOSEC %8.1e
EXPO %6.3f
IMAGE 1
SATM Na %5.1f CL %5.1f
EOF 
		""" % (self.logfile, self.energy, vbeam_mm, hbeam_mm, self.phosec, self.exptime, self.con, self.con)
        # print vbeam_mm,hbeam_mm
        comf = open(self.comfile, "w")
        # comf.write("%s"%comstring)
        # comf.write("%s"%oxistr)
        comf.write("%s" % lysstr)
        comf.close()

    def runRemote(self):
        self.writeCom()
        # print "COMFILE=",self.comfile
        # print "LOGFILE=",self.logfile

        os.system("chmod 744 %s" % self.comfile)
        os.system("ssh oys08.spring8.or.jp %s" % self.comfile)

        time.sleep(0.1)
        lines = open("%s" % self.logfile).readlines()
        for line in lines:
            if line.rfind("image") != -1:
                # print line.split()
                return float(line.split()[5]) / 1E6
        else:
            return -999.999

    def runOys(self, remote=False):
        if remote == False:
            os.system("csh %s" % self.comfile)
        else:
            os.system("chmod 744 %s" % self.comfile)
            os.system("ssh oys08.spring8.or.jp %s" % self.comfile)

        time.sleep(0.1)
        lines = open("%s" % self.logfile).readlines()
        for line in lines:
            if line.rfind("image") != -1:
                # print line.split()
                return float(line.split()[5]) / 1E6

    def runCom(self, remote=False):
        self.writeCom()
        if remote == False:
            os.system("csh %s" % self.comfile)
        else:
            os.system("chmod 744 %s" % self.comfile)
            os.system("ssh oys08.spring8.or.jp %s" % self.comfile)

        time.sleep(0.1)
        lines = open("%s" % self.logfile).readlines()
        for line in lines:
            if line.rfind("image") != -1:
                #print line.split()
                return float(line.split()[5]) / 1E6

    def getDose(self, h_beam_um, v_beam_um, phosec, exp_time, energy=12.3984, salcon=1500, remote=False):
        self.setSalCon(salcon)
        self.setPhosec(phosec)
        self.setExpTime(exp_time)
        self.setBeamsize(v_beam_um, h_beam_um)
        self.energy = energy
        dose = self.runCom(remote=remote)
        #print "getDose=", dose
        return dose

    def getDose1sec(self, h_beam_um, v_beam_um, phosec, energy=12.3984, salcon=1500, remote=False):
        self.setSalCon(salcon)
        self.setPhosec(phosec)
        self.setExpTime(1.0)
        self.setBeamsize(v_beam_um, h_beam_um)
        self.energy = energy
        dose = self.runCom(remote=remote)
        return dose


if __name__ == "__main__":
    e = Raddose()
    # dose_1sec=e.getDose(10,9,7E12,1.0)

    # 160425 K.Hirata 3x3 um , 5x5 um
    # dose_1sec=e.getDose(10,15,1.0E13,1.0)

    # 160509 wl=1.0A 10x15 um
    en = 12.3984
    # print e.writeCom()
    # print e.getDose()

    # density=7.0E10 # photons/um^2/s
    beam_h = 10
    beam_v = 10
    # flux=density*beam_h*beam_v #photons
    flux = 1.0E13

    # en_list=[8.5,10.0,12.3984,15,18]
    en_list = [12.3984]
    # nacl_con=[0,500,1000,1500] #mM
    for en in en_list:
        for exptime in [0.01, 0.02]:
            dose = e.getDose(10, 10, flux, 1.0, energy=en)
            dose_exp = dose * exptime *1000.0
            print "%8.1f %8.3f MGy (oxidase) %5.2f sec %5.2f kGy" % (en, dose, exptime, dose_exp)
            attenuation_for_200kGy = 200.0 / dose_exp
            print "Attenuation factor for 200 kGy (1time) = %8.3f" % (attenuation_for_200kGy)
            print "Attenuation factor for 200 kGy (2time) = %8.3f" % (attenuation_for_200kGy / 2)


