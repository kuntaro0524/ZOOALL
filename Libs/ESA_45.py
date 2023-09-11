import sqlite3, csv, os, sys, copy
import MyException
import re


class ESA:
    def __init__(self, dbname):
        self.dbname = dbname
        self.n_cur = 0

        # ZOO schemes
        # 2019/04/17
        self.scheme_list = ["multi", "helical", "single", "mixed", "ssrox"]

    # For existing data base file
    def prepReadDB(self):
        self.db = sqlite3.connect(self.dbname)
        self.cur = self.db.cursor()
        self.n_cur += 1
        print("preparation succeeded")

    def getTableName(self):
        if self.n_cur == 0:
            self.prepReadDB()
        self.cur.execute("select name from sqlite_master where type='table'")
        params = self.cur.fetchall()
        print("getTableName:", params)

        if len(params) == 0:
            return "None"

        print(params)
        for catalog in params:
            self.tableName = catalog[0]
            columnIndex = 0

        return self.tableName

    def getColumnsName(self):
        self.cur.execute("PRAGMA table_info(my_tbl)")
        print(self.cur.fetchall())

        """
        self.db.row_factory = sqlite3.Row
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM %s'%self.tableName)
        for row in cursor.fetchall():
            print "ROW=",row
            #results.append(dict(x))
        """

        # Fetch one test
        self.cur.execute("SELECT * FROM %s" % self.tableName)
        row = self.cur.fetchone()
        print(row)

    def fetchOne(self):
        self.prepReadDB()
        self.cur.execute("SELECT * FROM ESA")
        rows = self.cur.fetchone()
        return rows

    def fetchAll(self):
        # anytime, this initialize the cursor because it should get all components
        # even though the defined cursor designates one of the components
        self.prepReadDB()
        self.cur.execute("SELECT * FROM ESA")
        result = self.cur.fetchall()
        index = 0
        """
            for row in result:
                print index, row
                index+=1
        """
        return result

    # Always RE-READ 'zoo.db' and make the corresponding dictionary
    def getDict(self):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM ESA")
        results = []
        for row in cur.fetchall():
            x = dict(list(zip([d[0] for d in cur.description], row)))
            results.append(x)
        return results

    def updateValue(self, paramname, value, condition):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        command = "update ESA set %s = %s %s" % (paramname, value, condition)
        # print command
        cur.execute(command)
        con.commit()

    def updateValueAt(self, p_index, paramname, value):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        condition = "where p_index=%d" % p_index
        command = "update ESA set %s = %s %s" % (paramname, value, condition)
        print(command)
        cur.execute(command)
        con.commit()

    def addIntegerList_TEST(self):
        CREATE_TABLE = """
        create table if not exists testtable (
            id integer primary key,
            intlist IntList
        );
        """
        IntList = list
        sqlite3.register_adapter(IntList, lambda I: ';'.join([str(i) for i in I]))
        sqlite3.register_converter("IntList", lambda s: [int(i) for i in s.split(';')])

        con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        con.execute(CREATE_TABLE)

        insert_list = [1, 2, 3]
        con.execute('insert into testtable values(?,?)', (1, insert_list))
        con.commit()

        cur = con.cursor()
        cur.execute('select * from testtable;')
        assert insert_list == cur.fetchone()['intlist']

    def listDB(self):
        # print self.dbname
        self.cur = sqlite3.connect(self.dbname).cursor()
        # getTablename
        self.getTableName()
        # Sansho
        sql = "select * from %s" % self.tableName
        self.cur.execute(sql)
        for row in self.cur:
            print(row[0], row[1], row[2])
            # sql="select * from "

    def save_csv(self, csvfile):
        cur = sqlite3.connect(self.dbname).cursor()
        cur.execute("select * from ESA")

        ofile = open(csvfile, "w")
        tags = cur.description

        for i in range(0, len(tags)):
            x = tags[i][0]
            ofile.write("%s" % x)
            if i != len(tags) - 1:
                ofile.write(",")
            else:
                ofile.write("\n")

        for result in cur:
            for i in range(0, len(result)):
                ofile.write("%s" % result[i])
                if i != len(result) - 1:
                    ofile.write(",")
                else:
                    ofile.write("\n")
        ofile.close()

    def isSkipped(self, p_index):
        curr_dic = self.getDict()
        for d in curr_dic:
            if d['p_index'] == p_index:
                if d['isSkip'] == 1:
                    return True
                else:
                    return False

    def incrementInt(self, p_index, param_name, value=1):
        curr_dic = self.getDict()
        curr_value = -99999
        for d in curr_dic:
            if d['p_index'] == p_index:
                curr_value = d[param_name]
        incremented_value = curr_value + value
        self.updateValueAt(p_index, param_name, incremented_value)

    def makeTable(self, csvfile, force_to_make=False):
        # Does db file exist or not.
        if self.getTableName() != "None":
            print("DB exists")
            if force_to_make == True:
                print("Removing the existing ESA")
                self.cur.execute("drop table ESA")
            else:
                print("Nothings done")
                return

        # 190702 Added parameters
        # o_index: original prior index for tracing the final results
        #
        # Making the ESA table
        self.cur.execute("""CREATE TABLE ESA
        (root_dir char,
        o_index int,
        p_index int,
        mode char,
        puckid char,
        pinid int,
        sample_name char,
        wavelength float, 
        raster_vbeam float, 
        raster_hbeam float,
        att_raster float,
        hebi_att float,
        exp_raster float,
        dist_raster float,
        loopsize float,
        score_min float,
        score_max float,
        maxhits int,
        total_osc float,
        osc_width float,
        ds_vbeam float, 
        ds_hbeam float,
        exp_ds float,
        dist_ds float,
        dose_ds float,
        offset_angle float,
        reduced_fact float,
        ntimes int,
        meas_name char,
        cry_min_size_um float,
        cry_max_size_um float,
        hel_full_osc float,
        hel_part_osc float,
        raster_roi int,
        isSkip int,
        isMount int,
        isLoopCenter int,
        isRaster int,
        isDS int,  
        scan_height float,
        scan_width float,
        n_mount int,
        nds_multi int,
        nds_helical int,
        nds_helpart int,
        t_meas_start str,
        t_mount_end str,
        t_cent_start str,
        t_cent_end str,
        t_raster_start str,
        t_raster_end str,
        t_ds_start str,
        t_ds_end str,
        t_dismount_start str,
        t_dismount_end str,
        data_index int,
        n_mount_fails int,
        log_mount str,
        hel_cry_size float,
        flux float,
        phs_per_deg float
        )""")

        try:
            condition_list = self.readCSV(csvfile)
            print("KKKKKKK")
            db_list = self.makeDBlist(condition_list)
            for cond in db_list:
                self.cur.execute(
                    'INSERT INTO ESA VALUES (\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?);', cond)

                self.db.commit()
            self.db.close()

        except Exception as ex:
            print(ex)
            return []

    # makeTable

    def makeDBlist(self, condition_list):
        # condition_list is same format on CSV file
        # and should be modified for current DB format
        return_list = []
        for p in condition_list:
            c = copy.copy(p)
            # making o_index for saving the initial sequence
            p_index = c[1]
            c.insert(1, p_index)
            # Append log information
            # isSkip
            c.append(0)  # isSkip
            c.append(0)  # isMount
            c.append(0)  # isLoopCenter
            c.append(0)  # isRaster
            c.append(0)  # isDS
            c.append(0.0)  # scan_height
            c.append(0.0)  # scan_width
            c.append(0)  # n_mount
            c.append(0)  # nds_multi
            c.append(0)  # nds_helical
            c.append(0)  # nds_helpart
            c.append("0")  # t_meas_start
            c.append("0")  # t_mount_end
            c.append("0")  # t_cent_start
            c.append("0")  # t_cent_end
            c.append("0")  # t_raster_start
            c.append("0")  # t_raster_end
            c.append("0")  # t_ds_start
            c.append("0")  # t_ds_end
            c.append("0")  # t_dismount_start
            c.append("0")  # t_dismount_end
            c.append(0)  # data_index
            c.append(0)  # n_mount_fails
            c.append("0")  # log_mount
            c.append(0.0)  # hel_cry_size
            c.append(0.0)  # flux
            c.append(0.0)  # phs_per_deg

            return_list.append(c)

        return return_list

    def analyzePinList(self, pin_char):
        pinid_list = []
        # cols = pin_char.split(".+")
        cols = re.split('[.+;]', pin_char)
        for col in cols:
            if col.rfind("-") != -1:
                print("COL = ", col)
                startnum = int(col.split("-")[0])
                endnum = int(col.split("-")[1])
                for i in range(startnum, endnum + 1):
                    pinid_list.append(i)
            else:
                pinid_list.append(int(col))
        print(pinid_list)
        return pinid_list

    def readCSV(self, csvfile):
        process_index = 0
        # index of pin ID = 3
        condition_list = []
        with open(csvfile, 'rb') as f:
            b = csv.reader(f)
            header = next(b)
            for t in b:
                print("PINID part=", t[4])
                pinid_list = self.analyzePinList(t[4])

                for pinid in pinid_list:
                    t[1] = process_index
                    t[4] = pinid
                    p = copy.copy(t)
                    print("LEN in CSV=", len(t))
                    print("T=", t)
                    condition_list.append(p)
                    process_index += 1

        # Check duplication
        len_cond = len(condition_list)
        for i in range(0, len_cond):
            check_cond = condition_list[i]
            check_root = check_cond[0]
            check_puck = check_cond[3]
            check_pin = check_cond[4]
            for j in range(i + 1, len_cond):
                tmp_cond = condition_list[j]
                tmp_root = tmp_cond[0]
                tmp_puck = tmp_cond[3]
                tmp_pin = tmp_cond[4]
                if tmp_puck == check_puck and tmp_pin == check_pin and check_root == tmp_root:
                    msg = "Duplication in CSV file: %s-%s and %s-%s. Please fix it!\n" % (
                        check_puck, check_pin, tmp_puck, tmp_pin)
                    print(msg)
                    raise MyException.MyException(msg)

        # experimental scheme check
        for cond in condition_list:
            ok_flag = False
            for scheme in self.scheme_list:
                if scheme == cond[2].lower():
                    # print cond[1],cond[2],cond[3],"Okay"
                    ok_flag = True
                    break
                # SSROX made kiteitara error
                if scheme == "ssrox":
                    msg = "No such experimental scheme!! %s-%s : >> %s << Please fix it!\n" % (
                        cond[3], cond[4], cond[2])
                    raise MyException.MyException(msg)
        # Check Mode

        return condition_list

    # This code was got from WEB and currently I cannot understand.
    # But someday, it will be good for me
    def conditionGet(self):
        self.cur.execute('SELECT wavelength, exp_time, raster_vbeam FROM ESA WHERE raster_hbeam < 20;')
        for row in self.cur:
            print(row)

    def choufukunashiGet(self):
        # Chouhuku nashi rekkyo
        self.cur.execute('SELECT DISTINCT wavelength FROM ESA;')
        print("DISTINCE=", self.cur.fetchall())

    def getParam(self):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        condition = "where p_index=%d" % p_index
        command = "update ESA set %s = %s %s" % (paramname, value, condition)
        print(command)
        cur.execute(command)
        con.commit()


if __name__ == "__main__":
    esa = ESA(sys.argv[1])
    # esa.readCSV(sys.argv[2])
    # esa.makeTable(sys.argv[2],force_to_make=True)
    # esa.prepReadDB()
    # esa.getTableName()
    # esa.listDB()
    # esa.fetchAll()
    print("BEFORE")
    ppp = esa.getDict()
    print("LNE=", len(ppp))
    for p in ppp:
        print(p)
        print("SCAN_WIDTH=", p['scan_width'])
        print("n_mount=", p['n_mount'])
        print("nds_multi=", p['nds_multi'])
        print("nds_helical=", p['nds_helical'])
        print("nds_helpart=", p['nds_helpart'])
        print("t_meas_start=", p['t_meas_start'])
        print("t_mount_end=", p['t_mount_end'])
        print("t_cent_start=", p['t_cent_start'])
        print("t_cent_end=", p['t_cent_end'])
        print("t_raster_start=", p['t_raster_start'])
        print("t_raster_end=", p['t_raster_end'])
        print("t_ds_start=", p['t_ds_start'])
        print("t_ds_end=", p['t_ds_end'])
        print("t_dismount_start=", p['t_dismount_start'])
