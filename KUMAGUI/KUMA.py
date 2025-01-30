import sys, os, math, numpy

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Raddose
import logging
import BSSconfig

# Version 2.0.0 2019/07/04 K.Hirata
class KUMA:
    def __init__(self):
        # Around 10 MGy
        self.limit_dens = 1E10  # phs/um^2 this is for 1A wavelength
        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("KUMA")

        self.debug = True

    def setPhotonDensityLimit(self, value):
        self.limit_dens = value

    def estimateAttFactor(self, exp_per_frame, tot_phi, osc, crylen, phosec, vbeam_um):
        area = crylen * vbeam_um
        nframes = tot_phi / osc
        total_exp_time = exp_per_frame * nframes
        total_n_photons = total_exp_time * phosec
        density = total_n_photons / area
        tmp_att_fac = self.limit_dens / density
        if self.debug == True:
            print "att_factor=",tmp_att_fac
            print "Nframes = ", nframes
            print "total exp = ", total_exp_time
            print "total photons = %8.2e" % total_n_photons
            print "area = %8.2f  [um^2]" % area
            print "density = %8.3e" % density, "photons/um^2"
            print "Limit   = %8.3e" % self.limit_dens, "photons/um^2"

        attfactor = self.limit_dens * (crylen * vbeam_um * osc) / (phosec * exp_per_frame * tot_phi)
        return attfactor

    def convDoseToExptimeLimit(self, dose, beam_h, beam_v, flux, wavelength):
        en = 12.3984 / wavelength
        radd = Raddose.Raddose()
        dose_1sec = radd.getDose1sec(beam_h, beam_v, flux, en)
        print dose_1sec
        exptime_limit = dose / dose_1sec
        return exptime_limit

    def convDoseToDensityLimit(self, dose, wavelength):
        en = 12.3984 / wavelength
        radd = Raddose.Raddose()
        dose_per_photon = radd.getDose1sec(1.0, 1.0, 1, en)
        print "Dose per photon=",dose_per_photon
        self.limit_dens = (dose / dose_per_photon)
        print "Limit density= %e [phs/um2]" % self.limit_dens

        return self.limit_dens

    def getNframe(self, cond):
        n_frames = int(cond['total_osc'] / cond['osc_width'])
        return n_frames

    def getBestCondsMulti(self, cond, flux):
        n_frames = self.getNframe(cond)
        exptime_limit = self.convDoseToExptimeLimit(cond['dose_ds'], cond['ds_hbeam'], cond['ds_vbeam'], flux,
                                                    cond['wavelength'])
        best_transmission = exptime_limit / float(n_frames) / cond['exp_ds']

        mod_transmission = cond['reduced_fact'] * best_transmission
        print "Exptime limit = ", exptime_limit
        self.logger.info("Multi: Exposure time limit for dose %5.2f MGy = %10.5f " % (cond['dose_ds'], exptime_limit))
        self.logger.info("Multi: Utilized flux = %5.2e " % flux)

        # Attenuator is not required
        exp_orig = cond['exp_ds']
        if mod_transmission >= 1.0:
            exp_time = exptime_limit / float(n_frames)
            mod_transmission = 1.0
            self.logger.info("Exposure time was replaced by %8.3f sec" % exp_time)
            self.logger.info("Measurement time will be longer than the initial condition")
            self.logger.info("Initial data collection time: %8.2f [sec]" % (exp_orig * float(n_frames)))
            self.logger.info("Current data collection time: %8.2f [sec]" % (exp_time * float(n_frames)))
        # Attenuator is required
        else:
            exp_time = exp_orig
            print "Exposure time is input value: %8.3f [sec]" % exp_orig
        return exp_time, mod_transmission

    def getBestCondsHelical(self, cond, flux, dist_vec_mm):
        # type: (condition dictionary, flux value) -> exp_time, best_transmission
        self.logger.info("getBestCondsHelical starts\n")

        photon_density_limit = self.convDoseToDensityLimit(cond['dose_ds'], cond['wavelength'])
        dist_vec_um = dist_vec_mm * 1000.0  # [um]
        self.logger.info("Flux density limit for dose %5.2f MGy= %5.2e " % (cond['dose_ds'], photon_density_limit))
        self.logger.info("Utilized Beam = %5.2f x %5.2f [um]" % (cond['ds_vbeam'], cond['ds_hbeam']))
        self.logger.info("Utilized flux = %5.2e [phs/sec]" % flux)
        best_transmission = self.estimateAttFactor(cond['exp_ds'], cond['total_osc'],
                                                   cond['osc_width'], dist_vec_um, flux, cond['ds_vbeam'])
        # Dose slicing is considered
        self.logger.info("KUMA: Best attenuation factor=%8.5f" % best_transmission)
        self.logger.info("Reduced factor for dose slicing: %8.5f" % cond['reduced_fact'])
        self.logger.info("The number of datasets to be collected: %5d" % cond['ntimes'])
        mod_transmission = cond['reduced_fact'] * best_transmission
        self.logger.info("modified transmission for dose slicing %9.5f" % mod_transmission)

        # Attenuator is not required
        exp_orig = cond['exp_ds']
        n_frames = self.getNframe(cond)

        if mod_transmission >= 1.0:
            exp_time = exp_orig * mod_transmission
            mod_transmission = 1.0
            print "Exposure time was replaced by %8.4f sec" % exp_time
            print "Measurement time will be longer than the initial condition"
            print "Initial data collection time: %8.2f [sec]" % (exp_orig * float(n_frames))
            print "Current data collection time: %8.2f [sec]" % (exp_time * float(n_frames))
        # Attenuator is required
        else:
            exp_time = exp_orig
            self.logger.info("Exposure time is input value: %8.2f [sec]" % exp_orig)

        return exp_time, mod_transmission


