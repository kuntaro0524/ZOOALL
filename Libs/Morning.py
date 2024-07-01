q315r_workaround = False # 150511; for temporarily installed Q315r without moving detector cover

import socket
import time
import datetime

# My library
from Mono import *
from FES import *
from ID import *
from TCS import *
from ExSlit1 import *
from File import *
from Att import *
from SPACE import *
from MyException import *
from BM import *
from BS import *
from Stage import *
from Shutter import *
from Capture import *
from Gonio import *
from Colli import *
from Cryo import *
from CenteringNeedle import *
from Zoom import *
from MountPin import *
from Count import *
from FindNeedle import *
from CCDlen import *
from Cover import *
from Light import *
from CoaxYZ import *
from NeedlePicture import *
from AxesInfo import *
from DynamicTable import *
from BeamCenter import *
from ConfigFile import *
from CoaxPint import *
from AttFactor import *
import Flux

class Morning():
    def __init__(self,path):
        #host = '192.168.163.1'
        host = '172.24.242.41'
        port = 10101
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host,port))

        # Devices
        self.id=ID(self.s)
        self.mono=Mono(self.s)
        self.tcs=TCS(self.s)
        self.f=File(path)
        self.att=Att(self.s)
        #self.space=SPACE()
        self.bm=BM(self.s)
        self.stage=Stage(self.s)
        self.shutter=Shutter(self.s)
        self.cap=Capture()
        self.colli=Colli(self.s)
        self.bs=BS(self.s)
        self.gonio=Gonio(self.s)
        self.cryo=Cryo(self.s)
        self.zoom=Zoom(self.s)
        self.slit1=ExSlit1(self.s)
        self.clen=CCDlen(self.s)
        self.covz=Cover(self.s)
        self.light=Light(self.s)
        self.coaxYZ=CoaxYZ(self.s)
        self.coaxpint=CoaxPint(self.s)
        self.conf=ConfigFile()
        
        # current directory
        self.curr_dir=self.f.getAbsolutePath()
        print self.curr_dir

        # Beam position log
        self.bplogname="/isilon/BL32XU/BLsoft/Logs/beam.log"
        # Stage position log
        self.stlog="/isilon/BL32XU/BLsoft/Logs/stage.log"

############################
# Axes information
############################
    def axesInfo(self):
        prefix="%03d"%self.f.getNewIdx3()
        ax=AxesInfo(s)

        ofile=prefix+"_axes.dat"   #hashi 100615
        ax.all(ofile)              #hashi 100615

############################
### OPTICS PART
############################
    def changeE(self,energy):
        print "Energy is changed to %8.5f keV"%energy
        # Energy change
        self.mono.changeE(energy)
        # Gap
        self.id.moveE(energy)

    def dttunePeak(self):
        prefix="%s/%03d"%(self.curr_dir,self.f.getNewIdx3())
        #prefix="%03d"%(self.f.getNewIdx3())
        # Delta theta1 tune
        fwhm,center=self.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.tcs)
        return fwhm,center

    def dttunePeakE(self):
        en=self.mono.getE()
        prefix="%s/%03d"%(self.curr_dir,self.f.getNewIdx3())
        #prefix="%03d"%(self.f.getNewIdx3())

        if en >= 10.0:
        # Delta theta1 tune
            fwhm,center=self.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.tcs)
        else:
            fwhm,center=self.mono.scanDt1PeakConfig(prefix,"DTSCAN_LOWENERGY",self.tcs)
        return fwhm,center

    def setTCSapert(self,vert,hori):
        self.tcs.setApert(vert,hori)

    def measureFlux(self):
        en=self.mono.getE()
        # collimator on
        self.colli.on()
        # Prep scan
        self.prepScan(colli_off=False)
        # Attenuator set 0
        self.setAtt(0)
        # Measurement
        pin_ch=3
        counter=Count(self.s,pin_ch,0)
        i_pin,i_ion=counter.getCount(1.0)
        pin_uA=i_pin/100.0
        iic_nA=i_ion/100.0
        # Photon flux estimation
        ff=Flux.Flux(en)
        phosec=ff.calcFluxFromPIN(pin_uA)
        print "%5.2e"%phosec
        return pin_uA,iic_nA,phosec

