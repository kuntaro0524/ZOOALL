import sys,os
import TCSsimple
import socket

class BeamsizeConfig:
    def __init__(self,config_dir):
        self.config_dir=config_dir
        self.beamsize=[]
        self.tcs_width=[]
        self.tcs_height=[]
        self.flux_factor=[]
        self.isInit=False
        # Max horizontal/vertical beam size in unit of [um]
        self.max_hsize=10.0
        self.max_vsize=10.0
        #self.density=7E10 # photons/sec/um^2
        #self.flux_const=7.54E11 #photon flux at TCS 0.1x0.1mm
        #self.flux_const=6.17E11 # 2016/12/18 Final day on FY2016
        self.flux_const=7E11 # 2017/05/10 FY2017 TCS 0.1x0.1mm

        # Default configure file
        self.configfile="%s/bss/beamsize.config"%self.config_dir

    def setConfigFile(self,configfile):
        self.configfile=configfile

    # 2015/09/20 reading beam size config
    # Currently, only matching 'beam size' and 'beam size index on BSS'
    def readConfig(self):
        lines=open(self.configfile,"r").readlines()

        rflag=False
        tmpstr=[]
        beam_params=[]
        for line in lines:
            if line.rfind("_beam_size_begin:")!=-1:
                rflag=True
            if line.rfind("_beam_size_end:")!=-1:
                rflag=False
                beam_params.append(tmpstr)
                tmpstr=[]
            if rflag==True:
                tmpstr.append(line)

        beam_index=0
        for each_beam_str in beam_params:
            for defstr in each_beam_str:
                if defstr.rfind("rectangle")!=-1:
                    cols=defstr.split()
                    h_beam=float(cols[2])*1000.0
                    v_beam=float(cols[3])*1000.0
                    #print beam_index,h_beam,v_beam
                    blist=beam_index,h_beam,v_beam
                    self.beamsize.append(blist)
                    # Searching max beam
                    if self.max_hsize < h_beam:
                        self.max_hsize=h_beam
                    if self.max_vsize < v_beam:
                        self.max_vsize=v_beam
                if defstr.rfind("tc1_slit_1_width")!=-1:
                    cols=defstr.split()
                    #print "SLIT-W",cols[2]
                    self.tcs_width.append(float(cols[2]))
                if defstr.rfind("tc1_slit_1_height")!=-1:
                    cols=defstr.split()
                    #print "SLIT-H",cols[2]
                    self.tcs_height.append(float(cols[2]))
                if defstr.rfind("_flux_factor")!=-1:
                    cols=defstr.split()
                    #print "Flux factor",cols[1]
                    self.flux_factor.append(float(cols[1]))
                if defstr.rfind("_baseflux")!=-1:
                    cols=defstr.split(':')
                    valstr=cols[1].replace("[","").replace("]","")
                    self.flux_const=float(valstr)
                    print "Flux constant is overrided to %9.1e"%self.flux_const
            beam_index+=1
        self.isInit=True
        #print self.beamsize

    # Definition beam size UNIT=um.
    def getBeamIndexHV(self,hsize,vsize):
        if self.isInit==False:
            self.readConfig()
        #print hsize,vsize
        for beam in self.beamsize:
            b_idx,h_beam,v_beam=beam
            if hsize==h_beam and vsize==v_beam:
                #print b_idx
                #print self.tcs_height[b_idx],self.tcs_width[b_idx]
                return b_idx

    # Definition beam size UNIT=um.
    def getBeamsizeAtIndex(self,index):
        if self.isInit==False:
            self.readConfig()
        b_idx,h_beam,v_beam=self.beamsize[index]
        return h_beam,v_beam

    def getBeamParamList(self):
        if self.isInit==False:
            self.readConfig()
        return self.tcs_width,self.tcs_height,self.beamsize,self.flux_factor

    def getBeamsizeAtTCS_HV(self,tcs_hmm,tcs_vmm):
        if self.isInit==False:
            self.readConfig()
        for tcs_w,tcs_h,beam_par in zip(self.tcs_width,self.tcs_height,self.beamsize):
            #print tcs_w,tcs_h
            if tcs_w==tcs_hmm and tcs_h==tcs_vmm:
                b_idx,h_beam,v_beam=beam_par
                #print "BINGO!!"
                #print h_beam,v_beam
                return h_beam,v_beam

    def getTCSapertureWithBeamHV(self,hsize,vsize):
        if self.isInit==False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx,h_beam,v_beam=beam
            if hsize==h_beam and vsize==v_beam:
                return self.tcs_width[b_idx],self.tcs_height[b_idx]

    def changeBeamsizeHV(self,hsize,vsize):
        tcs_hsize,tcs_vsize=self.getTCSapertureWithBeamHV(hsize,vsize)
        #print tcs_hsize,tcs_vsize
        self.tcs.setApert(tcs_vsize,tcs_hsize)

    def getNumBeamsizeList(self):
        if self.isInit==False:
            self.readConfig()
        return len(self.beamsize)

    def getMaxBeam(self):
        if self.isInit==False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx,h_beam,v_beam=beam
            if h_beam==self.max_hsize and v_beam==self.max_vsize:
                #print b_idx
                return b_idx

    # For KUMA GUI list
    def getBeamsizeListForKUMA(self):
        if self.isInit==False:
            self.readConfig()
        char_beam_list=[]
        for beamparams,ff in zip(self.beamsize,self.flux_factor):
            print beamparams,ff
            bindex,h_beam,v_beam=beamparams
            char_beam="%4.1f(H) x %4.1f(V)"%(h_beam,v_beam)
            char_beam_list.append(char_beam)
            #blist=beam_index,h_beam,v_beam
        return char_beam_list

    def getFluxListForKUMA(self):
        if self.isInit==False:
            self.readConfig()
        flux_list=[]
        for beamparams,ffac in zip(self.beamsize,self.flux_factor):
            bindex,h_beam,v_beam=beamparams
            flux=self.flux_const*ffac
            flux_list.append(flux)
        return flux_list

    def getBeamParams(self,hsize,vsize):
        if self.isInit==False:
            self.readConfig()
        for beam in self.beamsize:
            b_idx,h_beam,v_beam=beam
            if hsize==h_beam and vsize==v_beam:
                #print self.tcs_height[b_idx],self.tcs_width[b_idx]
                ff=self.flux_factor[b_idx]
                flux=self.flux_const*ff
                #print "%5.1f um x %5.1f um flux=%e"%(hsize,vsize,flux)
                return b_idx+1,ff,flux

if __name__=="__main__":
    config_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
    config_dir="/isilon/blconfig/bl32xu/"
    bsc=BeamsizeConfig(config_dir)

    lll=bsc.getFluxListForKUMA()
    #lll=bsc.getBeamsizeListForKUMA()

    index=bsc.getBeamIndexHV(10,15)
    print index
    print lll[index]

    #tw,th,bs,ff=bsc.getBeamParamList()
    #for b in bs:
        #p,q,r=b
        #print "%5.1f (H) x %5.1f (V)um"%(q,r)
    #print bsc.getBeamsizeAtIndex(3)

    #tcs_hmm=0.1
    #tcs_vmm=0.1
    #bsc.getBeamsizeAtTCS_HV(tcs_hmm,tcs_vmm)

    #bsc.getBeamsizeListForKUMA()
    #print bsc.getFluxListForKUMA()
