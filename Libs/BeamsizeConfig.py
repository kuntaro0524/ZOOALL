# -*- coding: utf-8 -*-
import sys, os
import socket
import numpy as np
from scipy import interpolate
from configparser import ConfigParser, ExtendedInterpolation

class BeamsizeConfig:
    def __init__(self):
        # configure file : "beamline.ini" を読む
        # section 'dirs'  bssconfig_dir
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        self.beamsize = []
        self.tcs_width = []
        self.tcs_height = []
        self.flux_factor = []
        self.param_list = []
        self.tune_parameters = []
        self.isInit = False
        # Max horizontal/vertical beam size in unit of [um]
        self.max_hsize = 10.0
        self.max_vsize = 10.0
        # self.density=7E10 # photons/sec/um^2
        # self.flux_const=7.54E11 #photon flux at TCS 0.1x0.1mm
        # self.flux_const=6.17E11 # 2016/12/18 Final day on FY2016
        self.flux_const = 7E11  # 2017/05/10 FY2017 TCS 0.1x0.1mm

        # Default configure file
        # read from 'beamline.ini" section: files, option: beamsize_conf_file
        self.configfile = self.config.get("files", "beamsize_conf_file")

        self.debug = False

    def setConfigFile(self, configfile):
        self.configfile = configfile

    # BL41XU is using their specific settings
    def readConfig(self):
        print("%s was read" % self.configfile)
        lines = open(self.configfile, "r").readlines()

        rflag = False
        tmpstr = []
        self.wl_list = []
        # Number of wavelength for flux
        self.n_wave = 0
        # beam_params consists of 'beam size' block of strings from beamsize.conf
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

        if self.debug == True:
            for b in beam_params:
                print(b)
        beam_index = 1
        self.beamsize_flux_list = []

        for each_beam_str in beam_params:
            object_param_list = []
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

                if defstr.rfind("_object_parameter") != -1:
                    cols = defstr.split()
                    param_name = cols[1]
                    param_unit = cols[3]
                    if param_unit.rfind("pulse") != -1:
                        param_value = int(cols[2])
                    elif param_unit.rfind("mm") != -1:
                        param_value = float(cols[2])
                    param_list = param_name, param_value, param_unit
                    object_param_list.append(param_list)
                    if self.debug == True:
                        print(object_param_list)

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
                    print("Flux constant is overrided to %9.1e" % self.flux_const)

            self.param_list.append(object_param_list)

            beam_index += 1
        self.isInit = True

        if self.debug == True:
            for bf, pm in zip(self.beamsize_flux_list, self.param_list):
                print(bf, pm)

    # Coded for BL41XU parameter list
    def getFluxAtWavelength(self, hsize, vsize, wavelength):
        if self.isInit == False:
            self.readConfig()

        self.isDebug=True
        if self.debug: print("LENG=",len(self.beamsize_flux_list))
        for (h_beam, v_beam), flux_wave_list in self.beamsize_flux_list:
            #print h_beam, v_beam, flux_wave_list
            if h_beam == hsize and v_beam == vsize:
                flux_list = flux_wave_list
                break
        x = np.array(self.wl_list)
        y = np.array(flux_list)
        f = interpolate.interp1d(x,y,kind="cubic")
        X = np.linspace(x[0], x[-1], 10000, endpoint=True)
        Y = f(X)
        if self.debug == True:
            for ax, ay in zip(X,Y):
                print("wavelength=",ax," Splined=", ay)

        if self.wl_list[0] < self.wl_list[1]:
            for work_x in X:
                if self.debug: print("WORK_X1=", work_x)
                if work_x >= wavelength:
                    flux = f(work_x)
                    break
        else:
            for work_x in X:
                if self.debug: print("WORK_X2=", work_x)
                if work_x <= wavelength+1.e-6:
                    flux = f(work_x)
                    break

        if self.debug == True: 
            print("wavelength = ", wavelength)
            print("Flux = ", flux)

        return flux

    # Definition beam size UNIT=um.
    def getBeamIndexHV(self, hsize, vsize):
        if self.isInit == False:
            self.readConfig()
        # print hsize,vsize
        for beam in self.beamsize:
            b_idx, h_beam, v_beam = beam
            if hsize == h_beam and vsize == v_beam:
                # print b_idx
                # print self.tcs_height[b_idx],self.tcs_width[b_idx]
                return b_idx
        return -9999

    # Definition beam size UNIT=um.
    def getBeamsizeAtIndex(self, index):
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
        # wavelength 1A flux for the initial
        for beamparams in self.beamsize:
            bindex, h_beam, v_beam = beamparams
            char_beam = "%4.1f(H) x %4.1f(V)" % (h_beam, v_beam)
            char_beam_list.append(char_beam)
        # blist=beam_index,h_beam,v_beam

        return char_beam_list

    def getFluxListForKUMA(self):
        if self.isInit == False:
            self.readConfig()
        flux_list = []
        for beamparams in self.beamsize:
            bindex, h_beam, v_beam = beamparams
            flux_1A = self.getFluxAtWavelength(h_beam, v_beam, 1.0000)
            print(flux_1A)
            flux_list.append(flux_1A)
        return flux_list

    def getBeamParams(self, hsize, vsize):
        if self.isInit == False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx, h_beam, v_beam = beam
            if hsize == h_beam and vsize == v_beam:
                ff = self.flux_factor[b_idx]
                flux = self.flux_const * ff
                return b_idx + 1, ff, flux

if __name__ == "__main__":
    config_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
    bsc = BeamsizeConfig(config_dir)
    # bsc.readConfig()
    tw, th, bs, ff = bsc.getBeamParamList()
    print("LEN=",len(bs))
    index = 1
    for b in bs:
        p, q, r = b
        #print "%5.1f (H) x %5.1f (V)um %5.3e" % (q, r, ff)
        print("ALL=",p,q,r)
        #print bsc.getBeamsizeAtIndex(0)
    #print "FLUX=",bsc.getFluxListForKUMA()

    print("EEEEEEEEEEEEE")
    print("%e"%bsc.getFluxAtWavelength(10,15,1.0))

# tcs_hmm=0.1
# tcs_vmm=0.1
# bsc.getBeamsizeAtTCS_HV(tcs_hmm,tcs_vmm)

# bsc.getBeamsizeListForKUMA()
#print bsc.getFluxListForKUMA()