############################
### STAGE TUNE
############################
    def getCurrStPos(self):
        sty=self.stage.getYmm()
        stz=self.stage.getZmm()
        return sty,stz

    def kumaTune(self):
        # Dtheta tune with TCS 0.1mm
        # Prep capture
        # Read morning Beam position
        # Tune to the morning Beam position
        print "KUMA"

    # 1. Needle should position at rotation center of gonio
    def stageZtuneNeedle(self):
        # Original position
        z_ori=self.stage.getZmm()
        # Preparation
        self.prepScan()
        prefix="%s/%03d_stz_needle"%(self.curr_dir,self.f.getNewIdx3())

        # Required equipments
        fwhm,z_curr=self.stage.scanZneedleMove(prefix,0.001,40,3,0,0.2)
        print z_ori,z_curr

        # Scan finish
        self.finishExposure()

        return z_ori,z_curr
        
    def stageYtuneCapture(self):
        # Tuning the gain of coax-camera by BM
        self.tuneAttThick()

        # Zoom in
        self.zoom.zoomIn()
        self.movePintZoomMax()

        # Center cross in [pix]
        ceny=320
        cenz=240
        
        # Get current position [um]
        curr_pos=self.stage.getYmm()
        # gain=120   # For ARTRAY
        #gain=4      # controlled by gain DFK72 YK@190311
        gain=16      # controlled by exposure DFK72 YK@190311

        for i in range(0,10):
            print "Current stageY=%12.5f"%self.stage.getYmm()
            prefix="%s/%03d_sty_%02d"%(self.curr_dir,self.f.getNewIdx3(),i)
            # caputure and analyze
            # y,z=self.cap.aveCenter(prefix,gain,5,4000)   # For ARTRAY
            #y,z=self.cap.aveCenter(prefix,gain,5,120)      # controlled by gain DFK72 YK@190311
            y,z=self.cap.aveCenter(prefix,gain,5,1000)      # controlled by exposure DFK72 YK@190311

            # diff x,y
            dy=y-ceny

            # pixel to micron [um/pixel] in high zoom
            p2u_y=9.770E-2

            y_move=dy*p2u_y

            print "Stage Y movement: %8.4f [um]"%y_move

            if math.fabs(y_move) < 0.5:
                print "Tune is successfully done.\n"
                break
            if math.fabs(y_move) > 100:
                    raise MyException("Stage movement is too large Y:%8.4f\n"%(y_move))

            self.stage.moveYum(y_move)
            time.sleep(3)

        # Get current position [um]
        fin_y=self.stage.getYmm()
        fin_z=self.stage.getZmm()

        # Log file
        self.logStage(fin_y,fin_z)

        return curr_pos,fin_y

    def logStage(self,sty,stz):
        # Stage position log
        stf=open(self.stlog,"aw")
        ddd=datetime.datetime.now()
        stf.write("%s %8.5f %8.5f\n"%(ddd,sty,stz))
        stf.close()
        return True

#############################################
# Stage YZ tune to the morning BP
#############################################
    def stageYZtuneCapture(self):

        # Prep tuning
        self.zoom.zoomIn()
        self.movePintZoomMax()

        # Current newest BP in pixel 
        ceny,cenz=self.getBP()

        # Center cross in [pix]
        ceny=int(ceny)
        cenz=int(cenz)

        print "READ value is %10d%10d"%(ceny,cenz)

        # Tuning the gain of coax-camera
        self.tuneAttThick()

        # Initial position of stage YZ
        ini_z=self.stage.getZmm()
        ini_y=self.stage.getYmm()

        #gain=120   #  for ARTRAY by YK@190311
        #gain=4      # change by gain DFK72 YK@190311
        gain=16      # change by exposure DFK72 YK@190311

        # Prefix for 

        for i in range(0,5):
            # caputure and analyze
            prefix="%s/%03d_styz_%02d"%(self.curr_dir,self.f.getNewIdx3(),i)
            # ntime=5 shutter_speed=4000
            #y,z=self.cap.aveCenter(prefix,gain,5,4000)    # for ARTRAY
            y,z=self.cap.aveCenter(prefix,gain,5,500)      # change by exposure DFK72 YK@190311
    
            # diff x,y
            dy=y-ceny
            dz=z-cenz
    
            # pixel to micron [um/pixel] in high zoom
            p2u_z=7.1385E-2
            p2u_y=9.770E-2
    
            z_move=-dz*p2u_z
            y_move=dy*p2u_y
    
            print "Stage moveZ: %8.4f [um]"%z_move
            print "Stage moveY: %8.4f [um]"%y_move

            if math.fabs(z_move) < 0.5 and math.fabs(y_move) < 0.5:
                print "Tune is enough!!\n"
                break
            if math.fabs(z_move) > 50 or math.fabs(y_move) > 50:
                raise MyException("Stage movement is too large z:%8.4f y:%8.4f\n"%(z_move,y_move))
    
            # When the movement is larger than 0.5um -> Tune stage position
            if math.fabs(z_move) > 0.5:
                self.stage.moveZum(z_move)
            if math.fabs(y_move) > 0.5:
                self.stage.moveYum(y_move)
            time.sleep(3)

        # current position
        curr_y=self.stage.getYmm()
        curr_z=self.stage.getZmm()

        # Stage position log
        self.logStage(curr_y,curr_z)
        
        return ini_y,curr_y,ini_z,curr_z

