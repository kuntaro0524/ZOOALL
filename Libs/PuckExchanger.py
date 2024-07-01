# coding: utf-8
import os
import sys
sys.path.append("../")
import Zoo
import datetime
import pandas as pd
import logging
import logging.config

class PuckExchanger():
    def __init__(self, zoo):
        self.isCheck = False
        self.nmax_cane = 6
        self.nmax_pucks = self.nmax_cane * 7
        self.updated_time = datetime.datetime.now()
        self.puck_in_PE = []

        # Flag for a check of stored pucks
        self.isStored = False
        self.zoo = zoo

        # logger
        self.logger = logging.getLogger('ZOO').getChild('PuckExchanger')

    # このクラスの中ではCSVから読んだパック情報は重複を許さないリストとして良い
    # このあと python の set で集合体を扱うのでこの時点でsetにしていても良い気がする
    # ここで読む対象となっているCSVファイルはZOOPREPを書き下した最終のCSVのはずなので
    # 重複するパックもないはずか
    # いったんこのままリストとしてクラス変数としてもつことにする 2022/09/29
    def readPuckInfoFromCSV(self, csvfile):
        self.puck_df = pd.read_csv(csvfile)
        # self.logger(self.puck_df)
        self.schedule_pucks = self.puck_df['puckid']
        self.logger.info("Scheduling pucks %s" % self.schedule_pucks)

        return self.schedule_pucks

    # パックがSPACEの中に入っているかどうかを調査する
    def isPuckInList(self, target_puck, search_list):
        for puck_checking in search_list:
            print("checking:", puck_checking)
            if puck_checking.rfind("Not-Mount") != -1:
                self.logger.info("This is not checked.")
                continue
            elif puck_checking == target_puck:
                self.logger.info(
                    "%s is already in the list." % puck_checking)
                return True

        # 見つからなかった場合
        return False

    # スケジュールされたPuckリストとSPACEの中にいるパックのリストから
    # 今回何もしないパックリストと今回マウントしないといけないものを選択ｋ
    def groupMountUnmountPucks(self, scheduled_pucks, pucks_in_space):
        # Non-touch pucks
        non_touch_pucks = []
        # residual pucks
        pucks_to_be_mounted = []
        # Check if scheduled pucks are in SPACE dewar now.
        for scheduled_puck in scheduled_pucks:
            print("checking puck ID =", scheduled_puck)
            # SPACEの中に scheduled_puckがあるかどうか
            non_touch_flag = self.isPuckInList(scheduled_puck, pucks_in_space)

            # non_touch_flag が False: SPACE中にパックがなかったことを意味している
            if non_touch_flag == False:
                self.logger.info(
                    "%s is added to the mounting puck list." % scheduled_puck)
                pucks_to_be_mounted.append(scheduled_puck)
            else:
                non_touch_pucks.apppend(scheduled_puck)

        return non_touch_pucks, pucks_to_be_mounted

    # ここまでで新たなスケジュールから得たパックのリストを
    # マウントするべきもののリスト
    # 触らずに放置するべきもののリスト　
    # に分類したので、アンマウントするリストを作成する
    def listUnmountPucks(self, pucks_in_space, pucks_to_be_mounted, non_touch_pucks):
        # To be unmounted
        pucks_to_be_unmounted = []
        # mount するパックが0でなかった場合
        if len(pucks_to_be_mounted) != 0:
            # SPACEに入っているパックについて
            for puck_in_space in pucks_in_space:
                # マウントされていなかったらスキップ
                if puck_in_space.rfind("Not-Mount") != -1:
                    self.logger.info("skipping this position")
                    continue
                # Non touch pucks
                isNonTouch = False
                # Non touch puck の中にこのパックがあれば
                if puck_in_space in non_touch_pucks:
                    self.logger.info("This puck is 'non-touch' pucks.")
                    # Non touch flag is set to true
                    isNonTouch = True
                    continue
                # Pucks to be mounted
                isToBeMounted = False
                if puck_in_space in pucks_to_be_mounted:
                    # self.logger.info("This puck will come from PE from now: %s" % puck_to_be_mounted)
                    isToBeMounted = True
                    continue

                if isNonTouch == False and isToBeMounted == False:
                    self.logger.info(
                        "%s should be removed from SPACE dewar" % puck_in_space)
                    pucks_to_be_unmounted.append(puck_in_space)

        return pucks_to_be_unmounted

    def groupPucksForNext(self, pucks_in_schedule, pucks_in_space):
        # python set　に変換
        pucks_in_schedule_set = set(pucks_in_schedule)

        new_pucks=[]
        for puck in pucks_in_space:
            if "Not-Mounted" in puck:
                print("Skipping")
            else:
                new_pucks.append(puck)

        pucks_in_space_set = set(new_pucks)

        # 今回触らないパック
        remain_pucks_set = pucks_in_space_set & pucks_in_schedule_set
        # これからマウントしないといけないパック
        mounting_pucks_set = pucks_in_schedule_set - remain_pucks_set
        # これからアンマウントするパック
        unmounting_pucks_set = pucks_in_space_set - remain_pucks_set

        # listに戻してから返却する
        return list(remain_pucks_set), list(mounting_pucks_set), list(unmounting_pucks_set)

    def checkCurrentPucks(self, csvfile):
        # Read puck IDs in the dewar.
        pucks_in_space = self.zoo.getSampleInformation()
        scheduled_pucks = self.readPuckInfoFromCSV(csvfile)


        print("Pucks in SPACE=", pucks_in_space)
        print("Scheduled pucks=", scheduled_pucks)

        #今回触らないやつ、マウントするやつ、アンマウントするやつの仕分け
        remain_pucks, mounting_pucks, unmounting_pucks = self.groupPucksForNext(
            scheduled_pucks, pucks_in_space)

        # Check the number of pucks to be mounted from now.
        n_mounting = len(mounting_pucks)
        n_unmounting = len(unmounting_pucks)
        n_remain = len(remain_pucks)

        self.logger.info("%5d pucks will be   mounted from now" %
                         n_mounting)
        self.logger.info("%5d pucks will be unmounted from now" %
                         n_unmounting)
        self.logger.info("%5d pucks will be left as they are" %
                         n_remain)

        return mounting_pucks, unmounting_pucks

    def checkCurrentPucksAndMount(self, csvfile):
        pucks_to_be_mounted, pucks_to_be_unmounted = self.checkCurrentPucks(
            csvfile)

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

        tmp_dic = {}
        for index in range(1, self.nmax_pucks+1):
            puck = self.zoo.pe_get_puck(index)
            if puck != "Not-Mounted":
                self.puck_in_PE.append(puck)
                self.n_stored += 1

        self.updatedTime = datetime.datetime.now()
        self.isStored = True

        return(self.puck_in_PE)

    def isPuckIn(self, puckid):
        if not self.isStored:
            self.getAllPuckInfoPE()

        for stored_puck in self.puck_in_PE:
            if puckid == stored_puck:
                return True
        return False


if __name__ == "__main__":
    sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
    #logname = "/isilon/users/admin45/admin45/2020B/210215_ZOOPEtest/zoo.log"
    logname = "/isilon/users/admin45/admin45/Staff/220301-puckexchange/zoo.log"
    print "changing mode of %s" % logname
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})

    import Zoo
    zoo=Zoo.Zoo()
    zoo.connect()

    pe=PuckExchanger(zoo)
    #mount_list, unmount_list=pe.checkCurrentPucks(sys.argv[1])
    #print("  mountlist=", mount_list)
    #print("unmountlist=", unmount_list)
    pe.unmountAllpucksFromSPACE()
