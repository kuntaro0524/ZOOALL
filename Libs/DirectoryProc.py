import os,sys,math,glob 
import time

class DirectoryProc():
    def __init__(self,path):
        self.path=path
        self.dirs=[]
        self.filelist=[]
        self.isPrep=False
        
    def prep(self):
        self.chklist=os.listdir(self.path)
        index=0
        for eachf in self.chklist:
            index+=1
            chkfile="%s/%s"%(self.path,eachf)
            abspath=os.path.abspath(chkfile)
            if os.path.isdir(abspath):
                self.dirs.append(abspath)
            else:
                self.filelist.append(abspath)
        self.isPrep=True

    def roundMakeDirMaster(self, dir_prefix, ndigit = 3, option = "top", isMake = False):
        curr_dir = os.path.abspath(self.path)
        dir_to_be_made = "%s/%s"%(curr_dir, dir_prefix)
        print("Directopy prefix = ",dir_to_be_made)
        # Checking if the directory exists
        dindex = 0
        while(1):
            if option == "top":
                if ndigit == 3:
                    new_dir = "%03d_%s"%(dindex, dir_prefix)
                elif ndigit == 2:
                    new_dir = "%02d_%s"%(dindex, dir_prefix)
                elif ndigit == 4:
                    new_dir = "%04d_%s"%(dindex, dir_prefix)
                dir_for_replace = "%s/%s"%(curr_dir, new_dir)
                #print "Check if existence:",dir_for_replace
                if os.path.exists(dir_for_replace) == True:
                    print("Already exists:",dir_for_replace)
                    dindex += 1
                    continue
                else:
                    break
            else:
                if ndigit == 3:
                    new_dir = "%s_%03d"%(dir_prefix, dindex)
                elif ndigit == 2:
                    new_dir = "%s_%02d"%(dir_prefix, dindex)
                elif ndigit == 4:
                    new_dir = "%s_%04d"%(dir_prefix, dindex)
                dir_for_replace = "%s/%s"%(curr_dir, new_dir)
                if os.path.exists(dir_for_replace) == True:
                    print("Already exists:",dir_for_replace)
                    dindex += 1
                    continue
                else:
                    break

        # Making a directory
        if isMake == True:
            print("Making %s"%dir_for_replace)
            os.makedirs(dir_for_replace)

        return dir_for_replace, dindex

    # 2019/04/08 for ZOO scan/data collection
    def makeRoundDir(self, dir_prefix, isMake = False, ndigit=4):
        curr_dir = os.path.abspath(self.path)
        dindex = 0
        while(1):
            if ndigit == 4:
                local_dir = "%s%04d"%(dir_prefix,dindex)
            elif ndigit == 5:
                local_dir = "%s%05d"%(dir_prefix,dindex)
            elif ndigit == 3:
                local_dir = "%s%03d"%(dir_prefix,dindex)
            elif ndigit == 2:
                local_dir = "%s%02d"%(dir_prefix,dindex)
            else:  
                local_dir = "%s%08d"%(dir_prefix,dindex)
            target_dir = "%s/%s"%(curr_dir, local_dir)
            print("Checking %s" % target_dir)
            if os.path.exists(target_dir) == True:
                print("Existing=",target_dir)
                dindex += 1
                continue
            else:
                print("To be made :  %s"%(target_dir))
                print("dindex = %5d"%dindex)
                break

        if isMake == True:
            os.makedirs(target_dir)
        return target_dir, dindex

    # 2019/05/20
    def getFilenameRoundHeadPrefix(self, prefix, suffix, ndigit=4):
        proc_dir = os.path.abspath(self.path)

        # Checking if the target file exists
        dindex = 0
        check_filename = "%04d_%s.%s" % (0, prefix, suffix)
        print("Checking prefix = ", check_filename)

        while(1):
            if ndigit == 3:
                check_filename = "%03d_%s.%s" % (dindex, prefix, suffix)
            elif ndigit == 2:
                check_filename = "%02d_%s.%s" % (dindex, prefix, suffix)
            elif ndigit == 4:
                check_filename = "%04d_%s.%s" % (dindex, prefix, suffix)
            if os.path.exists(check_filename) == True:
                print("Already exists:", check_filename)
                dindex += 1
                continue
            else:
                break
        # Making a directory
        return check_filename

    # 2019/05/20 for logging INOCC
    def getRoundHeadPrefix(self, ndigit=4):
        proc_dir = os.path.abspath(self.path)

        # Checking if the target file exists
        dindex = 0
        dire_list = os.listdir(self.path)

        file_list = glob.glob("????_*")
        #print dire_list
        #check_filename = "%04d_%s.%s" % (0, prefix, suffix)
        #print "Checking prefix = ", check_filename

        if len(file_list) == 0:
            if ndigit == 4:
                return "0000"
            elif ndigit == 3:
                return "000"
            elif ndigit == 2:
                return "00"
            return num_prefix

        imax = -99999
        n_success = 0
        for dname in dire_list:
            try:
                file_index = int(dname[0:ndigit].replace("_",""))
                n_success += 1
                if file_index > imax:
                    imax = file_index
            except:
                print("Next file")
                continue

        if n_success == 0:
            imax = -1
        new_index = imax + 1
        if ndigit == 4:
            num_prefix = "%04d"%new_index
        elif ndigit == 3:
            num_prefix = "%03d"%new_index
        elif ndigit == 2:
            num_prefix = "%02d"%new_index
        return num_prefix

    # 2019/04/08 for ZOO scan/data collection
    def getRoundPath(self, dir_prefix, ndigit=4):
        curr_dir = os.path.abspath(self.path)
        dindex = 0
        while(1):
            if ndigit == 4:
                local_dir = "%04d_%s"%(dir_prefix,dindex)
            elif ndigit == 5:
                local_dir = "%05d_%s"%(dir_prefix,dindex)
            elif ndigit == 3:
                local_dir = "%03d_%s"%(dir_prefix,dindex)
            else:  
                local_dir = "%08d_%s"%(dir_prefix,dindex)
            target_dir = "%s/%s"%(curr_dir, local_dir)
            print("Checking %s" % target_dir)
            if os.path.exists(target_dir) == True:
                print("Existing=",target_dir)
                dindex += 1
                continue
            else:
                print("Making! %s"%(target_dir))
                print("dindex = %5d"%dindex)
                break

        return target_dir, dindex

    def getFileList(self):
        if self.isPrep==False:
            self.prep()
        return self.filelist

    def getDirList(self):
        if self.isPrep==False:
            self.prep()
        return self.dirs

    def findTarget(self,targetname):
        targetlist=[]
        pathlist=[]
        if self.isPrep==False:
            self.prep()
        for root, dirs, files in os.walk(self.path):
            for fname in files:
                fullpath=os.path.join(root, fname)
                if fname==targetname:
                    targetlist.append(fullpath)
                    pathlist.append(root)
        return targetlist,pathlist

    def findTargetWith(self,string_in_filename):
        targetlist=[]
        pathlist=[]
        if self.isPrep==False:
            self.prep()
        for root, dirs, files in os.walk(self.path):
            for fname in files:
                fullpath=os.path.join(root, fname)
                #print fname,string_in_filename
                #print fname.rfind(string_in_filename)
                if fname.rfind(string_in_filename)!=-1:
                    targetlist.append(fullpath)
                    pathlist.append(root)
                    print(fname)
        return targetlist,pathlist

    def findTargetFileInTargetDirectories(self,string_in_dire,string_in_filename,exclude_str=""):
        targetlist=[]
        pathlist=[]
        if self.isPrep==False:
            self.prep()
        for dir_in_path, junk, files in os.walk(self.path):
            #print "DIRE=",dir_in_path,string_in_dire
            if dir_in_path.rfind(string_in_dire)!=-1:
                if exclude_str!="":
                    if dir_in_path.rfind(exclude_str)!=-1:
                        print("Skipping",dir_in_path)
                        continue
                #print dir_in_path
                for fname in files:
                    fullpath=os.path.join(dir_in_path, fname)
                    if fname.rfind(string_in_filename)!=-1:
                        targetlist.append(fullpath)
                        pathlist.append(dir_in_path)
                        #print fname
        return targetlist,pathlist

    def findTargetDirs(self,string_in_dire):
        targetlist=[]
        pathlist=[]
        if self.isPrep==False:
            self.prep()
        for dir_in_path, junk, files in os.walk(self.path):
            if dir_in_path.rfind(string_in_dire)!=-1:
                pathlist.append(dir_in_path)
            else:
                continue
        return pathlist

    def findTargetFileIn(self,rootdir,targetname):
        targetlist=[]
        for root, dirs, files in os.walk(rootdir):
            if len(files)!=0:
                for fname in files:
                    fullpath=os.path.join(root, fname)
                if fname==targetname:
                    print(fullpath)
                    targetlist.append(fullpath)
            else:
                continue
            
        return targetlist

    def findAllFiles(self,root_path):
        for root, dirs, files in os.walk(root_path):
            yield root
            for file in files:
                yield os.path.join(root, file)

    def findDirs(self):
        for dirpath, dirnames, files in os.walk(self.path):
            return dirnames

    def findPathsInclude(self,keywords):
        rtn_list=[]
        for dirpath, dirnames, files in os.walk(self.path):
            for keyword in keywords:
                if dirpath.rfind(keyword)!=-1:
                    rtn_list.append(dirpath)
                print(dirnames)
                if dirnames.rfind(keyword)!=-1:
                    rtn_list.append(dirpath)
                print(files)
                if files.rfind(keyword)!=-1:
                    rtn_list.append(dirpath)
                print("dirnames=",dirnames)
                print("files=",files)

    def findAllDirs(self):
        for dirpath, dirnames, files in os.walk(self.path):
            for dir in dirnames:
                dirlist="%s/%s/"%(dirpath,dir)
                yield dirlist

    def findTargetDirDeep(self,targetdir):
        listdir=[]
        endwith_str="%s/"%targetdir
        dirlist=self.findAllDirs()
        for tmp_dir in dirlist:
            if tmp_dir.endswith(endwith_str)==True:
                listdir.append(tmp_dir)
        return listdir