##########################
### Needle centering
##########################
    def needleXcenter(self):
    ##    Attenuator set to 600um
        attfac=AttFactor()
        en=self.mono.getE()
        wavelength=12.3984/en
        bestatt=attfac.getBestAtt(wavelength,0.1)
        self.setAtt(bestatt)
    ##  Device definition
        conf=ConfigFile()
    
    ##    Counter channel
        cnt_ch1=3
        cnt_ch2=1 #PSIC
        counter=Count(self.s,3,1)
    
    ##    Gonio phi list
        phi_list=[(0,180),(90,270)]
    
    ##    Save Gonio position
        sx,sy,sz=self.gonio.getXYZmm()
    
    ##     Wire scan
        rough_radius=80.0 # [um]
        gstep=1.0 #[um]
        nstep=int(rough_radius/gstep)
    
        oname="%03d_scan.dat"%(self.f.getNewIdx3())
        ofile=open(oname,"w")
        oname="%03d_result.dat"%(self.f.getNewIdx3())
        sfile=open(oname,"w")
    
        flag_0_180=False
        flag_90_270=False

        while(1):

            pair_index=0
            for phi_pair in [(0,180),(90,270)]:
                idx=0
                orig=0.0
                reve=0.0
                ox,oy,oz=self.gonio.getXYZmm()
                for phi in phi_pair:
                    if phi==0.0 and flag_0_180==True:
                        continue
                    if phi==180.0 and flag_0_180==True:
                        continue
                    if phi==90.0 and flag_90_270==True:
                        continue
                    if phi==270.0 and flag_90_270==True:
                        continue

                    self.gonio.rotatePhi(phi)
                    gstep=1.0 # [um]
            
                    print "Scan at rotation=",phi,"[deg.]"
                    # PREFIX
                    prefix2="phi_%07.2fdeg_%08.4f"%(phi,sy)
                    prefix="%03d_%s"%(self.f.getNewIdx3(),prefix2)
                    outfile=prefix+"_gonioV.scn"
            
                    # Gonio Z scan range
                    print "Scan STARTED"
                    self.gonio.scanVert2(prefix,-50,50,1,cnt_ch1,cnt_ch2,0.02)
                    print "Scan FINISHED"
        
                    # Analyze
                    ana=AnalyzePeak(outfile)
                    outfig="%s_gonioV.png"%prefix
                    comment="GONIO V SCAN"
                    fwhm,center=ana.analyzeAll("gonioV[mm]","Intensity",outfig,comment,"OBS","FCEN")
                    print "Needle shade FWHM = %8.5f[um] CENTER=%8.5f[um]"%(fwhm,center)
        
                    # Encoder value
                    x,y,z=self.gonio.getXYZmm()
                    ex,ey,ez=self.gonio.getEnc()
        
                    ofile.write("%8.3f %10.3f %8.3f %10.5f%10.5f%10.5f%10.5f%10.5f%10.5f\n"
                        %(fwhm,center,phi,x,y,z,ex,ey,ez))
                    ofile.flush()
            
                    if idx==0:
                        orig=center
                    else:
                        reve=center
                    idx+=1
    
                ## Gonio to saved position
                self.gonio.moveXYZmm(ox,oy,oz)
                chuten=(orig+reve)/2.0
                zure=chuten-reve
                print "CHUTEN,ZURE",chuten,zure
                self.gonio.moveUpDown(-zure)
        
                x,y,z=self.gonio.getXYZmm()
                ex,ey,ez=self.gonio.getEnc()
                no=datetime.datetime.now()
        
                # PSIC
                #itime=10.0
                #psic=int(counter.getCount(itime)[1])
                #psic_pos=psic/100.0/itime*37/75 #[um]
                psic_pos=9.9999
    
                sfile.write("%20s %10.5f%10.5f%10.5f%10.5f%10.5f%10.5f %10.5f%10.2f%10.5f\n"
                    %(no,x,y,z,ex,ey,ez,chuten,psic_pos,zure))
                sfile.flush()
    
                # is finished?
                if math.fabs(zure)<0.5:
                    if phi_pair[0]==0.0:
                        print "0-180 deg OK!"
                        flag_0_180=True
                    if phi_pair[0]==90.0:
                        print "90-270 deg OK!"
                        flag_90_270=True
                    print "DONE1",phi_pair
            print "Loop 1 ends"
            if flag_0_180==False or flag_90_270==False:
                continue
            else:
                print "DONE2",phi_pair
                break
            ofile.close()
            sfile.close()
            break
        return ex,ey,ez

