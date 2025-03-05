import sys,os
import TCSsimple
import socket

class Beamsize:
    def __init__(self,ms,config_dir):
        self.ms=ms
        self.config_dir=config_dir
        self.beamsize=[]
        self.tcs_width=[]
        self.tcs_height=[]
        self.isInit=False
        # Max horizontal/vertical beam size in unit of [um]
        self.max_hsize=10.0
        self.max_vsize=10.0

        self.tcs=TCSsimple.TCSsimple(ms)

    # 2015/09/20 reading beam size config
    # Currently, only matching 'beam size' and 'beam size index on BSS'
    def readConfig(self):
        self.configfile="%s/bss/beamsize.config"%self.config_dir
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

    def getTCSapertureWithBeamHV(self,hsize,vsize):
        if self.isInit==False:
            self.readConfig()
        print "OKAY"
        print self.beamsize
        for beam in self.beamsize:
            b_idx,h_beam,v_beam=beam
            if hsize==h_beam and vsize==v_beam:
                return self.tcs_width[b_idx],self.tcs_height[b_idx]

    def changeBeamsizeHV(self,hsize,vsize):
        hsize=float(hsize)
        vsize=float(vsize)
        print hsize,vsize
        tcs_hsize,tcs_vsize=self.getTCSapertureWithBeamHV(hsize,vsize)
        print tcs_hsize,tcs_vsize
        self.tcs.setApert(tcs_vsize,tcs_hsize)
        print "OKOKOKOKOK"

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

if __name__=="__main__":
    #host = '192.168.163.1'
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    config_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/"
    bsc=Beamsize(s,config_dir)
    #bsc.readConfig()
    #print bsc.getBeamIndexHV(10.0,18.0)
    #print bsc.getBeamIndexHV(3.0,3.0)
    #print bsc.getTCSapertureWithBeamHV(10.0,18.0)
    print bsc.getTCSapertureWithBeamHV(3.0,3.0)
    #print bsc.changeBeamsizeHV(3.0,3.0)
    #print bsc.changeBeamsizeHV(10.0,18.0)
    #bsc.getMaxBeam()

"""
  File "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LoopMeasurement.py", line 497, in genHelical
    self.setBeamsize(hbeam,vbeam)
  File "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LoopMeasurement.py", line 42, in setBeamsize
    self.bsc.changeBeamsizeHV(h_beam,v_beam)
  File "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/Beamsize.py", line 86, in changeBeamsizeHV
    tcs_hsize,tcs_vsize=self.getTCSapertureWithBeamHV(hsize,vsize)
"""
