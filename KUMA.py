import sys, os, math
import logging
import pandas as pd
from scipy import interpolate
import numpy as np
from configparser import ConfigParser, ExtendedInterpolation


# Version 2.0.0 2019/07/04 K.Hirata
class KUMA:
    def __init__(self):
        # Around 10 MGy
        self.limit_dens = 1E10  # phs/um^2 this is for 1A wavelength
        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("KUMA")
        self.debug = True

        # Dose limit file
        # en_dose_lys.csv, en_dose_oxi.csv
        # energy,dose_mgy_per_photon,density_limit
        # 左から順に、エネルギー、1フォトンあたりの線量、10MGyに到達するまでのリミット(photons/um2)
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)
        self.dose_limit_file = self.config.get("files", "dose_csv")

    # 2023/05/10 coded by K.Hirata
    def getDoseLimitParams(self,target_dose=10.0, energy=12.3984):
        # CSVファイルを読んでdataframeにする
        df = pd.read_csv(self.dose_limit_file)
        # energy .vs. dose_mgy_per_photonのグラフについてスプライン補完を行い
        # エネルギーが与えられたら、線量を返す関数を作成する
        # 戻り値はfloatとする
        en_dose_function = interpolate.interp1d(df['energy'], df['dose_mgy_per_photon'], kind='cubic')
        # energy .vs. density_limitのグラフについてスプライン補完を行い
        # エネルギーが与えられたら、density_limitを返す関数を作成する
        # 戻り値はfloatとする
        en_dens_function = interpolate.interp1d(df['energy'], df['density_limit'], kind='cubic')
        # dosePerPhoton
        dose_per_photon = en_dose_function(energy).flatten()[0]
        # density limit
        density_limit = en_dens_function(energy).flatten()[0]

        return dose_per_photon, density_limit

    def getDose1sec(self, beam_h, beam_v, flux, energy):
        # density_limit は tableにある数値 → 10 MGy に到達するまでの photon density
        dose_per_photon, density_limit = self.getDoseLimitParams(energy=energy)
        # このビームの flux density を計算する
        flux_density = flux / (beam_h * beam_v)
        # このビームの 1 sec あたりの dose を計算する
        dose_per_sec = flux_density * 10.0 / density_limit
        return dose_per_sec

    def getDose(self, beam_h, beam_v, flux, energy, exp_time):
        dose_per_sec = self.getDose1sec(beam_h, beam_v, flux, energy)
        dose = dose_per_sec * exp_time
        return dose

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
            print("att_factor=",tmp_att_fac)
            print("Nframes = ", nframes)
            print("total exp = ", total_exp_time)
            print("total photons = %8.2e" % total_n_photons)
            print("area = %8.2f  [um^2]" % area)
            print("density = %8.3e" % density, "photons/um^2")
            print("Limit   = %8.3e" % self.limit_dens, "photons/um^2")

        attfactor = self.limit_dens * (crylen * vbeam_um * osc) / (phosec * exp_per_frame * tot_phi)
        return attfactor

    def convDoseToExptimeLimit(self, dose, beam_h, beam_v, flux, wavelength):
        en = 12.3984 / wavelength
        dose_per_photon, density_limit = self.getDoseLimitParams(target_dose=dose, energy=en)

        print(f"density_limit={density_limit:e}")

        # Actual photon flux density
        actual_density = flux / (beam_h * beam_v)
        exptime_limit = density_limit / actual_density

        return exptime_limit

    def convDoseToDensityLimit(self, dose, wavelength):
        en = 12.3984 / wavelength
        # dose_per_photon, density_limit
        dose_per_photon, density_limit = self.getDoseLimitParams(target_dose=dose, energy=en)
        self.limit_dens = density_limit
        print("Limit density= %e [phs/um2]" % self.limit_dens)

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
        print("Exptime limit = ", exptime_limit)
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
            print("Exposure time is input value: %8.3f [sec]" % exp_orig)
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
            print("Exposure time was replaced by %8.4f sec" % exp_time)
            print("Measurement time will be longer than the initial condition")
            print("Initial data collection time: %8.2f [sec]" % (exp_orig * float(n_frames)))
            print("Current data collection time: %8.2f [sec]" % (exp_time * float(n_frames)))
        # Attenuator is required
        else:
            exp_time = exp_orig
            self.logger.info("Exposure time is input value: %8.2f [sec]" % exp_orig)

        return exp_time, mod_transmission
    # end of getBestCondsHelical

if __name__ == "__main__":
    #import ESA

    logfile = open("logfile.dat","w")
    kuma = KUMA()

    #print(kuma.test())

    #esa = ESA.ESA(sys.argv[1])
    #conds = esa.getDict()

    #def estimateAttFactor(self, exp_per_frame, tot_phi, osc, crylen, phosec, vbeam_um):

    exptime_limit=kuma.convDoseToExptimeLimit(10.0,10,15,9.4E12,1.0000)
    print(kuma.estimateAttFactor(0.02,360,0.1,100,9E12,15.0))

    # 10 x 18 um beam 12.3984 keV 
    # Photon flux = 1.2E13 phs/s
    # exptime=1/30.0
    ##att=kuma.estimateAttFactor(exptime,1.0,1.0,100,1.2E13,18.0)
    # exptime_limit=kuma.convDoseToDensityLimit(10.0,1.0000)
    # print "%e"%exptime_limit

    # flux = 1E13
    # dist_vec = 100.0 /1000.0
    # conds[0]['ds_hbeam'] = 20
    # conds[0]['ds_vbeam'] = 20.0
    # conds[0]['total_osc'] = 360.0

    # print("hbeam = ", conds[0]['ds_hbeam'])
    # kuma.getBestCondsHelical(conds[0], flux, dist_vec)


    flux = 5E12
    dist_vec=0.1
    # cond dictionaryを作成する
    cond = {'ds_hbeam':10.0,'ds_vbeam':15.0,'dose_ds':10.0, 'wavelength':1.0, 'exp_ds':0.02, 'total_osc':10.0, 'osc_width': 0.1, 'reduced_fact':1.0, 'ntimes':1}
    exp_time, mod_transmission=kuma.getBestCondsHelical(cond, flux, dist_vec)
    print(exp_time, mod_transmission)

    print("#########################################")
    exptime = 0.02
    total_osc = 360.0
    stepphi = 0.1
    dist_vec = 200.0
    phosec_meas = 9.9E12
    beam_vert = 15.0
    dose = 10.0
    wl_list = np.arange(0.5, 1.5, 0.1)

    dose_1sec = kuma.getDose1sec(10, 15, 9.9E12, 12.3984)
    dose_per_exptime = 0.3/dose_1sec
    print("##################################")
    print(f'dose_1sec={dose_1sec:.3f}, dose_per_exptime={dose_per_exptime:.3f}')
    print("##################################")

    for wl in wl_list:
        photon_density_limit=kuma.convDoseToDensityLimit(10.0, wl)
        print(f"density limit={photon_density_limit:8.3e}")
        limit_time = kuma.convDoseToExptimeLimit(dose,10,15,phosec_meas,wl)
        print(f"Wavelength:{wl:.3f} LIMIT_TIME={limit_time:.4f}")

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


    # Helical estimation demo

    # con