# 2014/12/03 ZZ stage should be set to 1um upper from FWHM center of a needle scan

    def scanZZneedleX(self):
        counter=Count(self.s,3,1)
        # Wire scan
        oname="%03d_zz.dat"%(self.f.getNewIdx3())
        ofile=open(oname,"w")
        curr_pos=self.gonio.getZZ()

        savep=self.gonio.getZZ()
        print savep

        max=-99999.99999
        for rel in arange(-50,50,1):
            target=savep+rel
            self.gonio.moveZZpulse(target)
            cnt=counter.getCount(0.5)[0]
            ofile.write("1245 %10d %10d 1245\n"%(target,cnt))
            print "ZZ=%5d CPS=%5d"%(target,cnt*10)
            ofile.flush()

        self.gonio.moveZZpulse(savep)
        ofile.close()
        # Analyze
        ana=AnalyzePeak(oname)
        outfig="%03d_zz.png"%(self.f.getNewIdx3())
        comment="GONIO ZZ SCAN"
        fwhm,center=ana.analyzeAll("gonioZZ[pls]","Intensity",outfig,comment,"OBS","FCEN")
        print "FWHM = %8.5f CENTER=%8.5f "%(fwhm,center)

        # 2014/12/03 Offset is omitted by K.Hirata
        ## Move
        ## 1um down Y.Kawano's result on 2014/05/28
        ## gonioZZ 0.5 um/pls
        #move_pos=int(center)-2

        move_pos=int(center)

        self.gonio.moveZZpulse(move_pos)
        fin_pos=self.gonio.getZZ()
        print "Final position=",fin_pos

        return curr_pos,fin_pos

    def getNeedleZcenter(self,filename):
        self.cap.capture(filename)
        np=NeedlePicture(filename)
        fwhm,center=np.getCenterFWHM()
        return fwhm,center

    # For debugging
    def analyzeNeedleImage(self):
        sum=0.0
        for i in range(0,5):
            filename="%s/%03d_coaxz_%02d.ppm"% \
                (self.curr_dir,self.f.getNewIdx3(),i)
            print filename
            fwhm,center=self.getNeedleZcenter(filename)
            print "CENTER COAXZ=",center
            sum+=center
        center=sum/5.0
        print "FWHM Averaged.CENTER:",fwhm,center

        diff=center-240
        print "CENTER ZURE=",diff
        pix2um_highz=0.07125   # [um/pixel]
        diff_um=diff*pix2um_highz
        print "Difference from center cross: %5.2f[um]"%diff_um

    def tuneCoaxZ(self,offset):
        # offset : 1um up 140611@BL32XU # UNIT [pulse]
        # 1um = 2pls
        # 2014/12/03 Omitted by K.Hirata
        # See BL32XU log notebook No.15 P.26

        init_pos=self.coaxYZ.getZ()

        # Zoom in
        self.zoom.zoomIn()
        self.movePintZoomMax()
        self.light.on()

        for t in range(0,3):
            savep=self.coaxYZ.getZ()
            sum=0.0
            # Prefix of captured files

            for i in range(0,5):
                filename="%s/%03d_coaxz_%02d.ppm"% \
                    (self.curr_dir,self.f.getNewIdx3(),i)
                print filename
                fwhm,center=self.getNeedleZcenter(filename)
                print "CENTER COAXZ=",center
                sum+=center

            center=sum/5.0
            print "FWHM Averaged.CENTER:",fwhm,center

            diff=center-240
            print "CENTER ZURE=",diff
            pix2um_highz=0.07125   # [um/pixel]
            diff_um=diff*pix2um_highz
            print "Difference from center cross: %5.2f[um]"%diff_um

            # Coax Z PULSE

            # Offset value 2014/06 implement
            # offset value was omitted by K.Hirata 2014/12/03 
            #target=savep-relmove+offset

            if abs(diff_um) >= 0.5:
                relmove=int(diff_um/0.5)
                target=savep-relmove
                print "Moving to %5d"%target
                self.coaxYZ.moveZ(target)

        self.cap.disconnect()
        final_pos=self.coaxYZ.getZ()
        print "Final position=",final_pos
        return init_pos,final_pos

