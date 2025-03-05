import sys,os,math,numpy
import Raddose

class KUMA:
    def __init__(self):
        # Around 10 MGy
        self.limit_dens=1E10 # phs/um^2 this is for 1A wavelength

    def setPhotonDensityLimit(self,value):
        self.limit_dens=value

    def estimateAttFactor(self,exp_per_frame,tot_phi,osc,crylen,phosec,vbeam_um):
        attfactor=self.limit_dens*(crylen*vbeam_um*osc)/(phosec*exp_per_frame*tot_phi)
        return attfactor

    def convDoseToExptimeLimit(self,dose,beam_h,beam_v,flux,wavelength):
        en=12.3984/wavelength
        radd=Raddose.Raddose()
        dose_1sec=radd.getDose1sec(beam_h,beam_v,flux,en)
        print dose_1sec
        exptime_limit=dose/dose_1sec
        return exptime_limit

    def convDoseToDensityLimit(self,dose,wavelength):
        en=12.3984/wavelength
        print en
        radd=Raddose.Raddose()
        dose_per_photon=radd.getDose1sec(1.0,1.0,1,en)
        print dose_per_photon
        self.limit_dens=(dose/dose_per_photon)

        return self.limit_dens

if __name__ == "__main__":
    kuma=KUMA()
    #print kuma.estimateAttFactor(0.1,100,0.1,25,1E12,15.0)

    # 10 x 18 um beam 12.3984 keV 
    # Photon flux = 1.2E13 phs/s
    #exptime=1/30.0
    ##att=kuma.estimateAttFactor(exptime,1.0,1.0,100,1.2E13,18.0)
    #exptime_limit=kuma.convDoseToExptimeLimit(10.0,10,15,9.4E12,1.0000)
    exptime_limit=kuma.convDoseToDensityLimit(10.0,0.8000)
    print "%e"%exptime_limit

    #Flux constant is overrided to   8.2e+11
    #Beam size =  10.0 15.0  [um]
    #Photon flux=9.412e+12
    #EXP_LIMIT=     0.0621118012422
