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
        # header check
        if 'puckid' not in self.puck_df.columns:
            raise RuntimeError("CSV file must contain 'puckid' column.")

        self.schedule_pucks = self.puck_df['puckid']
        # self.schedule_pucks -> 重複をなくす
        self.schedule_pucks = list(dict.fromkeys(self.schedule_pucks))
        self.schedule_pucks = [str(puck) for puck in self.schedule_pucks if
                                str(puck) != "nan" and str(puck) != ""]

        self.logger.info("Scheduling pucks %s" % self.schedule_pucks)

        return self.schedule_pucks

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
        # 初期化する
        self.puck_in_PE = []
        for index in range(1, self.nmax_pucks+1):
            puck=self.zoo.pe_get_puck(index)
            if ("Not-Mount" not in puck) and ("Not-Mounted" not in puck):
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

    # Coded by Chatgpt 251020 K.Hirata
    # 未搭載扱いの判定ヘルパ（仕様：コマンドの返答は "Not-Mount" or "Not-Mounted"）
    def _is_not_mounted(s: str) -> bool:
        return (s is None) or ("Not-Mount" in s) or ("Not-Mounted" in s)

    def _unique_keep_order(seq):
        seen=set(); out=[]
        for x in seq:
            if x not in seen:
                seen.add(x); out.append(x)
        return out

    def _get_space_pucks(self):
        # 既存のSPACE取得ロジックに合わせて、未搭載表現を除外
        info = self.zoo.getSampleInformation()  # 既存の取得関数を想定
        return [p for p in info if not _is_not_mounted(p)]

    def get_pe_pucks(self):
        # ★重要：毎回リセット（重複増殖防止）
        self.puck_in_PE = []
        for idx in range(1, self.nmax_pucks+1):
            p = self.zoo.pe_get_puck(idx)  # 既存関数を想定
            if not _is_not_mounted(p):
                self.puck_in_PE.append(p)
        self.isStored = True
        return self.puck_in_PE

    def _validate_planned_exist_in_pe(self, planned):
        pe_pucks = self.getAllPuckInfoPE()
        missing = [p for p in planned if p not in pe_pucks]
        if missing:
            # shows error message in English
            raise RuntimeError(f"The following planned pucks are not found in PE inventory: {missing}. Please check the CSV file and PE status.")

    def _get_planned_from_csv(self, csv_path: str):
        puck_list = self.readPuckInfoFromCSV(csv_path)

        seen = set()
        planned = []
        for puck in puck_list:
            if puck and puck not in seen:
                seen.add(puck)
                planned.append(puck)

        return planned

    def plan_exchange(self, planned, space_pucks, capacity=8):
        # すでにSPACEに入っていて必要なものは残す（keep）
        keep = [p for p in space_pucks if p in planned]
        # SPACEにあるが不要なものは外す
        to_unmount = [p for p in space_pucks if p not in planned]
        # 必要だがSPACEに無いものは入れる対象
        need_mount = [p for p in planned if p not in keep]

        # 枠計算：keep + mount ≤ capacity
        free_slots = capacity - len(keep)
        if free_slots < 0:
            # ありえないが安全側：keepをcapacityまでに間引きし、外す側へ回す
            overflow = -free_slots
            to_unmount = keep[-overflow:] + to_unmount
            keep = keep[:capacity]
            free_slots = 0
        if len(need_mount) > free_slots:
            # まず不要（to_unmount）を外して枠を作る前提。足りなければエラー。
            if len(need_mount) - free_slots > len(to_unmount):
                raise RuntimeError("8枠に収まりません。計画を見直してください。")
            # to_unmountを外せば枠は作れる → 明示的な変更不要（実行時に先に外す）
        return need_mount, to_unmount, keep

    def execute_exchange(self, to_unmount, to_mount):
        # 先に外す（SPACE→PE）
        for p in to_unmount:
            self.logger.info(f"unmount {p}")
            self.zoo.pe_unmount_puck(p)  # 既存のアンマウント呼び出しに合わせる
        # 次に入れる（PE→SPACE）
        for p in to_mount:
            self.logger.info(f"mount {p}")
            self.zoo.pe_mount_puck(p)    # 既存のマウント呼び出しに合わせる

    def checkCurrentPucksAndMount(self, csv_path:str, dry_run:bool=False):
        planned = self._get_planned_from_csv(csv_path)
        pe_pucks = self.getAllPuckInfoPE()
        self._validate_planned_exist_in_pe(planned)

        cur = self.zoo.getSampleInformation()
        space_pucks = [p for p in cur if ("Not-Mount" not in p) and ("Not-Mounted" not in p)]

        keep = [p for p in space_pucks if p in planned]
        to_unmount = [p for p in space_pucks if p not in planned]
        to_mount = [p for p in planned if p not in keep]

        # plan
        plan = {"keep": keep, "to_unmount": to_unmount, "to_mount": to_mount}

        # return dry run info
        if dry_run:
            return plan

        final_keep = [p for p in space_pucks if p not in to_unmount]
        free_slots = 8 - len(final_keep)
        if len(to_mount) > free_slots:
            raise RuntimeError("Not enough space to mount all scheduled pucks after unmounting. Please check the CSV file and current SPACE status.")
        
        for p in to_unmount:
            self.logger.info(f"unmount {p}")
            self.zoo.pe_unmount_puck(p)
        for p in to_mount:
            self.zoo.pe_mount_puck(p)

if __name__ == "__main__":
    import Zoo
    zoo=Zoo.Zoo()
    zoo.connect()

    logger = logging.getLogger('ZOO')
    logger.info("Start ZOO")
    # logfile
    logger.setLevel(logging.INFO)   
    logname = "puck_exchanger_test.log"
    fh = logging.FileHandler(logname)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    fh.setFormatter(formatter)
    logger.addHandler(fh)   

    pe=PuckExchanger(zoo)
    # dry run
    plan = pe.checkCurrentPucksAndMount(sys.argv[1], dry_run=True)
    logger.info(f"Dry run plan: {plan}")