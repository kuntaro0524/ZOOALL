import os,sys
import datetime
import pandas as pd
import logging
import logging.config

class PuckExchanger():
    def __init__(self, zoo):
        self.isCheck=False
        self.nmax_cane = 6
        self.nmax_pucks=self.nmax_cane * 7
        self.updated_time=datetime.datetime.now()
        self.puck_in_PE=[]

        # Flag for a check of stored pucks
        self.isStored=False
        self.zoo=zoo

        # logger
        self.logger = logging.getLogger('ZOO').getChild('PuckExchanger')

    def readPuckInfoFromCSV(self, csvfile):
        self.puck_df = pd.read_csv(csvfile)
        # self.logger(self.puck_df)
        self.schedule_pucks = self.puck_df['puckid']
        self.logger.info("Scheduling pucks %s" % self.schedule_pucks)

        return self.schedule_pucks

    def checkCurrentPucks(self, csvfile):
        # Read puck IDs in the dewar.
        pucks_in_space=self.zoo.getSampleInformation()
        scheduled_pucks=self.readPuckInfoFromCSV(csvfile)

        print("Pucks in SPACE=", pucks_in_space)
        print("Scheduled pucks=", scheduled_pucks)

        # Non-touch pucks
        non_touch_pucks=[]
        # residual pucks
        to_be_mounted = []

        # Check if scheduled pucks are in SPACE dewar now.
        for scheduled_puck in scheduled_pucks:
            print("SCHE=",scheduled_puck)
            non_touch_flag=False
            for puck_in_space in pucks_in_space:
                print("PINSPA=",puck_in_space)
                if puck_in_space.rfind("Not-Mount")!=-1:
                    self.logger.info("%s is not mounted" % puck_in_space)
                    continue
                elif puck_in_space==scheduled_puck:
                    self.logger.info("%s is already in SPACE dewar." % puck_in_space)
                    non_touch_pucks.append(puck_in_space)
                    non_touch_flag=True
                    break

            if non_touch_flag==False:
                self.logger.info("%s is added to the mounting puck list." % scheduled_puck)
                to_be_mounted.append(scheduled_puck)

        # To be unmounted
        to_be_unmounted=[]
        if len(to_be_mounted) != 0:
            for puck_in_space in pucks_in_space:
                if puck_in_space.rfind("Not-Mount")!=-1:
                    self.logger.info("%s: skipping" % puck_in_space)
                    continue
                # Non touch pucks
                for non_touch_puck in non_touch_pucks:
                    if puck_in_space==non_touch_puck:
                        self.logger.info("This puck is 'non-touch' pucks.")
                        continue
                for puck_to_be_mounted in to_be_mounted:
                    if puck_to_be_mounted == puck_in_space:
                        # self.logger.info("This puck will come from PE from now: %s" % puck_to_be_mounted)
                        continue
                self.logger.info("%s should be removed from SPACE dewar" % puck_in_space)
                to_be_unmounted.append(puck_in_space)

        # Check the number of pucks to be mounted from now.
        n_pucks_to_be_mount=len(to_be_mounted)
        n_pucks_to_be_unmounted=len(to_be_unmounted)
        n_non_touch_pucks=len(non_touch_pucks)

        self.logger.info("%5d pucks will be   mounted from now" % n_pucks_to_be_mount)
        self.logger.info("%5d pucks will be unmounted from now" % n_pucks_to_be_unmounted)
        self.logger.info("%5d pucks will be left as they are" % n_non_touch_pucks)

        return to_be_mounted, to_be_unmounted

    def checkCurrentPucksAndMount(self, csvfile):
        pucks_to_be_mounted, pucks_to_be_unmounted = self.checkCurrentPucks(csvfile)

        # Unmounting pucks
        if len(pucks_to_be_unmounted) == 0:
            self.logger.info("Unmounting is not required now!")
        else:
            self.logger.info("Unmounting will be applied...")
            for unmounting_puck in pucks_to_be_unmounted:
                self.logger.info("unmounting %s" % unmounting_puck)
                self.zoo.pe_unmount_puck(unmounting_puck)

        # Mounting pucks
        if len(pucks_to_be_mounted) <= 8 and len(pucks_to_be_mounted) > 0:
            for puckid in pucks_to_be_mounted:
                self.zoo.pe_mount_puck(puckid)
        elif len(pucks_to_be_mounted) > 8:
            self.logger.info("The number of pucks exceeds 8! Error")
            return False
        else:
            self.logger.info("Pucks on the CSV are already mounted.")
            self.logger.info("or CSV file is empty.")
            return False

    def mountAllonCSV(self, csvfile):
        # First unount all pucks in SPACE
        self.unmountAllpucksFromSPACE()

        # Read CSV file and store puck information
        self.readPuckInfoFromCSV(csvfile)

        if len(self.schedule_pucks) >= 8:
            self.logger.error("Too many pucks!!")
            sys.exit()

        for puckid in self.schedule_pucks:
            self.logger.info("mounting %s" % puckid)
            # check if it is on PE.
            if self.isPuckIn(puckid):
                self.zoo.pe_mount_puck(puckid)
            else:
                self.logger.error("Puck is in CSV and it is not mounted on PE")

        self.logger.info("Puck mount from PE finished.")

    def unmountAllpucksFromSPACE(self):
        curr_pucks = self.zoo.getSampleInformation()

        for unmounting_puck in curr_pucks:
            if not "Not-Mounted" in unmounting_puck:
                self.logger.info("unmounting %s" % unmounting_puck)
                self.zoo.pe_unmount_puck(unmounting_puck)

    def getAllPuckInfoPE(self):
        self.n_stored = 0

        tmp_dic={}
        for index in range(1, self.nmax_pucks+1):
            puck=self.zoo.pe_get_puck(index)
            if puck!="Not-Mounted":
                self.puck_in_PE.append(puck)
                self.n_stored+=1

        self.updatedTime=datetime.datetime.now()
        self.isStored=True

        return(self.puck_in_PE)

    def isPuckIn(self, puckid):
        if not self.isStored: self.getAllPuckInfoPE()

        for stored_puck in self.puck_in_PE:
            if puckid==stored_puck:
                return True
        return False

if __name__ == "__main__":
    sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
    logname = "/isilon/users/admin45/admin45/2020B/210215_ZOOPEtest/zoo.log"
    print "changing mode of %s" % logname
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})

    import Zoo
    zoo=Zoo.Zoo()
    zoo.connect()

    pe=PuckExchanger(zoo)
    mount_list, unmount_list=pe.checkCurrentPucks(sys.argv[1])
    print("  mountlist=", mount_list)
    print("unmountlist=", unmount_list)
