import os
import sys
import math
#from  pylab import * 
import socket
import pylab
import scipy
import numpy
#from numpy import *
from pylab import *
from scipy.interpolate import splrep,splev,interp1d,splprep
from MyException import *

class AnalyzePeak:
    def __init__(self,datfile):
        self.fname=datfile
        self.isRead=0

    def gFit(self,px,py):
        gaussian = lambda x: 3*math.exp(-(30-x)**2/20.)

        pylab.plot(px,py)

        # Calculating gravity of integrated peak
        grav=sum(px*py)/sum(py)

        # rough FWHM calculation
        width=pylab.sqrt(abs(sum((px-grav)**2*py)/sum(py)))
        max=py.max()
        print(grav,width,max)

        # Fitting function
        fit=lambda t:max*pylab.exp(-(t-grav)**2/(2*width**2))

        pylab.plot([grav,grav],[0,max],'g--')
        #pylab.plot([grav,grav],[0,max],'g--')
        pylab.plot(px,fit(px))
        pylab.show()

    def newFWHM2(self,px,py):
        ## Min & Max value of smoothed curve
        miny=py.min()
        maxy=py.max()

        minx=px.min()
        maxx=px.max()
        step_int=(maxx-minx)/10000.0

        #tck=splrep(px,py)

        half=(maxy-miny)/2.0

        i_half_up=0
        i_half_down=0
        for i in range(1,len(py)):
            if py[i-1]<half and py[i]>=half:
                i_half_up+=1
                xup=px[i]
            if py[i-1]>=half and py[i]<half:
                i_half_down+=1
                xdown=px[i]

        # Peak shape judgement 
        if i_half_up==0 or i_half_down==0:
            print("No peak value")
            return 0

        if i_half_up>1 or i_half_down>1:
            print("Bad peak shape")
            return 0

        # Peak FWHM analysis
        print(xup,xdown)
        fwhm=math.fabs(xup-xdown)
        center=(xup+xdown)/2.0

        return fwhm,center

    def spline(self,px,py,div=100):
        ## Min & Max value of arrays
        miny=py.min()
        maxy=py.max()
        minx=px.min()
        maxx=px.max()

        step_int=(maxx-minx)/div

        half=(maxy-miny)/2.0

        tck=splrep(px,py)
        newx=arange(minx,maxx,step_int)
        newy=splev(newx,tck,der=0)
        #pylab.plot(newx,newy,'o-')
        #pylab.show()

        return newx,newy

    def newFWHM(self,px,py):
        ## Min & Max value of smoothed curve
        miny=py.min()
        maxy=py.max()

        minx=px.min()
        maxx=px.max()

        step_int=(maxx-minx)/10000.0

        #print miny,maxy,step_int

        half=(maxy-miny)/2.0

        ## base line subcription
        y_based=py-miny

        # Spline sine curve
        #try :
        #for i in range(0,len(px)):
            #print px[i],y_based[i]

        tck=splrep(px,y_based)
        # making narrow step profile from a splined curve
        newx=arange(minx,maxx,step_int)
        newy=splev(newx,tck,der=0)
        
        #pylab.plot(px,py,newx,newy)
        #pylab.show()

        # Error with linear 1d interpolation
        #except ValueError:
            #print "ERROR"
            # making narrow step profile from a splined curve
            #lin=interp1d(px,py)
            #newx=arange(minx,maxx,maxx/50.0)
            #print newx
            #newy=[lin(v) for v in newx]

        #pylab.plot(newx,newy)
        #pylab.show()

        i_half_up=0
        i_half_down=0
        #print len(newx)
        for i in range(1,len(newy)):
            if newy[i-1]<half and newy[i]>=half:
                i_half_up+=1
                xup=newx[i]
                #print "XUP:%8.6f %8.6f\n"%(newx[i],newx[i-1])
            if newy[i-1]>=half and newy[i]<half:
                i_half_down+=1
                xdown=newx[i]
                #print "XDOWN:%8.6f %8.6f\n"%(newx[i],newx[i-1])

        # Peak shape judgement 
        if i_half_up==0 or i_half_down==0:
            print("No peak value")
            return 0,0

        if i_half_up>1 or i_half_down>1:
            print("Bad peak shape")
            return 0,0

        # Peak FWHM analysis
        fwhm=math.fabs(xup-xdown)
        center=(xup+xdown)/2.0

        #print xup,xdown

        return fwhm,center

    def getPylabArray(self,dat):
        px=pylab.array(dat)
        return px

    def inter1dline(self,xdat,ydat,xlist):
        # xdat, ydat -> Numpy array
        f1=interp1d(xdat,ydat,kind='linear',bounds_error=False,fill_value=0)

        # making newx list
        newx=numpy.arange(min(xdat),max(xdat),(max(xdat)-min(xdat))/20000)
        newy=f1(newx)

        # search value
        ylist=[]
        for x in xlist:
            idx=0
            for nx in newx:
                if x==newx[idx]:
                    print("FIND")
                    ave=newy[idx]
                    ylist.append(ave)

                elif x > newx[idx] and x<newx[idx+1]:
                    #print "%8.5f %8.5f %8.5f"%(x,newx[idx],newx[idx+1])
                    ave=(newy[idx]+newy[idx+1])/2.0
                    ylist.append(ave)
                idx+=1
    
        # Search value
        #print "#######################"
        #print len(ylist)
        #print "#######################"

        return ylist

    def inter1d(self,xdat,ydat):
        minx=xdat.min()
        maxx=xdat.max()
        step=(maxx-minx)/50.0
        print(minx,maxx,step)

        len=interp1d(xdat,ydat)
        
        newx=arange(minx,maxx,step)
        print(newx)
        print(len(newx))
        newy=[lin(v) for v in newx]
        
        for i in range(0,len(newx)):
            print(newx[i],newy[i])

        pylab.plot(xdat,ydat,newx,newy)
        pylab.show()

        return newx,newy
    
    def smooth(self,x,window_len=11,window='hanning'):
        """smooth the data using a window with requested size.
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal
            
        example:
    
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string   
        """

        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")
        
        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")
    
    
        if window_len<3:
            return x
    
    
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    
    
        s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
        #print(len(s))
        if window == 'flat': #moving average
            w=ones(window_len,'d')
        else:
            w=eval('numpy.'+window+'(window_len)')
    
        y=numpy.convolve(w/w.sum(),s,mode='same')
        return y[window_len-1:-window_len+1]

    def interpolate(self,xdat,ydat):
        ###s=10
        ###k=3
        ###nest=-1
        
        ###tckp,u=splprep([xdat,ydat],s=s,k=k,nest=-1)
        ###xnew,ynew=splev(linspace(0,1,2000),tckp)
        ###pylab.plot(xnew,ynew)
        ###pylab.plot(xdat,ydat)
        ###pylab.savefig("test.png")

        ### New
        px=pylab.array(xdat)
        py=pylab.array(ydat)

        newy=self.smooth(py)

        pylab.plot(xdat,ydat)
        pylab.plot(xdat,newy)
        pylab.savefig("test.png")

        print(px,newy)

    def __readColumn(self):
        self.cols=[]
        # count a number of columns
        #print self.fname	
        f=open(self.fname,"r")
        lines=f.readlines()
        f.close()

        for line in lines:
            if line.strip().find("#")==0:
                continue

            new=[]
            new=line.replace(","," ").strip().split()

            self.cols.append(new)

        self.ncols=len(self.cols)
        #print self.ncols

    def clear(self):
        self.xdat=[]
        self.ydat=[]
        self.dx=[]
        self.dy=[]

    def convertArray(self,xdat,ydat):
        xd=pylab.array(xdat)
        yd=pylab.array(ydat)
        
        return xd,yd

    def divide(self,y1,y2):
        if len(y1) != len(y2):
            return False

        else :
            div=[]
            for i in range(0,len(y1)):
                if y2[i]==0.0:
                    return False
                else:
                    div.append(y1[i]/y2[i])

        return div

    def calcGrav(self,xdat,ydat):
        # Gravity calculation
        xd,yd=self.convertArray(xdat,ydat)

        # Calculating gravity of integrated peak
        grav=sum(xd*yd)/sum(yd)

        return grav

    def plotGauss(self,xdat,ydat,xlabel,ylabel,outfig):
        # Gravity calculation
        xd,yd=self.convertArray(xdat,ydat)
        pylab.plot(xd,yd,'o-')
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)

        # Calculating gravity of integrated peak
        grav=sum(xd*yd)/sum(yd)

        width=pylab.sqrt(abs(sum((xd-grav)**2*yd)/sum(yd)))
        max=yd.max()

        for i in range(0,len(xd)):
            if yd[i]==max:
                break
        max_x=xd[i]

        text="Observed FWHM(%8.3f), Peak gravity(%8.3f)\n"%(width,grav)
        peak="Peak (%8.3f)"%max_x
        text=text+peak
        pylab.title(text)

        fit=lambda t:max*pylab.exp(-(t-grav)**2/(2*width**2))
        pylab.plot(xd,fit(xd))
        pylab.legend((r'Observed',r"Gaussian fit"%grav),shadow=True,loc=(0.8,0.8))
        pylab.savefig(outfig)

        # clear axis and plot
        pylab.clf()
        pylab.cla()

    def gaussianFit(self,col_x,col_y):
        if self.isRead==0:
            self.__readColumn()
        self.storeData(col_x,col_y)

        self.convertToPylabArray()

        # Calculating gravity of integrated peak
        self.grav=sum(self.xd*self.yd)/sum(self.yd)

        self.width=pylab.sqrt(abs(sum((self.xd-self.grav)**2*self.yd)/sum(self.yd)))
        self.max=self.yd.max()

        print("gravity=%8.5f" % self.grav)

        return self.width,self.grav

    def averageData(self,nave):
        self.xave=[]
        self.yave=[]

        p=int(self.ncols/nave)
        residual=self.ncols-p*nave

        resi_start=self.ncols
    
        #print p,residual

        tmpsumx=0
        tmpsumy=0
        tmpnd=0

        #print self.ncols

        starti=0
        endi=0
        for i in range(0,p):
            starti=i*nave
            endi=starti+nave-1

            tmpsumx=0
            tmpsumy=0
            for j in range(starti,endi+1):
                #print j
                tmpsumx+=self.xdat[j]
                tmpsumy+=self.ydat[j]

            print(tmpsumx,tmpsumy)
            self.xave.append(tmpsumx/nave)
            self.yave.append(tmpsumy/nave)

        tmpsumx=0
        tmpsumy=0

        for i in range(endi+1,endi+1+residual):
            tmpsumx+=self.xdat[i]
            tmpsumy+=self.ydat[i]

        self.xave.append(tmpsumx/residual)
        self.yave.append(tmpsumy/residual)

        return self.xave,self.yave

    def storeData(self,col_x,col_y):
        self.__readColumn()
        self.xdat=[]
        self.ydat=[]

        for idx in range(0,self.ncols):
            self.xdat.append(float(self.cols[idx][col_x]))
            self.ydat.append(float(self.cols[idx][col_y]))
            #print self.cols[idx][col_x], self.cols[idx][col_y]

        return self.xdat,self.ydat

    def calcDrv(self):
        dx,dy=self.derivative(self.xdat,self.ydat)
        return self.dx,self.dy

    def scaleY(self,ydat,scale):
        yscale=[]

        print("scale factor %8.5f"%scale)

        for idx in range(0,len(ydat)):
            yscale.append(ydat[idx]*scale)

        return yscale
    
    def writeData(self,ofile,xdat,ydat):
        of=open(ofile,"w")
        ndata=len(xdat)

        for i in range(0,ndata):
            of.write("%12.5f %12.5f\n"%(xdat[i],ydat[i]))

        of.close()

    def writeDrv(self,ofile):
        of=open(ofile,"w")
        ndata=len(self.dx)
        #print ndata

        for i in range(0,ndata):
            #print i
            of.write("12345 %12.5f %12.5e 12345\n"%(self.dx[i],self.dy[i]))

        of.close()

    def divData(self,ydat1,ydat2):
        norm=[]
        for i in range(0,len(ydat1)):
            norm.append(ydat1[i]/ydat2[i])
        
        return norm

    def normalizePeak(self,col_x,col_y,ofile):
        of=open(ofile,"w")

        if self.isRead==0:
            self.__readColumn()
        self.storeData(col_x,col_y)
        self.findHalf(self.xdat,self.ydat)

        ndata=len(self.xdat)

        for i in range(0,ndata):
            self.ydat[i]=float(self.ydat[i])/float(self.maxvalue)

        self.writePeak(ofile)

    def getDerivative(self):
        return self.dx,self.dy

    def getData(self):
        return self.xdat,self.ydat

    def drvCenter(self,col_x,col_y):
        if self.isRead==0:
            self.__readColumn()
            self.storeData(col_x,col_y)
        self.calcDrv()
        mini,maxi=self.findMinMax(self.dy)
        drvcenter=(self.dx[mini]+self.dx[maxi])/2.0
        #self.writeDrv("ping.dat")
        return drvcenter

    def calcFWHM_PPM(self,px,py):
        peak_flag=0
        minx=px.min()
        maxx=px.max()

        miny=py.min()
        maxy=py.max()

        halfvalue=(maxy+miny)/2.0

        # Initialization
        smallx=-999.999
        largex=-999.999

        # before peak
        for idx in range(0,len(px)-1):
            if py[idx] <= halfvalue and py[idx+1] >= halfvalue:
                smallx=px[idx]
                break

        #print "Brightness half: %5d YMIN=%5d"%(halfvalue,py.argmin())
        #print "SMALL-LARGE:",smallx,largex
        for idx in range(py.argmax(),len(px)-1):
            if py[idx] >= halfvalue and py[idx+1] <= halfvalue:
                largex=px[idx]
                break

        fwhm=math.fabs(smallx-largex)
        fcen=(smallx+largex)/2.0
        return  fwhm,fcen

    def calcFWHM(self,px,py):
        peak_flag=0
        minx=px.min()
        maxx=px.max()

        miny=py.min()
        maxy=py.max()

        halfvalue=(maxy-miny)/2.0
        print("HALF:",maxy,miny,halfvalue)

        # Initialization
        smallx=-999.999
        largex=-999.999

        # before peak
        for idx in range(0,len(px)-1):
            if py[idx] <= halfvalue and py[idx+1] >= halfvalue:
                grad1=(py[idx+1]-py[idx])/(px[idx+1]-px[idx])
                sepp1=py[idx]-grad1*px[idx]
                
                #print "Y=%5.3f x + %5.3f" % (grad1,sepp1)
                smallx=(halfvalue-sepp1)/grad1
                break

        for idx in range(0,len(px)-1):
            if py[idx] >= halfvalue and py[idx+1] <= halfvalue:
                grad2=(py[idx+1]-py[idx])/(px[idx+1]-px[idx])
                sepp2=py[idx]-grad2*px[idx]
                
                #print "Y=%5.3f x + %5.3f" % (grad2,sepp2)
                largex=(halfvalue-sepp2)/grad2
                break

        if smallx==-999.999 or largex==-999.999:
            print("FWHM cannot be calculated!")
            return -999.999

        # FWHM center
        fcen=(smallx+largex)/2.0
        fwhm=math.fabs(smallx-largex)

        print(smallx,largex,fwhm,fcen)

        return  fwhm,fcen

    def calcDrv2(self,col_x,col_y):

        self.ddx=[]
        self.ddy=[]

        if len(self.dx)==0:
            self.dx,self.dy=self.calcDrv(col_x,col_y)

        self.ddx,self.ddy=self.derivative(self.dx,self.dy)

        for idx in range(0,len(self.dx)):
            print("%12.5f %12.5f" %(self.dx[idx], self.dy[idx]))


        def derivative(self,xdat,ydat):
                self.dx=[]
                self.dy=[]

        xsize=len(xdat)
        ysize=len(ydat)

        if xsize==0 or ysize==0:
            print("Size of arrays is 0")
            return 0

        for cols in range(0,xsize-1):
            self.dx.append((xdat[cols]+xdat[cols+1])/2.0)
            self.dy.append(ydat[cols]-ydat[cols+1])

        return self.dx,self.dy

    def findPeak(self,col,type):
        if self.isRead==0:
            self.__readColumn()

        #print self.ncols
        
        maxvalue=-999999.99999

        for idx in range(0,self.ncols):
            tmp=float(self.cols[idx][col])
            if tmp > maxvalue:
                maxvalue=tmp

        if type=="int":
            return int(maxvalue)
        elif type=="float":
            return float(maxvalue)
        elif type=="char":
            return str(maxvalue)

    def findMinMax(self,data_array):
        ndata=len(data_array)
        maxvalue=-999999999.99999
        minvalue=99999999.99999

        min_index=0
        max_index=0

        if ndata==0:
            print("Array is not good")
            return -1
        for i in range(0,ndata):
            if(maxvalue < data_array[i]):
                maxvalue=data_array[i]
                max_index=i
            if(minvalue > data_array[i]):
                minvalue=data_array[i]
                min_index=i
            else :
                continue

        return min_index,max_index

    def getXinY(self,x,y,yvalue):
        for i in range(0,len(y)):
            if y[i]==yvalue:
                return x[i]

    def getFWHMsplined(self,xdat,ydat):
        # xdat, ydata should be splined pylab.array
        miny=ydat.min()
        maxy=ydat.max()

        half=(maxy-miny)/2.0

        i_half_up=0
        i_half_down=0

        for i in range(1,len(ydat)):
            if ydat[i-1]<half and ydat[i]>=half:
                print(ydat[i-1],ydat[i])
                i_half_up+=1
                xup=xdat[i]
        if ydat[i-1]>=half and ydat[i]<half:
            print(ydat[i-1],ydat[i])
            i_half_down+=1
            xdown=xdat[i]

        # Peak shape judgement
        if i_half_up==0 or i_half_down==0:
                print("No peak value")
                return 0

        if i_half_up>1 or i_half_down>1:
                print("Bad peak shape")
                #return 0

        # Peak FWHM analysis
        print(xup,xdown)
        fwhm=math.fabs(xup-xdown)
        center=(xup+xdown)/2.0

        return fwhm,center

    def anaKnife(self,xlabel,ylabel,comment=""):
        # Reading .scn file (column 1,2; skip 0th column)
        xdat,ydat,junk=self.prepData3(1,2,1)
        junk=junk2=[]

        # derivative of observed curve
        dx,dy=self.derivative(xdat,ydat)

        # Swap for splined curve fitting
        if xdat[0]>xdat[1]:
            xdat.reverse()
            ydat.reverse()

        px,py,junk2=self.prepPylabArray(xdat,ydat,junk)
        pox,poy,junk2=self.prepPylabArray(dx,dy,junk)
        junk=[]

        minx=px.min()
        maxx=px.max()

        ## preparation of spline curve fitting
        step_int=(maxx-minx)/10000.0

        ## Spline fitting
        tck=splrep(px,py)
        newx=arange(minx,maxx,step_int)
        newy=splev(newx,tck,der=0)
        newdy=splev(newx,tck,der=1)

        ## Flip the peak profile 
        tmp_ymax=newdy.max()
        tmp_ymin=newdy.min()

        if abs(tmp_ymax) < abs(tmp_ymin):
            for i in range(0,len(newdy)):
                newdy[i]=-newdy[i]
            for j in range(0,len(poy)):
                poy[j]=-poy[j]

        ## Observed derivative
        obsd_file=self.fname.replace(".scn","_o_drv.scn")
        of=open(obsd_file,"w")
        for i in range(0,len(dx)):
            of.write("12345 %10d %10d 12345\n"%(pox[i],poy[i]))
        of.close()

        ## Splined derivative
        smooth_file=self.fname.replace(".scn","_s_drv.scn")
        of=open(smooth_file,"w")
        for i in range(0,len(newx)):
            of.write("12345 %8.5f %8.5f 12345\n"%(newx[i],newdy[i]))
        of.close()

        # Whole peak gravity
        grav_o=self.calcGrav(dx,dy)
        grav_s=self.calcGrav(newx,newdy)
        grav_str="[Grav O:%8.4f S:%8.4f]" % (grav_o,grav_s)

        # FWHM and its center
        #fwhm_ob,center_ob=self.calcFWHM(pox,poy)
        fwhm_sm,center_sm=self.getFWHMsplined(newx,newdy)
        #fwhm_str="[FWHM O:%8.4f/S:%8.3f][Center O:%8.4f/S:%8.4f]\n"%(fwhm_ob,fwhm_sm,center_ob,center_sm)
        fwhm_str="[FWHM S:%8.3f][Center S:%8.4f]\n"%(fwhm_sm,center_sm)

        # Peak position 
        maxyo=poy.max()
        maxxo=self.getXinY(pox,poy,maxyo)
        print(maxxo)

        maxy=newdy.max()
        maxx=self.getXinY(newx,newdy,maxy)
        print(maxx)
        peakstr="[Peak (O:%8.3f/S:%8.3f)]"%(float(maxxo),float(maxx))

        ## Plotting
        fig=pylab.figure()
        fig1=fig.add_subplot(111)
        fig1.set_xlabel(xlabel)
        fig1.set_ylabel(ylabel)

        text=fwhm_str+peakstr+grav_str
        fig1.set_title(text,fontsize=10)
        fig1.annotate(comment,xy=(0.27,0.8))
        fig1.plot(dx,dy,'-')

        fig2=fig1.twinx()
        fig2.plot(newx,newdy,'-')

        # picture
        picf=self.fname.replace(".scn","_drv.png")
        fig1.plot([center_sm,center_sm],[0,maxyo],'--')
        fig1.legend((r'Observed',r'Splined'),shadow=True,loc=(0.8,0.8))

        pylab.savefig(picf)

        return fwhm_sm,center_sm

    def anaK(self,xlabel,ylabel,comment=""):
        xdat,ydat,junk=self.prepData3(1,2,1)
        junk=junk2=[]

        # derivative of observed curve
        dx,dy=self.derivative(xdat,ydat)

        # Swap for splined curve fitting
        if xdat[0]>xdat[1]:
            xdat.reverse()
            ydat.reverse()

        px,py,junk2=self.prepPylabArray(xdat,ydat,junk)
        pox,poy,junk2=self.prepPylabArray(dx,dy,junk)
        junk=[]

        minx=px.min()
        maxx=px.max()

        ## preparation of spline curve fitting
        step_int=(maxx-minx)/10000.0

        ## Spline fitting
        tck=splrep(px,py)
        newx=arange(minx,maxx,step_int)
        newy=splev(newx,tck,der=0)
        newdy=splev(newx,tck,der=1)

        ## Flip the peak profile 
        tmp_ymax=newdy.max()
        tmp_ymin=newdy.min()

        if abs(tmp_ymax) < abs(tmp_ymin):
            for i in range(0,len(newdy)):
                newdy[i]=-newdy[i]
            for j in range(0,len(poy)):
                poy[j]=-poy[j]

        ## Observed derivative
        obsd_file=self.fname.replace(".scn","_o_drv.scn")
        of=open(obsd_file,"w")
        for i in range(0,len(dx)):
            of.write("12345 %12.5f %10d 12345\n"%(pox[i],poy[i]))
        of.close()

        ## Splined derivative
        smooth_file=self.fname.replace(".scn","_s_drv.scn")
        of=open(smooth_file,"w")
        for i in range(0,len(newx)):
            of.write("12345 %8.5f %8.5f 12345\n"%(newx[i],newdy[i]))
        of.close()

        # Whole peak gravity
        grav_o=self.calcGrav(dx,dy)
        grav_s=self.calcGrav(newx,newdy)
        grav_str="[Grav O:%8.4f S:%8.4f]" % (grav_o,grav_s)

        # FWHM and its center
        #fwhm_ob,center_ob=self.calcFWHM(pox,poy)
        fwhm_sm,center_sm=self.getFWHMsplined(newx,newdy)
        #fwhm_str="[FWHM O:%8.4f/S:%8.3f][Center O:%8.4f/S:%8.4f]\n"%(fwhm_ob,fwhm_sm,center_ob,center_sm)
        fwhm_str="[FWHM S:%8.3f][Center S:%8.4f]\n"%(fwhm_sm,center_sm)

        # Peak position 
        maxyo=poy.max()
        maxxo=self.getXinY(pox,poy,maxyo)
        print(maxxo)

        maxy=newdy.max()
        maxx=self.getXinY(newx,newdy,maxy)
        print(maxx)
        peakstr="[Peak (O:%8.3f/S:%8.3f)]"%(float(maxxo),float(maxx))

        ## Plotting
        fig=pylab.figure()
        fig1=fig.add_subplot(111)
        fig1.set_xlabel(xlabel)
        fig1.set_ylabel(ylabel)

        text=fwhm_str+peakstr+grav_str
        fig1.set_title(text,fontsize=10)
        fig1.annotate(comment,xy=(0.27,0.8))
        fig1.plot(dx,dy,'-')

        fig2=fig1.twinx()
        fig2.plot(newx,newdy,'-')

        # picture
        picf=self.fname.replace(".scn","_drv.png")
        fig1.plot([center_sm,center_sm],[0,maxyo],'--')
        fig1.legend((r'Observed',r'Splined'),shadow=True,loc=(0.8,0.8))

        pylab.savefig(picf)
        return fwhm_sm,center_sm

    def fitting(self):
        xdat,ydat,junk=self.prepData3(1,2,1)
        #px,py,junk2=self.prepPylabArray(xdat,ydat,junk)
        junk=junk2=[]

        # Swap
        if xdat[0]>xdat[1]:
            xdat.reverse()
            ydat.reverse()

        px,py,junk2=self.prepPylabArray(xdat,ydat,junk)

        py_smooth=self.smooth(py)

        tck=splrep(px,py_smooth)

        minx=px.min()
        maxx=px.max()
        #miny=py.min()
        #maxy=py.max()

        step_int=(maxx-minx)/10000.0

        newx=arange(minx,maxx,step_int)
        newy=splev(newx,tck,der=0)

        newdy=splev(newx,tck,der=1)

        for i in range(0,len(newx)):
            print(newx[i],newy[i],newdy[i])
        
        pylab.plot(newx,newy,xdat,ydat,newx,newdy)

        pylab.show()

    def prepData2(self,col1,col2):
        # X-Y acquisition
        self.storeData(col1,col2)
        xdat,ydat=self.getData()

        # Pylab array
        px=self.getPylabArray(xdat)
        py=self.getPylabArray(ydat)

        return px,py

    def prepData3(self,col1,col2,col3):
        # X-Y1 acquisition
        self.storeData(col1,col2)
        xdat,y1dat=self.getData()

        # X-Y2 acquisition
        self.clear()
        self.storeData(col1,col3)
        junk,y2dat=self.getData()

        return xdat,y1dat,y2dat

    def prepPylabArray(self,a1,a2,a3):
        # convert to pylabarray
        pa1=self.getPylabArray(a1)
        pa2=self.getPylabArray(a2)
        pa3=self.getPylabArray(a3)

        return pa1,pa2,pa3

    def analyzeKnife(self,xlabel,ylabel,drvfile,outfig,comment="",opt="FWHM"):
        # graph clear
        pylab.clf()
        pylab.cla()
        # prep data
        xdat,ydat,junk=self.prepData3(1,2,1)

        dx,dy=self.derivative(xdat,ydat)
        px,py,junk2=self.prepPylabArray(dx,dy,junk)

        #px,py,junk2=self.prepPylabArray(xdat,ydat,junk)
        #dx=(px[0]+px[1])/2.0
        #dy=(py[0]-py[1])

        junk=junk2=[]

        # smoothing y data
        sy=self.smooth(py)

        # Whole peak gravity
        grav=self.calcGrav(px,sy)
        maxy=sy.max()
        maxx=self.getXinY(px,sy,maxy)

        #print maxy,maxx

        # FWHM calculation
        #print len(px),len(sy)
        #fwhm_ob,center_ob=self.newFWHM2(px,py)
        #fwhm_sm,center_sm=self.newFWHM2(px,sy)
        #fwhm_ob,center_ob=self.newFWHM(px,py)
        #fwhm_sm,center_sm=self.newFWHM(px,sy)
        fwhm_ob,center_ob=self.calcFWHM(px,py)
        fwhm_sm,center_sm=self.calcFWHM(px,sy)

        # Output derivatives
        of=open(drvfile,"w")
        for i in range(0,len(dx)):
            of.write("12345 %12.5f %12.5f 12345\n"%(dx[i],dy[i]))
        of.close()

        # plot all data
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)

        text="Observed/Smoothed FWHM(%8.4f/%8.4f), FWHM center(%8.4f/%8.4f),\nPeak gravity(%8.4f),"%(fwhm_ob,fwhm_sm,center_ob,center_sm,grav)
        peak="Peak (%8.3f)"%maxx
        text=text+peak
        pylab.title(text,fontsize=10)
        pylab.suptitle(comment,fontsize=7,x=0.27,y=0.8)

        # Legend setting
        pylab.plot(px,py,'o-',px,sy,'x-')
        pylab.legend((r'Observed',r'Splined Obs'),shadow=True,loc=(0.8,0.8))

        if opt=="PEAK":
            pylab.plot([maxx,maxx],[0,py.max()],'--')
            pylab.savefig(outfig)
        else:
            pylab.plot([center_sm,center_sm],[0,maxy],'--')
            pylab.savefig(outfig)

        # clear axis and plot
        pylab.clf()
        pylab.cla()

        # Option
        if opt=="PEAK":
            return fwhm_sm,maxx
        elif opt=="OBS":
            return fwhm_ob,center_ob
        else:
            return fwhm_sm,center_sm

    def analyzeAll2(self,xlabel,ylabel,outfig,col1,col2,comment="",opt1="OBS",opt2="FCEN"):
        # clear axis and plot
        pylab.clf()
        pylab.cla()

        # prep data
        xdat,y1dat,y2dat=self.prepData3(col1,col2,3)
        print(xdat,y1dat)
        px,py1,py2=self.prepPylabArray(xdat,y1dat,y2dat)

        # smoothing y1 data
        sy1=self.smooth(py1)

        # average
        ave=sy1.mean()

        # peak gravity 
        grav=self.calcGrav(px,sy1)

        # Observed or Smoothed
        if opt1=="OBS":
            maxy1=py1.max()
            maxx1=self.getXinY(px,py1,maxy1)
            fwhm,center=self.newFWHM(px,py1)
            if fwhm==0:
                raise MyException("analyzeAll failed: FWHM is none\n")

        else:
            maxy1=sy1.max()
            maxx1=self.getXinY(px,sy1,maxy1)
            fwhm,center=self.newFWHM(px,sy1)
            if fwhm==0:
                raise MyException("analyzeAll failed: FWHM is none%s\n")

        # plot all data
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.suptitle(comment,fontsize=7,x=0.27,y=0.8)

        # plot all data
        if opt1=="SMOOTH":
            pylab.plot(px,py1,'o-',px,py2,'^-',px,sy1,'r-',linewidth=1.5)
            pylab.legend((r'Ch1',r'Ch2',r"Splined Ch1"%grav),shadow=True,loc=(0.8,0.8))
            pylab.plot([center,center],[0,maxy1],'--')
            # Title setting
            text="Observed FWHM(%8.4f), FWHM center(%8.4f)\nPeak gravity(%8.4f),"%(fwhm,center,grav)
            peak="Peak (%8.3f) "%maxx1
            text=text+peak
            pylab.title(text,fontsize=10)

        else :
            pylab.plot(px,py1,'o-',px,py2,'r-',linewidth=1.5)
            pylab.legend((r'Ch1',r'Ch2'),shadow=True,loc=(0.8,0.8))
            pylab.plot([center,center],[0,maxy1],'--')
            # Title setting
            text="Observed FWHM(%8.4f), FWHM center(%8.4f), Peak gravity(%8.4f)\n"%(fwhm,center,grav)
            peak="Peak (%8.3f) "%maxx1
            text=text+peak
            pylab.title(text,fontsize=10)

        pylab.savefig(outfig)


        # condition
        if opt2=="PEAK":
            return fwhm,maxx1
        else:
            return fwhm,center

        
    def analyzeAll(self,xlabel,ylabel,outfig,comment="",opt1="OBS",opt2="FCEN"):
        # clear axis and plot
        pylab.clf()
        pylab.cla()

        # prep data
        xdat,y1dat,y2dat=self.prepData3(1,2,3)
        px,py1,py2=self.prepPylabArray(xdat,y1dat,y2dat)

        # smoothing y1 data
        sy1=self.smooth(py1)

        # average
        ave=sy1.mean()

        # peak gravity 
        grav=self.calcGrav(px,sy1)

        # Observed or Smoothed
        if opt1=="OBS":
            maxy1=py1.max()
            maxx1=self.getXinY(px,py1,maxy1)
            fwhm,center=self.newFWHM(px,py1)
            if fwhm==0:
                raise MyException("analyzeAll failed: FWHM is none\n")

        else:
            maxy1=sy1.max()
            maxx1=self.getXinY(px,sy1,maxy1)
            fwhm,center=self.newFWHM(px,sy1)
            if fwhm==0:
                raise MyException("analyzeAll failed: FWHM is none%s\n")

        # plot all data
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        pylab.suptitle(comment,fontsize=7,x=0.27,y=0.8)

        # plot all data
        if opt1=="SMOOTH":
            pylab.plot(px,py1,'o-',px,py2,'^-',px,sy1,'r-',linewidth=1.5)
            pylab.legend((r'Ch1',r'Ch2',r"Splined Ch1"%grav),shadow=True,loc=(0.8,0.8))
            pylab.plot([center,center],[0,maxy1],'--')
            # Title setting
            text="Observed FWHM(%8.4f), FWHM center(%8.4f)\nPeak gravity(%8.4f),"%(fwhm,center,grav)
            peak="Peak (%8.3f) "%maxx1
            text=text+peak
            pylab.title(text,fontsize=10)

        else :
            pylab.plot(px,py1,'o-',px,py2,'r-',linewidth=1.5)
            pylab.legend((r'Ch1',r'Ch2'),shadow=True,loc=(0.8,0.8))
            pylab.plot([center,center],[0,maxy1],'--')
            # Title setting
            text="Observed FWHM(%8.4f), FWHM center(%8.4f), Peak gravity(%8.4f)\n"%(fwhm,center,grav)
            peak="Peak (%8.3f) "%maxx1
            text=text+peak
            pylab.title(text,fontsize=10)

        pylab.savefig(outfig)


        # condition
        if opt2=="PEAK":
            return fwhm,maxx1
        else:
            return fwhm,center

if __name__=="__main__":
            #host = '172.24.242.41'
            #port = 10101
            ##s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.connect((host,port))

        ana=AnalyzePeak(sys.argv[1])

                #fwhm,center=ana.anaK("slit1 upper[pulse]","intensity[cnt]","TEST")
        px,py=ana.prepData2(0,1)
        #dx,dy=ana.spline(px,py,10000)	
        #dx,dy=ana.analyzeKnife("X","Y")
        #print ana.analyzeKnife("X","Y","test_ana.drv","test.png","TEST","OBS")
        #ana.calcDrv2(1,2)
        #xdat,ydat,junk=ana.prepData3(1,2,1)
        dx,dy=ana.derivative(xdat,ydat)

        for idx in range(0,len(dxx)):
            print(1234,dxx[idx],dyy[idx],1234)