##########################
### Scan related
##########################
    def prepScan(self,colli_off=True):
        if q315r_workaround: print ":: Workaround for Q315r. Don't move detector and its cover."
        # CCD Evacuation
        if not q315r_workaround: self.clen.evac()
        # Cover on
        if not q315r_workaround: self.covz.on()

        # Collimator evacuate
        if colli_off==True:
            self.colli.off()
        # beamstop evacuate
        self.bs.off()

        if q315r_workaround or self.covz.isCover():
            print "Slit1 open"
            self.slit1.openV()
            print "Light down"
            self.light.off()
            print "Shutter open"
            self.shutter.open()
        print "Ready..."

    def finishExposure(self):
        # Shutter close
        time.sleep(1.0)
        self.shutter.close()
        print "Slit1 close"
        self.slit1.closeV()
        # Cover off
        if not q315r_workaround: self.covz.off()
        print "Goto experiments!!"

        # Collimator evacuate for manual unmount
        self.colli.evacManual()
        # Beamstopper evacuate for manual unmount
        self.bs.evacManual()

    def evacNeedle(self,evac_mm):
        x,y,z=self.gonio.getXYZmm()
        ynew=y+evac_mm
        self.gonio.moveXYZmm(x,ynew,z)
        return x,y,z

    def moveXYZmm(self,x,y,z):
        self.gonio.moveXYZmm(x,y,z)

    def prepBC(self):
        self.bm.onPika()

    def finishBC(self):
        self.bm.offXYZ()
        
    def allFin(self):
        self.cap.setCross()
        self.cap.disconnect()
        self.s.close()

######################
## Capture beam position & Analyze only
######################
    def changeAttCapture(self):
        satflag=False
        thrflag=False
        for thick in self.att.getAttList():
            tmpfile="%s/thick_%04d.ppm"%(self.curr_dir,int(thick))
            self.setAtt(thick)
            #self.cap.captureWithSpeed(tmpfile,4000)   #  For ARTRAY by YK@190311
            #self.cap.captureWithSpeed(tmpfile,130)      # change by gain DFK72 YK@190311
            self.cap.captureWithSpeed(tmpfile,500)      # change by exposure DFK72 YK@190311
            bc=BeamCenter(tmpfile)
            satcnt,ave,ithresh=bc.getParams()
        return thick

    def tuneAttThick(self):
        perflag=False
        threflag=False
        for thick in self.att.getAttList():
            tmpfile="%s/thick_%04d.ppm"%(self.curr_dir,int(thick))
            self.setAtt(thick)
            #self.cap.captureWithSpeed(tmpfile,4000)    #  For ARTRAY by YK@190311
            #self.cap.captureWithSpeed(tmpfile,130)      # controleed by gain DFK72 YK@190311
            self.cap.captureWithSpeed(tmpfile,500)      # controlled by exposure DFK72 YK@190311
            bc=BeamCenter(tmpfile)
            satcnt,perc,isum_all=bc.check()
            aveall=float(isum_all)/480.0/640.0

            # I saw a weak scintillation by using perc<3.0
            # I gave a larger value for the threshold.
            # I gave a larger value for the threshold 4 -> 5 on 2016/06/23
            # I gave a larger value for the threshold 5 -> 6 on 2016/06/27
            if perc < 6.0:
                perflag=True

            if aveall <= 60:
                threflag=True

            # K. Hirata 160512 added
            print "RE ",thick,satcnt,perc,isum_all,aveall
            if perflag==True and threflag==True:
                break
        return thick

    # !!!!!! DANGER !!!!!!!
    def doCapAna(self,prefix,avetime=10,nrepeat=1,thicktune=True):
        # Zoom in
        self.zoom.zoomIn()
        self.movePintZoomMax()

        prefix="%s/%03d_%s"%(self.curr_dir,self.f.getNewIdx3(),prefix)
        if thicktune==True:
            self.tuneAttThick()

        ## gain=120   # For ARTRAY
        ##gain=4      # 190311 modified for ImaginSource DFK72 by YK controlled by gain
        gain=16      # 190311 modified for ImaginSource DFK72 by YK  controlled by Speed
                   # caputure and analyze
        # Shutter speed = 4000 for scintillator  140617 K.Hirata
        sumy=0.0
        sumz=0.0
        for i in range(0,nrepeat):
            #y,z=self.cap.aveCenter(prefix,gain,avetime,4000)     # For ARTRAY
            #y,z=self.cap.aveCenter(prefix,gain,avetime,130)     # controlled by gain DFK72 YK@190311
            y,z=self.cap.aveCenter(prefix,gain,avetime,500)      # controlled by exposure DFK72 YK@190311
            print y,z
            sumy+=y
            sumz+=z

        # Average
        y=sumy/float(nrepeat)
        z=sumz/float(nrepeat)
    
        return y,z

    def colliScan(self):
        attfac=AttFactor()
        en=self.mono.getE()
        wavelength=12.3984/en
        bestatt=attfac.getBestAtt(wavelength,0.1)
        self.setAtt(bestatt)
        prefix="%s/%03d"%(self.curr_dir,self.f.getNewIdx3())
        try:
            fwhm_y,fwhm_z,ceny,cenz=self.colli.scanCore(prefix,3)
        except MyException,tttt:
            self.finishExposure()
            print tttt.args[0]
            raise MyException(tttt.args[0])
            
        trans,pin=self.colli.compareOnOff(3)
        logstr="FWHM (Y,Z)=(%10.2f, %10.2f) CENTER (Y,Z)=(%10d,%10d)\n"%(fwhm_y,fwhm_z,ceny,cenz)
        logstr+="Transmission %5.2f percent (Counter:%d)\n"%(trans,pin)
        print "Transmission %5.2f percent (Counter:%d)\n"%(trans,pin)
        return logstr
    
    def setAtt(self,thickness):
        # Configuration of Attenuator
        self.att.init()
        self.att.setAttThick(thickness)

    def setAttTrans(self,transmission):
        # Energy
        en=self.mono.getE()
        wave=12.3984/en

        print self.att.getBestAtt(wave,transmission)

        # Configuration of Attenuator
        #self.att.setAttThick(thickness)

