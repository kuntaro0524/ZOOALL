import sys, os, math
import logging
import pandas as pd
from scipy import interpolate
import numpy as np
from configparser import ConfigParser, ExtendedInterpolation
from dose.fields import get_dose_ds, get_dist_ds

# Version 2.0.0 2019/07/04 K.Hirata
class KUMA:
    def __init__(self):
        # Around 10 MGy
        self.limit_dens = 0.00  # phs/um^2 this is for 1A wavelength
        # Kuntaro Log file
        self.logger = logging.getLogger('ZOO').getChild("KUMA")
        self.debug = False

        # Dose limit file
        # en_dose_lys.csv, en_dose_oxi.csv
        # energy,dose_mgy_per_photon,density_limit_for10MGy
        # 左から順に、エネルギー、1フォトンあたりの線量、10MGyに到達するまでのリミット(photons/um2)
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.logger.info(f"################ Config path: {config_path}")
        self.config.read(config_path)
        self.dose_limit_file = self.config.get("files", "dose_csv")
        self.logger.info(f"### dose limit file: {self.dose_limit_file}")

    # 2023/05/10 coded by K.Hirata
    # aimed_dose: float (aimed dose in MGy)
    def getDoseLimitParams(self, aimed_dose, energy=12.3984):
        # CSVファイルを読んでdataframeにする
        df = pd.read_csv(self.dose_limit_file)
        # energy .vs. dose_mgy_per_photonのグラフについてスプライン補完を行い
        # エネルギーが与えられたら、線量を返す関数を作成する
        # 戻り値はfloatとする
        en_dose_function = interpolate.interp1d(df['energy'], df['dose_mgy_per_photon'], kind='cubic')
        # dose_per_photon: CSV 2nd column
        dose_per_photon = en_dose_function(energy).flatten()[0]
        # density_limit: CSV 3rd column (10MGyに到達するまでの photon density)
        density_limit = interpolate.interp1d(df['energy'], df['density_limit_for10MGy'], kind='cubic')(energy).flatten()[0]
        #print(f"aimed_dose={aimed_dose} MGy, energy={energy} keV, dose_per_photon={dose_per_photon} MGy/photon, density_limit={density_limit} phs/um^2 for 10 MGy")
        if self.debug:
            self.logger.info(f"aimed_dose={type(aimed_dose)} {aimed_dose:.3f} MGy, energy={energy:.3f} keV")
        # aimed_dose_per_photon
        aimed_dose_per_photon = aimed_dose / 10.0 * dose_per_photon
        # aimed_density_limit
        aimed_density_limit = aimed_dose / 10.0 * density_limit
        # set self.limit_dens
        self.limit_dens = aimed_density_limit

        return aimed_dose_per_photon, aimed_density_limit

    def getDose1sec(self, beam_h, beam_v, flux, energy):
        """
        Calculate dose rate [MGy/s] from beam geometry, flux, and photon energy.
        The '10 MGy' reference in CSV is used internally; no explicit constant here.
        """
        # use the CSV-based dose_per_photon directly
        dose_per_photon, _ = self.getDoseLimitParams(aimed_dose=1.0, energy=energy)
        # getDoseLimitParams scales linearly with aimed_dose,
        # so aimed_dose=1.0 simply returns 1 MGy-equivalent dose_per_photon value.
    
        flux_density = flux / (beam_h * beam_v)       # photons/(s·µm²)
        dose_per_sec = flux_density * dose_per_photon # MGy/s

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
        # Logging
        self.logger.info(f"Estimate Attenuation Factor:{tmp_att_fac:.3f}")
        self.logger.info(f"Nframes = {nframes}")
        self.logger.info(f"total exp = {total_exp_time:.3f} [sec]")
        self.logger.info(f"total photons = {total_n_photons:.3e} [photons]")
        self.logger.info(f"X-ray irradiated area = {area:.3f} [um^2]")
        self.logger.info(f"density on a crystal= {density:.3e} [photons/um^2]")
        self.logger.info(f"Density limit for aimed dose {self.limit_dens:.3e} [photons/um^2]")

        attfactor = self.limit_dens * (crylen * vbeam_um * osc) / (phosec * exp_per_frame * tot_phi)
        return attfactor

    def convDoseToExptimeLimit(self, dose, beam_h, beam_v, flux, wavelength):
        en = 12.3984 / wavelength

        # density limit for aimed dose
        dose_per_photon, density_limit = self.getDoseLimitParams(aimed_dose=dose, energy=en)
        self.logger.info(f"Energy={en:.3f}, dose_per_photon={dose_per_photon:.2e}, density_limit={density_limit:.3e}")

        # Actual photon flux density
        actual_density = flux / (beam_h * beam_v)
        exptime_limit = density_limit / actual_density

        return exptime_limit

    def convDoseToDensityLimit(self, dose, wavelength):
        en = 12.3984 / wavelength
        # dose_per_photon, density_limit
        dose_per_photon, density_limit = self.getDoseLimitParams(aimed_dose=dose, energy=en)
        self.limit_dens = density_limit
        self.logger.info(f"Limit density for {dose:.3f} MGy at {en:.3f} keV = {self.limit_dens:.3e} [photons/um^2]")

        return self.limit_dens

    def getNframe(self, cond):
        n_frames = int(cond['total_osc'] / cond['osc_width'])
        return n_frames

    def checkDoseString(self, dose_string, mode):
        # Multiのときは１つだけ
        if mode=="multi":
            # 文字列は "[10.0]" のようになっている
            try:
                self.logger.info(f"Current dose string: {dose_string}")
                dose_value = float(dose_string.strip("{}"))
            except ValueError:
                self.logger.error(f"Invalid dose string format: {dose_string}. Expected format is '[value]'.")
                raise ValueError("Invalid dose string format.")
            return dose_value
        elif mode=="helical":
            # Helicalのときは"{10.0, 20.0, 30.0}" のようになっている
            dose_list = dose_string.strip("{}").split(',')
            return dose_list

    # やむをえず作成 2025/07/18
    # HEBIの中でsingleに切り替わったときには dose_ds には単一の数値が入っている
    # 昔はgetBestCondsMultiを呼んでいたのだがそれではまずいことが判明した
    # 2025/10/07 ChatGPTの提案を受け入れて改修
    def getBestCondsSingle(self, cond, flux):
        from Libs.dose.fields import get_dose_ds, get_dist_ds

        mode = cond.get("mode", "single")
        if mode != "single":
            raise ValueError(f"getBestCondsSingle() called with mode='{mode}'. Expected 'single'.")
    
        n_frames = self.getNframe(cond)
        results = []
        exptime_limit = self.convDoseToExptimeLimit(
            cond['dose_ds'], cond['ds_hbeam'], cond['ds_vbeam'], flux, cond['wavelength']
        )
        best_transmission = exptime_limit / float(n_frames) / cond['exp_ds']
        mod_transmission = cond['reduced_fact'] * best_transmission

        exp_orig = cond['exp_ds']
        if mod_transmission >= 1.0:
            exp_time = exptime_limit / float(n_frames)
            mod_transmission = 1.0
            self.logger.info(f"[single dose={cond['dose_ds']} exp -> {exp_time:.3f}s (limit reached)")
        else:
            exp_time = exp_orig
            self.logger.info(f"[single dose={cond['dose_ds']}, exp uses input {exp_time:.3f}s")
    
        return exp_time, mod_transmission

    def getBestCondsMulti(self, cond, flux):
        from Libs.dose.fields import get_dose_ds, get_dist_ds
        # --- 基本設定 ---
        n_frames = self.getNframe(cond)

        # --- dose_ds の取得と検証 ---
        dose_list = get_dose_ds(cond)
        if not dose_list:
            raise ValueError("dose_ds is empty or invalid.")

        # Multiモードでは単一値のみ許可
        if len(dose_list) > 1:
            raise ValueError(
                f"Multiple dose_ds values detected ({dose_list}) "
                f"but mode='{cond.get('mode')}'. Only one value allowed in 'multi' mode."
            )

        # dist_ds がある場合も同様に確認（将来の拡張用）
        dist_list = get_dist_ds(cond)
        if len(dist_list) > 1:
            raise ValueError(
                f"Multiple dist_ds values detected ({dist_list}) "
                f"but mode='{cond.get('mode')}'. Only one value allowed in 'multi' mode."
            )

        cond['dose_ds'] = float(dose_list[0])

        # --- 計算部分 ---
        exptime_limit = self.convDoseToExptimeLimit(
            cond['dose_ds'],
            cond['ds_hbeam'],
            cond['ds_vbeam'],
            flux,
            cond['wavelength']
        )

        best_transmission = exptime_limit / float(n_frames) / cond['exp_ds']
        mod_transmission = cond['reduced_fact'] * best_transmission

        self.logger.info(f"Multi: Exposure time limit for dose {cond['dose_ds']:.2f} MGy = {exptime_limit:.5f}")
        self.logger.info(f"Multi: Utilized flux = {flux:.2e}")

        # --- Attenuator 判定 ---
        exp_orig = cond['exp_ds']
        if mod_transmission >= 1.0:
            exp_time = exptime_limit / float(n_frames)
            mod_transmission = 1.0
            self.logger.info(f"Exposure time was replaced by {exp_time:.3f} sec")
            self.logger.info(f"Initial data collection time: {exp_orig * n_frames:.2f} [sec]")
            self.logger.info(f"Current data collection time: {exp_time * n_frames:.2f} [sec]")
        else:
            exp_time = exp_orig
            self.logger.info(f"Exposure time is input value: {exp_orig:.3f} [sec]")

        return exp_time, mod_transmission

    # 2025/07/09 dose_listに対応はしているが、この関数の呼び出し以降は
    # dose_listを使わず、cond['dose_ds']に数値が単体で入っている
    # (HEBI.pyの中で展開してからこちらの呼び出しをしている)
    # 2025/10/07 ChatGPTの提案を受け入れて改修
    def getBestCondsHelical(self, cond, flux, dist_vec_mm):
        """
        単一 (dose_ds, dist_ds) ペアを入力として、
        ヘリカル測定条件に基づく露光時間と透過率を計算する。
    
        仕様:
          - HEBI 側で展開済みの単一ペアを受け取る想定。
          - 複数値 (list) が渡された場合はエラー。
        """
        mode = cond['mode']
        if mode != "helical" and mode != "mixed":
            raise ValueError(f"getBestCondsHelical() called with mode='{mode}'. Expected 'helical'.")
    
        dose_val = cond.get("dose_ds")
        dist_val = cond.get("dist_ds")
    
        # --- 型チェック ---
        if isinstance(dose_val, (list, tuple)):
            raise ValueError(f"getBestCondsHelical(): dose_ds should be scalar, got list {dose_val}")
        if isinstance(dist_val, (list, tuple)):
            raise ValueError(f"getBestCondsHelical(): dist_ds should be scalar, got list {dist_val}")
    
        dose_val = float(dose_val)
        dist_val = float(dist_val)
    
        photon_density_limit = self.convDoseToDensityLimit(dose_val, cond['wavelength'])
        dist_vec_um = dist_vec_mm * 1000.0  # mm → μm
    
        self.logger.info(f"Flux density limit for dose {dose_val:.5f} MGy = {photon_density_limit:.2e}")
        self.logger.info(f"Utilized Beam = {cond['ds_vbeam']:.2f} x {cond['ds_hbeam']:.2f} [μm]")
        self.logger.info(f"Utilized flux = {flux:.2e} [phs/sec]")
    
        best_transmission = self.estimateAttFactor(
            cond['exp_ds'], cond['total_osc'], cond['osc_width'],
            dist_vec_um, flux, cond['ds_vbeam']
        )
    
        self.logger.info(f"KUMA: Best attenuation factor = {best_transmission:.7f}")
        self.logger.info(f"Reduced factor for dose slicing = {cond['reduced_fact']:.5f}")
        self.logger.info(f"Number of datasets = {cond['ntimes']:d}")
    
        mod_transmission = cond['reduced_fact'] * best_transmission
        self.logger.info(f"Modified transmission = {mod_transmission:.5f}")
    
        exp_orig = cond['exp_ds']
        n_frames = self.getNframe(cond)
    
        if mod_transmission >= 1.0:
            exp_time = exp_orig * mod_transmission
            mod_transmission = 1.0
            self.logger.info(f"[dose={dose_val}, dist={dist_val}] Exposure time adjusted: {exp_time:.4f}s")
        else:
            exp_time = exp_orig
            self.logger.info(f"[dose={dose_val}, dist={dist_val}] Using original exposure {exp_time:.3f}s")
    
        # 常にタプルで返す（HEBI 側の期待仕様）
        return exp_time, mod_transmission

