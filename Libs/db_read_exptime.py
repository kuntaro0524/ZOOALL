import os, sys, math
import DBinfo
import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    conds = esa.getDict()

    for p in conds:
        puckid = p['puckid']
        pinid = p['pinid']
        exp_time = p['exp_ds']
        rot = p['osc_width']
        total_osc = p['total_osc']
        raster_vbeam = p['raster_vbeam']
        raster_hbeam = p['raster_hbeam']
        ds_vbeam = p['ds_vbeam']
        ds_hbeam = p['ds_hbeam']
        wt = p['warm_time']
        print(puckid,pinid,exp_time,rot,total_osc, "raster=", raster_vbeam, raster_hbeam," DSbeam=", ds_vbeam, ds_hbeam, "WARM=",wt)
        #print "wavelength=", p['wavelength'], type(p['wavelength'])
