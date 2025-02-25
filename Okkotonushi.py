import os,sys,math,numpy,socket,datetime,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS
import Device
import LoopMeasurement
import StopWatch
import MyException

if __name__ == "__main__":

    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    inocc=IboINOCC.IboINOCC(dev)

    # ROOT DIRECTORY
    root_dir="/isilon/users/target/target/Staff/kuntaro/181109-Okkotonushi/Honban/"

    # Zoo progress report
    zooprog=open("%s/zoo_large.log"%root_dir, "a")

    # preparation
    dev.colli.off()

    # Background image for centering
    # Dismount current pin
    #zoo.dismountCurrentPin()
    #zoo.waitTillReady()

    # Conditions (normally cond.####)
    trayid="CPS1024"
    h_beam=10.0
    v_beam=15.0
    shika_minscore=10
    shika_maxhits=300
    osc_width=0.1
    total_osc=5.0
    exp_henderson=0.25
    exp_time=0.02
    distance=200.0
    sample_name="holder1"
    scan_mode="2D"
    scanv_um=1500
    scanh_um=1500
    hstep_um=10.0
    vstep_um=15.0
    att_idx=0
    raster_exp=0.01
    wl=0.90

    # Change energy
    # Wavelength is changed
    en=12.3984/wl

    curr_en=dev.mono.getE()
    print curr_en,en
    if math.fabs(curr_en-en)>0.001:
        dev.changeEnergy(en,isTune=True)

    for pinid in [15]:
        prefix="%s-%02d"%(trayid,pinid)
        stopwatch=StopWatch.StopWatch()
    
        stopwatch.setTime("start")
        # Mounting the loop
        zoo.mountSample(trayid,pinid)
        zoo.waitTillReady()
    
        stopwatch.setTime("mount_finished")
        starttime=datetime.datetime.now()
    
        ##### Centering part
        inocc.fit_side()
        inocc.fit_tateyoko()
        inocc.fit_pint_direction()
        inocc.fit_tateyoko()
    
        sx,sy,sz=dev.gonio.getXYZmm()
        sphi=dev.gonio.getPhi()
        stopwatch.setTime("centering_finished")
    
        ################# Loop measurement
        lm=LoopMeasurement.LoopMeasurement(s,root_dir,prefix)
        cxyz=sx,sy,sz
        raster_id="2d"
        lm.setWavelength(wl)
    
        lm.prepDataCollection()
        raster_schedule,raster_path=lm.rasterMaster(raster_id,scan_mode,v_beam,h_beam,scanv_um,
                scanh_um,vstep_um,hstep_um,cxyz,sphi,att_idx=att_idx,distance=distance,exptime=raster_exp)
    
        raster_start_time = time.localtime()
        stopwatch.setTime("raster_start")
        zoo.doRaster(raster_schedule)
        zoo.waitTillReady()
        stopwatch.setTime("raster_end")
    
        # Raster scan results
        try:
            glist=[]
            # Crystal size setting
            if h_beam > v_beam:
                    crysize=h_beam/1000.0+0.0001
            else:
                    crysize=v_beam/1000.0+0.0001
    
            glist=lm.shikaSumSkipStrongMulti(cxyz,sphi,raster_path,
                    raster_id,thresh_nspots=shika_minscore,crysize=crysize,max_ncry=shika_maxhits,
                    mode="peak")
    
            n_crystals=len(glist)
    
            # Time calculation
            t_for_mount=stopwatch.getDsecBtw("start","mount_finished")/60.0
            t_for_center=stopwatch.getDsecBtw("mount_finished","centering_finished")/60.0
            t_for_raster=stopwatch.getDsecBtw("raster_start","raster_end")/60.0
            logstr="%20s %20s %5d crystals MCRD[min]:%5.2f %5.2f %5.2f"%(
                    stopwatch.getTime("start"),prefix,n_crystals,t_for_mount,t_for_center,t_for_raster)
            zooprog.write("%s "%logstr)
            zooprog.flush()
    
        except MyException, tttt:
            print "Skipping this loop!!"
            zooprog.write("\n")
            zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print "Disconnecting capture"
            lm.closeCapture()
            sys.exit(1)

        if len(glist)==0:
            print "Skipping this loop!!"
            zooprog.write("\n")
            zooprog.flush()
            # Disconnecting capture in this loop's 'capture' instance
            print "Disconnecting capture"
            lm.closeCapture()
            continue
    
        # Precise centering
        time.sleep(5.0)
        data_prefix="%s-%02d-multi"%(trayid,pinid)
        multi_sch=lm.genMultiSchedule(sphi,glist,osc_width,total_osc,
            exp_henderson,exp_time,distance,sample_name,prefix=data_prefix)
    
        time.sleep(5.0)
    
        dev.gonio.moveXYZmm(sx,sy,sz)
        stopwatch.setTime("data_collection_start")
        zoo.doDataCollection(multi_sch)
        zoo.waitTillReady()
        stopwatch.setTime("data_collection_end")
    
        # Writing Time table for this data collection
        t_for_ds=stopwatch.getDsecBtw("data_collection_start","data_collection_end")/60.0
        logstr="%6.1f "%(t_for_ds)
        zooprog.write("%s\n"%logstr)
        zooprog.flush()
        # Disconnecting capture in this loop's 'capture' instance
        print "Disconnecting capture"
        lm.closeCapture()

    zoo.disconnect()