if __name__ == "__main__":
    #import ESA

    kuma = KUMA()

    # logger setting
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    #kuma.logger.setLevel(logging.DEBUG)
    kuma.logger.setLevel(logging.INFO)
    kuma.debug = True
    
    #exptime_limit=kuma.convDoseToExptimeLimit(10.0,10,15,9.4E12,1.0000)
    #print(kuma.estimateAttFactor(0.02,360,0.1,100,9E12,15.0))

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

    # Dose estimation of 'helical data collection'
    flux = 5E12
    dist_vec=0.1
    # string type of dose values
    dose_ds = 5.0
    #dose_ds = "{1.0,5.0,10.0}"
    dist_ds = 110.0
    # Test for helical
    # cond dictionaryを作成する
    cond = {'ds_hbeam':10.0,'ds_vbeam':15.0,'dose_ds':dose_ds, 'dist_ds':dist_ds,'wavelength':1.0, 'exp_ds':0.02, 'total_osc':360.0, 'osc_width': 0.1, 'reduced_fact':0.2, 'ntimes':5,'mode':"helical"}
    exp_time, mod_transmission=kuma.getBestCondsHelical(cond, flux, dist_vec)
    print(f"suitable exposure time: {exp_time:.4f} sec, modified transmission: {mod_transmission:.5f}")
    """

    # Test for multi
    dose_ds = "{1.0,5.0,10.0}"
    dist_ds = "{110.0,120.0}"
    cond = {'ds_hbeam':10.0,'ds_vbeam':15.0,'dose_ds':dose_ds, 'dist_ds':dist_ds,'wavelength':1.0, 'exp_ds':0.02, 'total_osc':360.0, 'osc_width': 0.1, 'reduced_fact':0.2, 'ntimes':5}
    exp_time, mod_transmission=kuma.getBestCondsMulti(cond, flux)
    print(f"suitable exposure time: {exp_time:.4f} sec, modified transmission: {mod_transmission:.5f}")
    """

    """
    # Dose estimation of 'SWSX' data collection
    cond = {'ds_hbeam':10.0,'ds_vbeam':15.0,'dose_ds':"0.1+1.0+1.0+1.0",'wavelength':1.0, 'exp_ds':0.02, 'total_osc':360.0, 'osc_width': 0.1, 'reduced_fact':0.2, 'ntimes':5}
    exp_time, mod_transmission=kuma.getBestCondsHelical(cond, flux, dist_vec)

    # Dose slicing test
    cond = {'ds_hbeam':10.0,'ds_vbeam':15.0,'dose_ds':"{10.0}", 'wavelength':1.0, 'exp_ds':0.02, 'total_osc':360.0, 'osc_width': 0.1, 'reduced_fact':0.2, 'ntimes':5}
    kuma.getBestCondsMulti(cond,flux)
    """

    """

    print("#########################################")
    exptime = 0.02
    total_osc = 360.0
    stepphi = 0.1
    dist_vec = 200.0
    phosec_meas = 9.9E12
    beam_vert = 15.0
    dose = 10.0
    wl_list = np.arange(0.5, 1.5, 0.1)

    # getDose の挙動テスト
    dose_tmp = kuma.getDose(1,1,2E10,12.3984,1.0)
    print(f"getDose: {dose_tmp:.3f}")

    dose_1sec = kuma.getDose1sec(10, 15, 9.9E12, 12.3984)
    dose_per_exptime = 0.01*dose_1sec
    print("##################################")
    print(f'dose_1sec={dose_1sec:.3f}, dose_per_exptime={dose_per_exptime:.3f}')
    print("##################################")

    for wl in wl_list:
        photon_density_limit=kuma.convDoseToDensityLimit(10.0, wl)
        print(f"density limit={photon_density_limit:8.3e}")
        limit_time = kuma.convDoseToExptimeLimit(dose,10,15,phosec_meas,wl)
        print(f"Wavelength:{wl:.3f} LIMIT_TIME={limit_time:.4f}")
    """