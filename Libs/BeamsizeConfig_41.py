import sys, os
import socket
import numpy as np
from scipy import interpolate

class BeamsizeConfig:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.beamsize = []
        self.tcs_width = []
        self.tcs_height = []
        self.flux_factor = []
        self.isInit = False
        # Max horizontal/vertical beam size in unit of [um]
        self.max_hsize = 10.0
        self.max_vsize = 10.0
        # self.density=7E10 # photons/sec/um^2
        # self.flux_const=7.54E11 #photon flux at TCS 0.1x0.1mm
        # self.flux_const=6.17E11 # 2016/12/18 Final day on FY2016
        self.flux_const = 7E11  # 2017/05/10 FY2017 TCS 0.1x0.1mm

        # Default configure file
        self.configfile = "%s/bss/beamsize.config" % self.config_dir

    def setConfigFile(self, configfile):
        self.configfile = configfile

    # BL41XU is using their specific settings
    def readConfig(self):
        print "%s was read" % self.configfile
        lines = open(self.configfile, "r").readlines()

        rflag = False
        tmpstr = []
        self.wl_list = []
        # Number of wavelength for flux
        self.n_wave = 0
        beam_params = []
        for line in lines:
            if line[0] == "#":
                continue
            if line.rfind("_beam_size_begin:") != -1:
                rflag = True
            if line.rfind("_beam_size_end:") != -1:
                rflag = False
                beam_params.append(tmpstr)
                tmpstr = []
            if rflag == True:
                tmpstr.append(line)
            if line.rfind("_wavelength_list:") != -1:
                wl_cols = (line.replace("_wavelength_list:", "")).split(",")
                for wl in wl_cols:
                    self.wl_list.append(float(wl))

        beam_index = 1
        self.beamsize_flux_list = []
        for each_beam_str in beam_params:
            for defstr in each_beam_str:
                if defstr.rfind("rectangle") != -1:
                    cols = defstr.split()
                    h_beam = float(cols[2]) * 1000.0
                    v_beam = float(cols[3]) * 1000.0
                    # print beam_index,h_beam,v_beam
                    blist = beam_index, h_beam, v_beam
                    self.beamsize.append(blist)
                    # Searching max beam
                    if self.max_hsize < h_beam:
                        self.max_hsize = h_beam
                    if self.max_vsize < v_beam:
                        self.max_vsize = v_beam
                if defstr.rfind("tc1_slit_1_width") != -1:
                    cols = defstr.split()
                    # print "SLIT-W",cols[2]
                    self.tcs_width.append(float(cols[2]))
                if defstr.rfind("tc1_slit_1_height") != -1:
                    cols = defstr.split()
                    # print "SLIT-H",cols[2]
                    self.tcs_height.append(float(cols[2]))
                if defstr.rfind("_flux_list") != -1:
                    #print "DEFSTR=",defstr
                    flux_cols = (defstr.strip().replace("_flux_list:", "")).split(",")
                    self.beamsize_flux_list.append(((h_beam, v_beam), flux_cols))

                if defstr.rfind("_baseflux") != -1:
                    cols = defstr.split(':')
                    valstr = cols[1].replace("[", "").replace("]", "")
                    self.flux_const = float(valstr)
                    print "Flux constant is overrided to %9.1e" % self.flux_const
            beam_index += 1
        self.isInit = True
        #print self.beamsize_flux_list

    # Coded for BL41XU parameter list
    def getFluxAtWavelength(self, hsize, vsize, wavelength):
        if self.isInit == False:
            self.readConfig()

        # print len(self.beamsize_flux_list)
        for (h_beam, v_beam), flux_wave_list in self.beamsize_flux_list:
            if h_beam == hsize and v_beam == vsize:
                flux_list = flux_wave_list
                break
        x = np.array(self.wl_list)
        y = np.array(flux_list)
        #print x,y
        f = interpolate.interp1d(x,y,kind="cubic")
        X = np.linspace(x[0], x[-1], 10000, endpoint=True)
        Y = f(X)
        """
        for ax, ay in zip(X,Y):
            print ax, ay
        """
        for work_x in X:
            if work_x > wavelength:
                flux = f(work_x)
                break

        return flux

    # Definition beam size UNIT=um.
    def getBeamIndexHV(self, hsize, vsize):
        if self.isInit == False:
            self.readConfig()

        # print hsize,vsize
        for beam in self.beamsize:
            b_idx, h_beam, v_beam = beam
            if hsize == h_beam and vsize == v_beam:
                return b_idx
        return -9999

    # Definition beam size UNIT=um.
    def getBeamsizeAtIndex(self, index):
        print "TESTTEST"
        if self.isInit == False:
            self.readConfig()
        for b_idx, h_beam, v_beam in self.beamsize:
            if b_idx == index:
                return h_beam, v_beam

    def getBeamParamList(self):
        if self.isInit == False:
            self.readConfig()
        return self.tcs_width, self.tcs_height, self.beamsize, self.flux_factor

    def getNumBeamsizeList(self):
        if self.isInit == False:
            self.readConfig()
        return len(self.beamsize)

    def getMaxBeam(self):
        if self.isInit == False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx, h_beam, v_beam = beam
            if h_beam == self.max_hsize and v_beam == self.max_vsize:
                # print b_idx
                return b_idx

    # For KUMA GUI list
    def getBeamsizeListForKUMA(self):
        if self.isInit == False:
            self.readConfig()
        char_beam_list = []
        for beamparams, ff in zip(self.beamsize, self.flux_factor):
            print beamparams, ff
            bindex, h_beam, v_beam = beamparams
            char_beam = "%4.1f(H) x %4.1f(V)" % (h_beam, v_beam)
            char_beam_list.append(char_beam)
        # blist=beam_index,h_beam,v_beam
        return char_beam_list

    def getFluxListForKUMA(self):
        if self.isInit == False:
            self.readConfig()
        flux_list = []
        print self.beamsize, self.flux_factor
        for beamparams, ffac in zip(self.beamsize, self.flux_factor):
            bindex, h_beam, v_beam = beamparams
            flux = self.flux_const * ffac
            flux_list.append(flux)
        return flux_list

    def getBeamParams(self, hsize, vsize):
        if self.isInit == False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx, h_beam, v_beam = beam
            if hsize == h_beam and vsize == v_beam:
                # print self.tcs_height[b_idx],self.tcs_width[b_idx]
                ff = self.flux_factor[b_idx]
                flux = self.flux_const * ff
                # print "%5.1f um x %5.1f um flux=%e"%(hsize,vsize,flux)
                return b_idx + 1, ff, flux


if __name__ == "__main__":
    config_dir = "/isilon/blconfig/bl41xu/"
    bsc = tttt(config_dir)
    # bsc.readConfig()
    tw, th, bs, ff = bsc.getBeamParamList()
    print "LEN=",len(bs)
    for b in bs:
        p, q, r = b
        #print "%5.1f (H) x %5.1f (V)um %5.3e" % (q, r, ff)
        print p,q,r
        #print bsc.getBeamsizeAtIndex(0)
    #print bsc.getFluxListForKUMA()
    #print bsc.getBeamIndexHV(21,21)
    print bsc.getFluxAtWavelength(22, 30, 1.0)

    bsc.readConfig()

# tcs_hmm=0.1
# tcs_vmm=0.1
# bsc.getBeamsizeAtTCS_HV(tcs_hmm,tcs_vmm)

# bsc.getBeamsizeListForKUMA()
#print bsc.getFluxListForKUMA()
