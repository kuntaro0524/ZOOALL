import sqlite3, csv, os, sys
import ESA

if __name__ == "__main__":
    esa = ESA.ESA("test.db")
    esa.makeTable("test.db", csvfile, force_to_make=False):
    esa.getTableName()
    esa.listDB()
    # esa.getColumnsName()
    #esa.makeTable("zoo.db", sys.argv[1],True)
    #esa.addList()
    #esa.addIntegerList_TEST()

    #esa.listDB()
    print "BEFORE"
    ppp = esa.getDict()
    print "LNE=",len(ppp)
    for p in ppp:
        print p
	#print p['isSKip']
        #print p['puckid'],p['pinid'],p['total_osc'],p['mode']
        print "SCAN_WIDTH=",p['scan_width']
        print p['n_mount']
        print p['nds_multi']
        print p['nds_helical']
        print p['nds_helpart']
        print p['t_meas_start']
        print p['t_mount_end']
        print p['t_cent_start']
        print p['t_cent_end']
        print p['t_raster_start']
        print p['t_raster_end']
        print p['t_ds_start']
        print p['t_ds_end']
        print p['t_dismount_start']
    #esa.updateValue("mode","'multi'","where p_index=1")
    #esa.updateValueAt(1,"isMount","1")
    #print "AFTER"
    #ppp = esa.getDict()
    #for p in ppp:
		#print p
        #print p['puckid'],p['pinid'],p['total_osc'],p['mode'],p['hbeam']
