import sys, os, math, time, tempfile, datetime


class Raddose():
    def __init__(self):
        self.energy = 12.3984
        self.vbeam_size_um = 10.0
        self.hbeam_size_um = 10.0
        self.phosec = 2E12
        self.exptime = 1.0
        self.common_dir = "/isilon/BL32XU/BLsoft/PPPP/RADDOSE/"
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

        if self.sample == "oxi":
            sample_str = """#!/bin/csh
raddose << EOF  > %s
ENERGY %12.5f
CELL 180 178 209 90 90 90 
NRES 4000
NMON 4
PATM S 4 Fe 4 CU 4 ZN 2
BEAM  %8.4f %8.4f
CRYST 0.5 0.5 0.5
PHOSEC %8.1e
EXPO %8.2f
IMAGE 1
EOF
		""" % (self.logfile, self.energy, vbeam_mm, hbeam_mm, self.phosec, self.exptime)

        elif self.sample == "lys":
            sample_str = """#!/bin/csh
raddose << EOF > %s
ENERGY %12.5f
CELL 78 78 36 90 90 90"
NRES 129
NMON 8
SOLVENT 0.38
CRYST 0.5 0.5 0.05
BEAM  %8.4f %8.4f
PHOSEC %8.1e
EXPO %8.2f
IMAGE 1
SATM Na %5.1f CL %5.1f
EOF 
		""" % (self.logfile, self.energy, vbeam_mm, hbeam_mm, self.phosec, self.exptime, self.con, self.con)
        # print vbeam_mm,hbeam_mm
        comf = open(self.comfile, "w")
        comf.write("%s" % sample_str)
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
        print(self.logfile)
        print(os.path.exists(self.logfile))
        #lines = open("%s" % self.logfile, encoding="CP932").readlines()
        lines = open("%s" % self.logfile).readlines()
        for line in lines:
            if line.rfind("image") != -1:
                # print line.split()
                return float(line.split()[5]) / 1E6

    def getDose(self, h_beam_um, v_beam_um, phosec, exp_time, energy=12.3984, salcon=1500, remote=False):
        self.setSalCon(salcon)
        self.setPhosec(phosec)
        self.setExpTime(exp_time)
        self.setBeamsize(v_beam_um, h_beam_um)
        self.energy = energy
        # print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
        dose = self.runCom(remote=remote)
        # print "DDDDDDD" , dose
        return dose

    def getDose1sec(self, h_beam_um, v_beam_um, phosec, energy=12.3984, salcon=1500, remote=False,sample="lys"):
        self.sample = sample
        self.setSalCon(salcon)
        self.setPhosec(phosec)
        self.setExpTime(1.0)
        self.setBeamsize(v_beam_um, h_beam_um)
        self.energy = energy
        dose = self.runCom(remote=remote)
        return dose


if __name__ == "__main__":
    e = Raddose()

    # 160509 wl=1.0A 10x15 um
    en = 12.3984

    # density=1.4E12 # photons/um^2/s
    beam_h = 10
    beam_v = 10
    flux = 2E10
    exptime = 1.0

    pf_en = 12.3984 / 3.0
    numoto_en = 12.3984 / 1.1
    hirata_en = 12.3984 / 0.9
    en_list = [pf_en, numoto_en, 12.3984]

    for en in en_list:
        dose = e.getDose(beam_h, beam_v, flux, exptime, energy=en)
        # exptime_for_10MGy = dose/
        print("%8.1f %8.3f MGy" % (en, dose))
