import sqlite3, csv, os, sys

class ESA:
    def __init__(self, dbname):
        self.dbname = dbname
        self.n_cur=0

    # For existing data base file
    def prepReadDB(self):
        self.db = sqlite3.connect(self.dbname)
        self.cur = self.db.cursor()
        self.n_cur+=1
        print "preparation succeeded"

    def getTableName(self):
        if self.n_cur==0:
            self.prepReadDB()
        self.cur.execute("select name from sqlite_master where type='table'")
        params = self.cur.fetchall()
        print "getTableName:",params

        if len(params) == 0:
            return "None"

        print params
        for catalog in params:
            self.tableName = catalog[0]
            columnIndex = 0

        return self.tableName

    def getColumnsName(self):
        self.cur.execute("PRAGMA table_info(my_tbl)")
        print self.cur.fetchall()

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
        print row

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
        result=self.cur.fetchall()
        index=0
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
            x = dict(zip([d[0] for d in cur.description], row))
            results.append(x)
        return results

    def updateValue(self,paramname,value,condition):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        command="update ESA set %s = %s %s"%(paramname,value,condition)
        #print command
        cur.execute(command)
        con.commit()

    def updateValueAt(self,p_index,paramname,value):
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        condition="where p_index=%d"%p_index
        command="update ESA set %s = %s %s"%(paramname,value,condition)
        print command
        cur.execute(command)
        con.commit()

    def addIntegerList_TEST(self):
        CREATE_TABLE=u"""
        create table if not exists testtable (
            id integer primary key,
            intlist IntList
        );
        """
        IntList = list
        sqlite3.register_adapter(IntList,lambda I: ';'.join([str(i) for i in I]))
        sqlite3.register_converter("IntList",lambda s:[int(i) for i in s.split(';')])

        con=sqlite3.connect(":memory:",detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory=sqlite3.Row
        con.execute(CREATE_TABLE)

        insert_list=[1,2,3]
        con.execute(u'insert into testtable values(?,?)',(1, insert_list))
        con.commit()

        cur=con.cursor()
        cur.execute(u'select * from testtable;')
        assert insert_list==cur.fetchone()['intlist']

    def listDB(self):
        # print self.dbname
        self.cur = sqlite3.connect(self.dbname).cursor()
        # getTablename
        self.getTableName()
        # Sansho
        sql = "select * from %s" % self.tableName
        self.cur.execute(sql)
        for row in self.cur:
            print row[0], row[1], row[2]
            # sql="select * from "

    def save_csv(self,csvfile):
        cur = sqlite3.connect(self.dbname).cursor()
        cur.execute("select * from ESA")

        ofile=open(csvfile,"w")
        tags=cur.description

        for i in range(0,len(tags)):
            x=tags[i][0]
            ofile.write("%s"%x)
            if i != len(tags)-1:
                ofile.write(",")
            else:
                ofile.write("\n")

        for result in cur:
            for i in range(0,len(result)):
                ofile.write("%s"%result[i])
                if i != len(result)-1:
                    ofile.write(",")
                else:
                    ofile.write("\n")
        ofile.close()

    def isSkipped(self,p_index):
        curr_dic=self.getDict()
        for d in curr_dic:
            if d['p_index']==p_index:
                if d['isSkip']==1:
                    return True
                else:
                    return False

    def incrementInt(self,p_index,param_name,value=1):
        curr_dic=self.getDict()
        curr_value=-99999
        for d in curr_dic:
            if d['p_index']==p_index:
                curr_value=d[param_name]
        incremented_value=curr_value+value
        self.updateValueAt(p_index,param_name,incremented_value)

    def makeTable(self, csvfile, force_to_make=False):
        # Does db file exist or not.
        if self.getTableName() != "None":
            print "DB exists"
            if force_to_make==True:
                print "Removing the existing ESA"
                self.cur.execute("drop table ESA")
            else:
                print "Nothings done"
                return

        # Making the ESA table
        self.cur.execute("""CREATE TABLE ESA
        (root_dir char,
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
        loopsize char,
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
        t_dismount_end str
        )""")

        process_index=0
        with open(csvfile, 'rb') as f:
            b = csv.reader(f)
            header = next(b)
            for t in b:
                t[1]=process_index
                print "PROCESS_INDEX=",process_index
                self.cur.execute(
                    'INSERT INTO ESA VALUES (\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?,?,?,?,?,?,?,?,\
                        ?,?,?);',t)
                process_index+=1

   	    self.db.commit()
        self.db.close()

    # This code was got from WEB and currently I cannot understand.
    # But someday, it will be good for me
    def conditionGet(self):
        self.cur.execute('SELECT wavelength, exp_time, raster_vbeam FROM ESA WHERE raster_hbeam < 20;')
        for row in self.cur:
            print row

    def choufukunashiGet(self):
        # Chouhuku nashi rekkyo
        self.cur.execute('SELECT DISTINCT wavelength FROM ESA;')
        print "DISTINCE=",self.cur.fetchall()

if __name__ == "__main__":
    esa = ESA(sys.argv[1])
    esa.getTableName()
    esa.listDB()

    print "BEFORE"
    ppp = esa.getDict()
    print "LNE=",len(ppp)
    for p in ppp:
        print p
        print "SCAN_WIDTH=",p['scan_width']
        print "n_mount=",p['n_mount']
        print "nds_multi=",p['nds_multi']
        print "nds_helical=",p['nds_helical']
        print "nds_helpart=",p['nds_helpart']
        print "t_meas_start=",p['t_meas_start']
        print "t_mount_end=",p['t_mount_end']
        print "t_cent_start=",p['t_cent_start']
        print "t_cent_end=",p['t_cent_end']
        print "t_raster_start=",p['t_raster_start']
        print "t_raster_end=",p['t_raster_end']
        print "t_ds_start=",p['t_ds_start']
        print "t_ds_end=",p['t_ds_end']
        print "t_dismount_start=",p['t_dismount_start']
