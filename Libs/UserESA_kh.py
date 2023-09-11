import sys, os, math, numpy
import BeamsizeConfig

# For version 1.0 2019/06/14 coded by K. Hirata
# Updated on 2019/11/1 for beam size settings. K. Hirata.
# Updated on 2019/11/07 for including 'ln2_flag' etc. for BL45XU

class UserESA():
    def __init__(self, csvfile, root_dir, beamline = "BL32XU"):
        self.beamline = beamline
        self.csvfile = csvfile
        self.cols = []
        self.isRead = False
        self.isPrep = False
        self.isGot = False
        self.contents = []
        self.root_dir = root_dir

        # Beamsize config
        sys.path.append("/isilon/%s/BLsoft/PPPP/10.Zoo/Libs")
        import BeamsizeConfig
        self.confdir = "/isilon/blconfig/%s/" % beamline.lower()
        self.bsconf = BeamsizeConfig.BeamsizeConfig(self.confdir)

    def read(self):
        self.lines = open(self.csvfile, "r").readlines()
        for line in self.lines:
            cols = line.split(',')
            self.cols.append(cols)

        self.isRead = True

    def printCols(self):
        if self.isRead == False:
            self.read()
        for cols in self.cols:
            print(cols)

    def extractRealList(self):
        if self.isRead == False:
            self.read()
        contents_index = 0
        save_start = 0
        for cols in self.cols:
            contents_index += 1
            if cols[0] == "PuckID":
                save_start = contents_index
            if save_start != 0 and len(cols[0]):
                save_end = contents_index
        contents_start = save_start
        contents_end = save_end
        for cols in self.cols[contents_start:contents_end]:
            self.contents.append(cols)

        self.isPrep = True

    def calcDist(self, wavelength, resolution_limit):
        if self.beamline.lower() == "bl32xu":
            # EIGER X 9M
            min_dim = 233.0 #mm
        elif self.beamline.lower() == "bl45xu":
            # PILATUS 6M
            min_dim = 422.0 #mm
        theta = numpy.arcsin(wavelength / 2.0 / resolution_limit)
        bunbo = 2.0 * numpy.tan(2.0 * theta)
        camera_len = min_dim / bunbo
        return camera_len

    def check_beamsize(self, beamsize_char):
        cols = beamsize_char.split('x')
        if len(cols) == 2:
            hbeam = float(cols[0])
            vbeam = float(cols[1])
            return hbeam, vbeam
        else:
            hbeam = float(cols[0])
            vbeam = float(cols[1])
            return hbeam, vbeam

    def getParams(self, desired_exp_string, type_crystal, mode):
        type_crystal = type_crystal.lower().strip()
        dose_ds = 10.0
        # Default value of raster ROI -> small
        raster_roi = 1
        desired_exp_string = desired_exp_string.lower()
        #print "LOWER=",desired_exp_string
        # Default
        if self.beamline.lower() == "bl32xu":
            exp_raster = 0.01
            att_raster = 25.0
            hebi_att = 25.0

        if self.beamline.lower() == "bl45xu":
            exp_raster = 0.02
            att_raster = 25.0
            hebi_att = 25.0

        if desired_exp_string == "check_diffraction":
            raster_dose = 0.3
            score_min = 10000
            score_max = 10000
            raster_roi = 0

        elif desired_exp_string == "improve_resolution":
            raster_dose = 0.05
            if type_crystal == "lcp" or type_crystal == "sponge":
                raster_dose = 0.1
                att_raster = 100.0
                hebi_att = 100.0
                score_min = 15
                score_max = 100
            elif type_crystal == "soluble":
                #print "GETTTTTTTTTTTTTTTTTTTT"
                score_min = 25
                score_max = 100
        elif desired_exp_string == "unknown_crystals":
            raster_dose = 0.05
            score_min = 10000
            score_max = 10000
            raster_roi = 0
        elif desired_exp_string == "normal_collection":
            if type_crystal == "lcp" or type_crystal == "sponge":
                att_raster = 100.0
                hebi_att = 100.0
                raster_dose = 0.2
                score_min = 10
                score_max = 100
            elif type_crystal == "soluble":
                raster_dose = 0.1
                score_min = 10
                score_max = 100
                if mode == "helical":
                    raster_dose = raster_dose / 2.0
                    score_max = 9999
            elif type_crystal == "membrane":
                raster_dose = 0.2
                score_min = 10
                score_max = 100
                if mode == "helical":
                    raster_dose = raster_dose / 2.0
                    score_max = 9999
        elif desired_exp_string == "phasing":
            raster_dose = 0.1
            if type_crystal == "lcp" or type_crystal == "sponge":
                att_raster = 100.0
                hebi_att = 100.0
                raster_dose = 0.2
                dose_ds = 8.0
                score_min = 10
                score_max = 100
            elif type_crystal == "soluble":
                raster_dose = 0.1
                score_min = 10
                score_max = 100
                dose_ds = 8.0
                if mode == "helical":
                    raster_dose = raster_dose / 2.0
                    score_max = 9999
        elif desired_exp_string == "lcp_crystals":
            if type_crystal == "lcp" or type_crystal == "sponge":
                att_raster = 100.0
                hebi_att = 100.0
                raster_dose = 0.2
                score_min = 10
                score_max = 100
        elif desired_exp_string == "difficult_sample":
            att_raster = 100.0
            hebi_att = 100.0
            raster_dose = 1.0
            score_min = 7
            score_max = 70
        else:
            print("No desired experiments", desired_exp_string)
            sys.exit()

        return score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, att_raster, hebi_att

    def makeCondList(self):
        if self.isPrep == False:
            self.extractRealList()
        self.conds = []
        self.keys = []
        self.params = []
        p_index = 0
        # KEYS
        keys = "root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,raster_hbeam,att_raster,\
        hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,\
        exp_ds,dist_ds,dose_ds,offset_angle,reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,\
        hel_full_osc,hel_part_osc".split(",")

        pin_param = []
        line_strs = []
        line_strs.append("root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,"
                         "raster_hbeam,att_raster,hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,"
                         "maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,exp_ds,dist_ds,dose_ds,offset_angle,"
                         "reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,hel_full_osc,hel_part_osc,"
                         "raster_roi,ln2_flag,cover_scan_flag,zoomcap_flag,warm_time")
        for cols in self.contents:
            puckid = cols[0].replace("-","")
            pinid = cols[1]
            mode = cols[2]
            wavelength = float(cols[3])
            loop_size = float(cols[4])
            resolution_limit = float(cols[5])
            if resolution_limit > 10.0:
                resolution_limit = 1.5
            max_crystal_size = float(cols[6])
            beamsize = cols[7]
            sample_name = cols[8].replace("(","-").replace(")","-")
            desired_exp = cols[9]
            n_crystals = int(cols[10])
            total_osc = float(cols[11])
            osc_width = float(cols[12])
            type_crystal = cols[13]
            anomalous_flag = cols[14]

            # Calculate detector distance
            distance = self.calcDist(wavelength, resolution_limit)
            hbeam, vbeam = self.check_beamsize(beamsize)
            score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, att_raster, hebi_att = self.getParams(desired_exp, type_crystal, mode)

            cry_min_size = max_crystal_size
            cry_max_size = max_crystal_size
            # Special code
            if mode == "multi" and cry_max_size > 100.0:
                cry_min_size = 25.0
                cry_max_size = 25.0

            self.conds.append((puckid, pinid, mode, wavelength, loop_size, resolution_limit, max_crystal_size, beamsize, 
                sample_name, desired_exp, n_crystals, total_osc, osc_width, type_crystal, anomalous_flag))

            if self.beamline.lower() == "bl32xu":
                dist_raster = 200.0
            elif self.beamline.lower() == "bl45xu":
                dist_raster = 500.0

            # strings
            line_str = "%s,%d,%s,%s,%s,%s," % (root_dir,p_index,mode,puckid,pinid,sample_name)
            # 2020/01/24 wavelength was read as 'character' from the final CSV in ZooNavigator.
            # Be careful to use different version of LIBREOFFICE to convert the CSV file.
            line_str += "%7.5f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%f,%f,%f,0.02,%f,%f,%f,%f,%f,%s,%f,%f,%f," \
                        "%f,%d,%d,%d,%d,%d" % \
                (wavelength,vbeam,hbeam,att_raster,hebi_att,exp_raster,dist_raster,
                loop_size,score_min,score_max,n_crystals,total_osc,osc_width,vbeam,hbeam,distance,dose_ds,0.0,1.0,1.0,
                 desired_exp,cry_min_size,cry_max_size,60,40,raster_roi,0,0,0,0)
            line_strs.append(line_str)
            pin_param = []
            p_index += 1

        prefix = self.csvfile.replace(".csv","")
        ofile=open("%s_zoo.csv" % prefix, "w")
        for line in line_strs:
            ofile.write("%s\n" % line)
            print(line)
        #print line_strs

        self.isGot = True
        return pin_param

    def checkCondList(self):
        root_dir = "ROOT"
        if self.isGot == False:
            self.makeCondList()
        
        #print "root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,raster_hbeam,att_raster,\
        #   hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam, \
        #   exp_ds,dist_ds,dose_ds,offset_angle,reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um, \
        #   hel_full_osc,hel_part_osc,isSkip,isMount,isLoopCenter,isRaster,isDS,scan_height,scan_width,n_mount, \
        #   nds_multi,nds_helical,nds_helpart,t_meas_start,t_mount_end,t_cent_start,t_cent_end,t_raster_start, \
        #   t_raster_end,t_ds_start,t_ds_end,t_dismount_start,t_dismount_end"

        p_index = 0
        """
        for cond in self.conds:
            #print "%(root_dir)s, %(p_index)d, %(mode)s, %(puckid)s, %(pinid)d, %(sample_name)s" % dict(cond)
            #print "%s, %d, %s, %s, %s, "%(
            print cond
            #print "%s,%d,%s,%d" % cond[0],cond[1],cond[2]
        """

if __name__ == "__main__":
    root_dir = os.getcwd()
    useresa = UserESA(sys.argv[1],root_dir,beamline="BL32XU")
    #useresa.printCols()
    #
    useresa.checkCondList()
