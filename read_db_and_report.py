import sqlite3, csv, os, sys
import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    #print esa.getTableName()
    #esa.listDB()
    conds_dict = esa.getDict()

    datedata=sys.argv[1].replace("zoo_","").replace("db","").replace(".","").replace("/","")
    progress_file="check_%s.dat"%datedata
    check_com=open("check_%s.com"%datedata,"w")
    ofile=open(progress_file,"w")
    for cond in conds_dict:
        mode=cond['mode']
        logline=""
        logline+="PUCK:%s"%cond['puckid']
        logline+="-%02d "%cond['pinid']
        logline+="MODE=%8s "%cond['mode']
        logline+="isSkip=%8s "%cond['isSkip']
        logline+="isMount=%8s "%cond['isMount']
        logline+="isDS=%8s "%cond['isDS']
        if mode == "helical":
            nds_helical = cond['nds_helical']
            if nds_helical == "none" or nds_helical == 0:
                logline+="Not-collected      "
                isRaster = cond['isRaster']
                logline+="isRaster = %5d"%isRaster
                if isRaster == 0:
                    logline+="LOG: Raster scan was not conducted."
                else:
                    check_com.write("echo Checking %s-%02d\n"%(cond['puckid'],cond['pinid']))
                    check_com.write("display %s/%s-%02d/scan00/2d/_spotfinder/2d_selected_map.png\n"%(cond['root_dir'],cond['puckid'],cond['pinid']))
                    check_com.write("display %s/%s-%02d/before.ppm \n"%(cond['root_dir'],cond['puckid'],cond['pinid']))
            else:
                logline+="    Collected %5d"%nds_helical
                #logline+="# of datasets:%s"%nds_helical

        if mode == "multi":
            nds_multi = cond['nds_multi']
            logline+="# of datasets:%s"%nds_multi
            
        logline+=" Finished %s"%cond['t_ds_end']
        ofile.write("%s\n"%logline)

