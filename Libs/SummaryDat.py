import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import CrystalSpot

class SummaryDat:
    def __init__(self, summary_dat_path, nv, nh):
        self.path=summary_dat_path
        self.isRead=False
        self.isKind=False
        self.isList=False
        self.isScoreAbove=False
        self.summary_file="%s/summary.dat"%self.path
        self.DEBUG=False

        # DEBUG option
        self.debug=False

        # Threshold for min/max score
        # Crystals with core ranging self.min_score to self.max_score
        # data collection is applied
        self.min_score=10
        self.max_score=1000

        # # of spots in the heatmap
        self.nv=nv
        self.nh=nh

        self.timeout = 1800.0

    def setSummaryFile(self,filename):
        self.summary_file="%s/%s"%(self.path,filename)

    def waitTillSummary(self):
        print("waitTillSummary")

    # 2016/06/27
    # completeness: = (n images in summary.dat / n images collected)
    # timeout: waiting time of output file
    def readSummary(self,scan_id,nimages_all,comp_thresh,timeout=120):
        starttime=datetime.datetime.now()
        prefix="%s_"%scan_id
        # Waitinf for the generation of summary.dat file
        while(1):
            print("Waiting for generating %s"%self.summary_file)
            if os.path.exists(self.summary_file)==False:
                time.sleep(2.0)
            else:
                "%s can be read now!!"%self.summary_file
                break

        # Checking completeness
        while(1):
            # Re-open the file : to close the file definitely 2020.10.22 added by K.H
            sumdatfile=open(self.summary_file,"r")
            self.lines=sumdatfile.readlines()
            self.isRead=True
            self.extractKind(kind="n_spots")
            n_read=len(self.score_lines)
            print("Current=",self.ngrids,"All=",nimages_all)
            completeness=float(self.ngrids)/float(nimages_all)
            print("completeness=",completeness*100.0)
            if completeness >= comp_thresh:
                break
            else:
                currtime=datetime.datetime.now()
                print(currtime)
                if (currtime-starttime).seconds > timeout:
                    raise MyException.MyException("readSummary: summary.dat was not filled < 80%")
                else:
                    # closing the file definitely 2020.10.22 added by K.H
                    sumdatfile.close()
                    time.sleep(2.0)

        self.isRead=True

    def extractKind(self,kind="n_spots"):
        if self.isRead==False:
            self.readSummary()
        # score_lines:
        # lines including targeted "kind"
        # kind: scores on SHIKA
        self.score_lines=[]
        for line in self.lines:
            if line.rfind(kind)!=-1:
                self.score_lines.append(line)

        self.score_lines.sort(key=lambda x:x.split()[5])
        self.ngrids=len(self.score_lines)

        if self.DEBUG: print(self.score_lines)
        self.isKind=True

    def process(self,kind):
        #print "in processing"
        self.score_good=[]
        self.extractKind(kind)

        # self.score_lines should be obtained
        if self.isKind==False:
            self.extractKind(kind)
        if self.DEBUG: print(self.score_lines)
        self.v=[]
        #print "LEN SCORE_LINES",len(self.score_lines)
        for line in self.score_lines:
            #print "SCORE_LINE:",line
            cols=line.split()
            tmp_score=float(cols[4])
            self.v.append(tmp_score)

        #print "LEN",len(self.v)
        aaa=numpy.array(self.v)
        print("SummaryDat.process:(V,H)=",self.nv,self.nh,"LEN(AAA)=",len(aaa))
        #self.heatmap=numpy.reshape(aaa,(self.nh,self.nv))
        self.heatmap=numpy.reshape(aaa,(self.nv,self.nh))

        # Vertical direction
        for nv in range(0,self.nv):
            if nv % 2 != 0:
                hline=self.heatmap[nv,]
                #print "ORIG=",self.heatmap[nv,]
                newline=numpy.fliplr([hline])[0]
                self.heatmap[nv,]=newline
            #print "INV=",self.heatmap[nv,]

        """
                print "SummaryDat.process=",self.heatmap.shape
                for v in range(0,self.nv):
                        for h in range(0,self.nh):
                                print "ML:",h,v,self.heatmap[v,h]
                        print ""
        """

        self.isList=True
        return self.heatmap

if __name__=="__main__":
    cxyz=(0.7379,   -11.5623,    -0.0629)
    phi=0.0
    prefix="xi-KLaT006-12"
    summary_dat_path="/isilon/users/target/target/AutoUsers/180123/xiangyu/xi-KLaT006-12/scan/_spotfinder/"

    sumdat=SummaryDat(summary_dat_path,cxyz,phi,45,83)
    nimages_all=10
    completeness=0.95

    #sumdat.setMinMax(50,100)
    sumdat.readSummary(prefix,nimages_all,completeness,timeout=120)
    heatmap=sumdat.process("n_spots")

    print(heatmap.shape)

    for v in range(0,45):
        for h in range(0,83):
            print(v,h,heatmap[v,h])
        print("")