if __name__ == "__main__":
    #print dp.roundMakeDir("data")
    #print dp.makeRoundDir("data",ndigit = 4)

    dir_prefix = "scan"
    #print dp.makeRoundDir(dir_prefix, isMake = False, ndigit=2)
    #dp.makeRoundDir(dir_prefix, isMake = True, ndigit=2,option='tail')
    #dp.roundMakeDirMaster(dir_prefix, ndigit = 3, option = "tail", isMake = True)
    check_dir = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Log/190520/025_sample/"
    dp=DirectoryProc(check_dir)
    #print dp.getRoundHeadPrefix(dir_prefix, "png", ndigit = 4)
    prefix = "raster"
    suffix = "jpg"
    #print dp.getRoundHeadPrefix(ndigit=4)

    print(dp.getRoundHeadPrefix(ndigit=4))

    #def getRoundHeadPrefix(self, prefix, suffix, ndigit=4):

    #def roundDir(self, dir_prefix):
    #dlist=dp.getDirList()
    #dlist.sort()
    #j.for d in dlist:
        #j.print d
    #dp.findTarget("xscale.mtz")
    #keywords=["run","final"]
    #print dp.findPathsInclude(keywords)

    # _kamoproc directory
    #dlist.sort()
    #for d in dlist:
    #print d
    #lll= dp.findTargetFileIn(d,"XDS_ASCII.HKL")
    #print lll

    #print dp.findTargetWith("sch")
    #print dp.findTargetFileInTargetDirectories("data","sch","_kamoproc")
