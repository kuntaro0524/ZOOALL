import sys,os

"""
 SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION
 RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano
   LIMIT     OBSERVED  UNIQUE  POSSIBLE     OF DATA   observed  expected                                      Corr

     6.40        3718     992       995       99.7%      20.6%     19.8%     3706    4.35     23.9%    95.6*     1    0.891     351
     4.54        7014    1807      1807      100.0%      23.0%     21.4%     7010    4.43     26.7%    94.3*     5    0.963     753
     3.72        9013    2303      2303      100.0%      22.7%     21.3%     9011    4.58     26.3%    94.2*     1    0.923    1000
     3.22       10322    2734      2734      100.0%      28.2%     25.3%    10319    3.55     32.9%    90.8*     4    0.958    1213
     2.88       10053    3093      3094      100.0%      35.9%     32.8%    10013    2.35     43.1%    81.3*     6    0.993    1362
     2.63       10655    3412      3420       99.8%      52.5%     47.4%    10572    1.42     63.5%    67.2*     1    0.900    1480
     2.44       12766    3743      3748       99.9%      67.5%     63.5%    12733    1.02     80.2%    60.3*     5    0.847    1693
     2.28       14078    4011      4012      100.0%      76.3%     73.1%    14047    0.84     90.0%    57.2*     1    0.802    1826
     2.15       14867    4216      4227       99.7%      91.0%     89.3%    14773    0.61    106.9%    48.3*     2    0.763    1896
    total       92487   26312     26340       99.9%      37.5%     35.1%    92184    2.07     44.2%    90.3*     3    0.877   11574
"""

