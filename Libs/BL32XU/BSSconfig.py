from MyException import *

class BSSconfig:
    def __init__(self,config_file="/isilon/blconfig/bl32xu/bss/bss.config"):
        self.confile=config_file
        self.isRead=False
        self.isPrep=False

    def storeLines(self):
        ifile=open(self.confile,"r")
        self.lines=ifile.readlines()

        ifile.close()
        self.isRead=True

    def get(self,confstr):
        if self.isRead==False:
            self.storeLines()

        isFound=False
        for line in self.lines:
            # skip "#" character
            if line[0]=="#":
                continue
            if line.find(confstr)!=-1:
                isFound=True
                fstr=line
                break

        # check if the string was found
        if isFound==False:
            raise MyException("config string was not found.")

        # strip after "#"
        if fstr.rfind("#")!=-1:
            fstr=fstr[:fstr.rfind("#")-1]

        # ":" treatment
        return fstr[fstr.rfind(":")+1:]

    def getValue(self,confstr):
        strvalue=self.get(confstr)
        #print strvalue
        return float(strvalue)

    def readEvacuate(self):
        try:
            self.cryo_on=self.getValue("Cryostream_1_On_Position")
            self.cryo_off=self.getValue("Cryostream_1_Off_Position")
            self.colli_on=self.getValue("Collimator_1_On_Position")
            self.colli_off=self.getValue("Collimator_1_Off_Position:")
            self.bs_on=self.getValue("Beam_Stop_1_On_Position")
            self.bs_off=self.getValue("Beam_Stop_1_Off_Position:")

            self.mx=self.getValue("Cmount_Gonio_X:")
            self.my=self.getValue("Cmount_Gonio_Y:")
            self.mz=self.getValue("Cmount_Gonio_Z:")

        except MyException,ttt:
            print ttt.args[0]

        self.isPrep=True

    def getCmount(self):
        if self.isPrep==False:
            self.readEvacuate()
        return self.mx,self.my,self.mz

    def getCryo(self):
        if self.isPrep==False:
            self.readEvacuate()
        return self.cryo_on,self.cryo_off

    def getBS(self):
        if self.isPrep==False:
            self.readEvacuate()
        return self.bs_on,self.bs_off

    def getColli(self):
        if self.isPrep==False:
            self.readEvacuate()
        return self.colli_on,self.colli_off

#def getCLinfo(self):
#try:
#self.cl_hv=self.getValue("_home_value")
#self.cl_sense=self.getValue("_sense")
#self.cl_val2pulse=self.getValue("_home_value")
#
#except MyException,ttt:
#print ttt.args[0]

if __name__=="__main__":
    bssconf=BSSconfig()


    try:
        print bssconf.getCmount()
        print bssconf.getCryo()
        print bssconf.getColli()
        print bssconf.getBS()

    except MyException,ttt:
        print ttt.args[0]