if __name__ == "__main__":
    import ESA

    logfile = open("logfile.dat","w")
    kuma = KUMA(logfile)

    esa = ESA.ESA(sys.argv[1])
    conds = esa.getDict()

    # print kuma.estimateAttFactor(0.1,100,0.1,25,1E12,15.0)

    # 10 x 18 um beam 12.3984 keV 
    # Photon flux = 1.2E13 phs/s
    # exptime=1/30.0
    ##att=kuma.estimateAttFactor(exptime,1.0,1.0,100,1.2E13,18.0)
    # exptime_limit=kuma.convDoseToExptimeLimit(10.0,10,15,9.4E12,1.0000)
    # exptime_limit=kuma.convDoseToDensityLimit(10.0,1.0000)
    # print "%e"%exptime_limit

    flux = 1E13
    dist_vec = 100.0 /1000.0
    conds[0]['ds_hbeam'] = 20
    conds[0]['ds_vbeam'] = 20.0
    conds[0]['total_osc'] = 360.0

    print "hbeam = ", conds[0]['ds_hbeam']
    kuma.getBestCondsHelical(conds[0], flux, dist_vec)


    flux = 5E12
    conds[0]['ds_hbeam'] = 10.0
    print "hbeam = ", conds[0]['ds_hbeam']
    kuma.getBestCondsHelical(conds[0], flux, dist_vec)

    """
    exptime = 0.02
    total_osc = 360.0
    stepphi = 0.1
    dist_vec = 20.0
    phosec_meas = 1.64E13
    beam_vert = 20.0
    dose = 6.5
    photon_density_limit=kuma.convDoseToDensityLimit(10.0, 0.9)
    limit_time = kuma.convDoseToExptimeLimit(dose,20,20,phosec_meas, 0.9)
    print "LIMIT_TIME=",limit_time

    frame = 3600.0
    exp_per_frame_limit = limit_time / frame

    print exp_per_frame_limit
    print exp_per_frame_limit / exptime
    """

    """
    for dist_vec in range(50,500,10.0):
        transmission=kuma.estimateAttFactor(exptime,total_osc,stepphi,dist_vec,phosec_meas,beam_vert)
        #print "%e"%photon_density_limit
        print "%5.2f [um] crystal Trans =" % dist_vec, transmission
    """
    # Flux constant is overrided to   8.2e+11
    # Beam size =  10.0 15.0  [um]
    # Photon flux=9.412e+12
    # EXP_LIMIT=     0.0621118012422
