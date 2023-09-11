import os, sys, math, numpy, scipy, glob
import DBinfo, ESA 
import BSSmeasurementLog
import Raddose

if __name__ == "__main__":

    dbfile = sys.argv[1]

    esa = ESA.ESA(dbfile)
    conds = esa.getDict()

    for each_db in conds:
        dbinfo = DBinfo.DBinfo(each_db)
        pinstr=dbinfo.getPinStr()
        good_flag = dbinfo.getGoodOrNot()
        constime = dbinfo.getMeasTime()

        root_dir = "%s/%s" % (dbinfo.root_dir, pinstr)

        print(dbinfo.n_mount)

        if good_flag == True:
            mode = each_db['mode']
            nds = dbinfo.getNDS()
            #print dbinfo.ds_vbeam, dbinfo.ds_hbeam, dbinfo.flux, dbinfo.exp_ds
            #print dbinfo.total_osc, dbinfo.osc_width, 

            data_dir = "data%02d" % dbinfo.n_mount

            data_abs = os.path.join(root_dir, data_dir)
            log_files = glob.glob("%s/*.log" % data_abs)
            print(log_files)

            if mode == "multi":
                for log_file in log_files:
                    bmml = BSSmeasurementLog.BSSmeasurementLog(log_file)
                    startphi, endphi, osc_width, exp_time,att_factor = bmml.getExpConds()
                    wavelength = bmml.getWL()
                    hbeam, vbeam = bmml.getBeamsize()
                    nframe = (endphi - startphi) / osc_width
                    if wavelength < 0.0:
                        print("%s: skipping" % log_file)
                    else:
                        #print "DDDDDDDDDD=",wavelength, startphi, endphi, osc_width, exp_time, dbinfo.flux
                        rad = Raddose.Raddose()
                        en = 12.3984 / wavelength
                        #print "EEEEEEEEEEEEEEEEEE",hbeam, vbeam, dbinfo.flux, exp_time, en
                        att_flux = dbinfo.flux * att_factor
                        dose = rad.getDose(hbeam, vbeam, att_flux, exp_time, en)
                        total_dose = dose * nframe
                        print("DOSE %8.2f MGy" % total_dose)
    
                    #getDose(self,h_beam_um,v_beam_um,phosec,exp_time,energy=12.3984,salcon=1500,remote=False):