class AnaCORRECT():
    def __init__(self,fname):
        ifile=open(fname,"r")
        self.lines=ifile.readlines()
        ifile.close()
        self.isRead=False

        self.dmin=[]
        self.ds2=[]
        self.nrefl=[]
        self.nuniq=[]
        self.nposs=[]
        self.redun=[]
        self.compl=[]
        self.rmeas=[]
        self.isigi=[]
        self.cchalf=[]
        self.anocorr=[]
        self.sigano=[]
        self.nano=[]

    def getFinalSPG(self):
        for line in self.lines:
            if line.rfind("SPACE_GROUP_NUMBER=")!=-1:
                cols=line.split()
                spgnum=int(cols[1])
                return spgnum

        return -1

    def getCellParm(self):
        foundFlag=False
        for line in self.lines:
            if line.rfind("UNIT_CELL_CONSTANTS=")!=-1:
                cols=line.split()
                a=float(cols[1])
                b=float(cols[2])
                c=float(cols[3])
                alph=float(cols[4])
                beta=float(cols[5])
                gamm=float(cols[6])
                foundFlag=True

        if foundFlag==False:
            a,b,c,alph,beta,gamm=0,0,0,0,0,0
        return a,b,c,alph,beta,gamm

    def countDatasets(self):
            if self.isRead==False:
                    self.readLog()
            return self.ndata

    def readLog(self):
            flag=0
            skip=0
            start=0
            idx=0
            self.ndata=0
            for line in self.lines:
                if line.rfind("INPUT_FILE=")!=-1:
                    self.ndata+=1
                if line.find("SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION")!=-1:
                    start=idx
                    #print "START", start
                if start!=0 and line.rfind("total")!=-1:
                    end=idx+1
                    # 2019/10/08 I noticed that this 'break' was included.
                    # Because of this, the final table could not be acquired.
                    # I commented out this line till some problems occurr.
                    #break
                idx+=1
            #end=idx

            self.correct_table=self.lines[start:end]

            dmin_save=0.0
            cc_half_mon=0.0
            logstr=[]
            for i in range(start,end):
                    line=self.lines[i]
                    if line=="\n":
                            continue
                    cols=line.split()
                    #print cols
                    if flag==1 and skip < 3:
                            skip+=1
                            continue
 #3.22       10322    2734      2734      100.0%      28.2%     25.3%    10319    3.55     32.9%    90.8*     4    0.958    1213
 #0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123
 #          1         2         3         4         5         6         7         8         9
                    if line.find("SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION")!=-1:
                            flag=1
                            skip+=1
                            continue
                    if flag==1 and cols[0]=="total":
                            self.total_compl=float(cols[4].replace("%",""))
                            self.total_rfact=float(cols[5].replace("%",""))
                            self.total_isigi=float(cols[8])
                            self.total_cc_half=float(cols[10].replace("%","").replace("*",""))
                            break
                    if flag==1:
                            dmin=float(cols[0])
                            ds2=1.0/dmin/dmin
                            self.dmin.append(dmin)
                            self.ds2.append(ds2)
                            nobs=int(cols[1])
                            nuniq=int(cols[2])
                            compl=float(cols[4].replace("%",""))
                            rfact_string = line[51:60]
                            rfact=float(rfact_string)
                            isigi_string = line[81:88]
                            isigi=float(isigi_string)
                            cc_half_string = line[89:97]
                            cc_half=float(cc_half_string)
                            if nuniq!=0:
                                redun=float(nobs)/float(nuniq)
                            else:
                                redun=0.0

                            self.nrefl.append(nobs)
                            self.nuniq.append(nuniq)
                            self.compl.append(compl)
                            self.rmeas.append(rfact)
                            self.isigi.append(isigi)
                            self.redun.append(redun)
                            self.cchalf.append(cc_half)

                            dmin_save=dmin

            self.isRead=True
            return logstr

    def getStatsTable(self):
            if self.isRead==False:
                    self.readLog()
    
            self.logstr=[]
            for dmin,compl,ds2,rfact,isigi,cc_half in zip(self.dmin,self.compl,self.ds2,self.rmeas,self.isigi,self.cchalf):
                    self.logstr.append("%8.3f, %8.3f, %8.3f,%8.3f,%8.3f,%8.3f\n"%(dmin,compl,ds2,rfact,isigi,cc_half))
            return self.logstr

    def getStatsTableAsItIs(self):
        if self.isRead==False:
            self.readLog()
        return self.correct_table

    def getTotalRmeas(self):
            if self.isRead==False:
                    self.readLog()
            return self.total_rfact

    def getTotalRmeas(self):
            if self.isRead==False:
                    self.readLog()
            return self.total_rfact

    def getDmin(self):
        if self.isRead==False:
            self.readLog()
        dmin = self.dmin[-1]
        return dmin
        
    def getInnerShellRmeas(self):
            if self.isRead == False:
                self.readLog()
            return self.rmeas[0]

    def getOuterShellRmeas(self):
            if self.isRead==False:
                    self.readLog()
            return self.rmeas[len(self.rmeas)-1]

    def getOuterShellCompl(self):
            if self.isRead==False:
                    self.readLog()
            return self.compl[len(self.compl)-1]

    def getOuterShellRedun(self):
            if self.isRead==False:
                    self.readLog()
            return self.redun[len(self.redun)-1]

    def getOuterShellInfo(self):
            if self.isRead==False:
                    self.readLog()
            #print "CCHALF"
            #print self.cchalf
            redun=self.redun[len(self.redun)-1]
            rmeas=self.rmeas[len(self.redun)-1]
            compl=self.compl[len(self.redun)-1]
            isigi=self.isigi[len(self.redun)-1]
            print("HERE")
            cchalf=self.cchalf[len(self.redun)-1]

            return compl,redun,rmeas,isigi,cchalf

if __name__=="__main__":
        ac=AnaCORRECT(sys.argv[1])
        print("###",sys.argv[1])
        outfile=sys.argv[1].replace(".LP",".csv")
        ofile=open(outfile,"w")
        for logstr in ac.getStatsTable():
                ofile.write("%s"%logstr)

        print("Inner=",ac.getInnerShellRmeas())
        print("Total=",ac.getTotalRmeas())
        print(ac.getOuterShellRmeas())
        print(ac.countDatasets())
        print(ac.getCellParm())
        print(ac.getFinalSPG())
        print("######################")
        lines = ac.getStatsTableAsItIs()
        for line in lines:
            print(line)