############################
#### Coax pint
############################
    def movePintZoomMax(self):
        pintvalue=int(self.conf.getCondition2("COAX","x130_pint")) #[pulse]
        self.coaxpint.move(pintvalue)

###########################
# Configure file
###########################
    def makeDynamic(self):
        dt=DynamicTable()
        strtime=datetime.datetime.now().strftime("%Y%m%d-%H%M")[2:]
        conffile="/blconfig/bl41xu/bl41xu.config"
        filename="/blconfig/bl41xu/bl41xu.config.%s"%strtime

        # Get current st-y,z
        sty=self.stage.getYmm()
        stz=self.stage.getZmm()

        # REMOVE original bl41xu.conf
        if os.path.exists(conffile):
            os.remove(conffile)
        dt.make(sty,stz,filename)
        # Link
        os.symlink(filename,conffile)

##########################
# Beam position log
##########################
    def getIntensityPosition(self):
        # PIN=3 PSIC=1
        counter=Count(self.s,3,1)
        # PIN value
        #self.setAtt(0)
        itime=10.0 #unit [sec]
        #gain=100.0   # For ARTRAY
        #gain=4.0     # controlled by gain DFK72 YK@190311
        gain=16.0     # controlled by exposure DFK72 YK@190311
        i0,i2=counter.getCount(itime)
        psic=-float(i2)/itime/gain
        psic_pos=psic*37/75.0 #[um]
        return psic_pos

    def saveBP(self,bpy,bpz):
        bplog=open(self.bplogname,"aw")
        date_now=datetime.datetime.now().strftime("%Y%m%d-%H%M")
        bplog.write("%10s %10d %10d\n"%(date_now,bpy,bpz))
        bplog.close()

    def getBP(self):
        bplog=open(self.bplogname,"r")
        lines=bplog.readlines()

        for line in lines:
            print line

        cols=line.split()
        sy,sz=int(cols[1]),int(cols[2])
        return sy,sz

if __name__=="__main__":
    mng=Morning("./")
    mng.analyzeNeedleImage()
    ##cap=Capture()
    ##filename="/isilon/users/target/target/Staff/2015A/150525/1414/test.ppm"
    ##cap.capture(filename,1200)
    ##print mng.getNeedleZcenter(filename)
    #mng.setAttTrans(0.1)
    #mng.measureFlux()
    #mng.allFin()
    #mng.tuneCoaxZ(0)

