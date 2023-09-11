#coding: UTF-8
"""
(C) RIKEN/JASRI 2020 :
Author: Kunio Hirata
ESA -> the main function : the class to read & write zoo database file
This code is originally written by K.Hirata and modified by N.Mizuno.
NM added function to read xlsx file directly and output zoo.db by using ESA class.

Author: Nobuhiro Mizuno
"""
import sys, os, math, numpy, csv, re, datetime, xlrd, codecs
import configparser
import pandas as pd
import numpy as np
import KUMA
# logger の設定
import logging
from configparser import ConfigParser, ExtendedInterpolation

class UserESA():
    def __init__(self, fname=None, root_dir=".", beamline=None):
        # beamlineの名前はconfigから読む
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        self.fname = fname
        self.isRead = None
        self.isPrep = None
        self.isGot  = None
        self.zoocsv = None
        self.contents = []

        # configure file から情報を読む: beamlineの名前
        self.beamline = self.config.get("beamline", "beamline")
        import BeamsizeConfig
        self.bsconf = BeamsizeConfig.BeamsizeConfig()

        # CSV prefix
        self.csv_prefix = self.fname.replace(".xlsx","")

        # logger の設定
        self.logger = logging.getLogger("ZOO")
        self.logger.setLevel(logging.DEBUG)
        # levelがwarningのときには標準出力とファイル両方に出力する
        
        # create file handler which logs even debug messages
        self.logger_fh = logging.FileHandler('useresa.log')
        self.logger_fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        self.logger_ch = logging.StreamHandler()
        self.logger_ch.setLevel(logging.WARNING)
        # create formatter and add it to the handlers
        self.logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger_fh.setFormatter(self.logger_formatter)
        self.logger_ch.setFormatter(self.logger_formatter)
        # add the handlers to logger
        self.logger.addHandler(self.logger_fh)
        self.logger.addHandler(self.logger_ch)

        self.root_dir = root_dir

    def setDefaults(self):
        # self.df に以下のカラムを追加する
        # self.config.getfloat("experiment", "score_min") などで読み込む
        # "score_min"
        # "score_max"
        # "raster_dose"
        # "dose_ds"
        # "raster_roi"
        # "exp_raster"
        # "att_raster"
        # "hebi_att"
        # "cover_flag"
        # "exp_ds"
        self.df["score_min"] = self.config.getfloat("experiment", "score_min")
        self.df["score_max"] = self.config.getfloat("experiment", "score_max")
        self.df["raster_dose"] = self.config.getfloat("experiment", "raster_dose")
        self.df["dose_ds"] = self.config.getfloat("experiment", "dose_ds")
        self.df["raster_roi"] = self.config.getfloat("experiment", "raster_roi")
        self.df["exp_ds"] = self.config.getfloat("experiment", "exp_ds")
        self.df["exp_raster"] = self.config.getfloat("experiment", "exp_raster")
        # att_raster の数値を取得して小数点以下第一位までに丸める
        self.df["att_raster"] = self.config.getfloat("experiment", "att_raster")
        self.df["att_raster"] = round(self.df["att_raster"], 1)
        self.df["hebi_att"] = self.df["att_raster"]
        self.df["cover_scan_flag"] = self.config.getint("experiment", "cover_flag")
        # 結晶サイズは max_crystal_size として読み込む
        self.df['cry_min_size_um'] = self.df['max_crystal_size']
        self.df['cry_max_size_um'] = self.df['max_crystal_size']
        # root_dir は self.root_dir として読み込む
        self.df['root_dir'] = self.root_dir
        # p_indexはDataFrameのインデックスと同じで良い
        self.df['p_index'] = self.df.index
        # offset_angle は 0 とする
        self.df['offset_angle'] = 0
        # reduced_fact は 1 とする
        self.df['reduced_fact'] = 1
        # ntimes は 1 とする
        self.df['ntimes'] = 1
        # meas_name は 変換に利用したファイル名を入れておく
        self.df['meas_name'] = self.fname 
        # hel_full_osc,hel_part_osc
        self.df['hel_full_osc'] = 60.0
        self.df['hel_part_osc'] = 30.0

        # 'desired_exp' と 'mode' から実験パラメータを設定する
        # 1) desired_exp が "scan_only" のとき 
        # score_min, score_max ともに 9999 とする
        # raster_dose: 0.3, dose_ds: 0.0, cover_flag: 0
        self.df.loc[self.df['desired_exp'] == "scan_only", 'score_min'] = 9999
        self.df.loc[self.df['desired_exp'] == "scan_only", 'raster_dose'] = 0.3
        self.df.loc[self.df['desired_exp'] == "scan_only", 'dose_ds'] = 0.0
        self.df.loc[self.df['desired_exp'] == "scan_only", 'cover_scan_flag'] = 0

        # 2) desired_exp が "normal" のとき
        # mode が "helical" の場合には、score_max を 9999 とする
        self.df.loc[self.df['desired_exp'] == "normal", 'score_max'] = 9999

        # 3) desired_exp が "ultra_high_dose_scan" のとき
        # dose_ds = 9.0 とする
        self.df.loc[self.df['desired_exp'] == "ultra_high_dose_scan", 'dose_ds'] = 9.0
        # 4) desired_exp が "phaing" のとき
        # dose_ds = 5.0 とする
        self.df.loc[self.df['desired_exp'] == "phasing", 'dose_ds'] = 5.0

    # ビームライン、実験モードと結晶のタイプから実験パラメータを取得する
    # 2023/05/09 type_crystal は使わない
    def getParams(self, desired_exp_string, mode):
        desired_exp_string = desired_exp_string.lower()

        # DEFAULT PARAMETER
        # beamline.ini から読む
        #self.beamline = self.config.get("beamline", "beamline")
        score_min   = self.config.getfloat("experiment", "score_min")
        score_max   = self.config.getfloat("experiment", "score_max")
        raster_dose = self.config.getfloat("experiment", "raster_dose")
        dose_ds     = self.config.getfloat("experiment", "dose_ds")
        raster_roi  = self.config.getfloat("experiment", "raster_roi")
        exp_raster = self.config.getfloat("experiment", "exp_raster")
        att_raster  = self.config.getfloat("experiment", "att_raster")
        hebi_att    = self.config.getfloat("experiment", "hebi_att")
        cover_flag  = self.config.getint("experiment", "cover_flag")

        # PARAMTER CONDITION
        self.param = {
            "scan_only":{
                "single":   [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                "helical":  [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                "multi":    [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
                "mixed":    [9999, 9999, 0.3, dose_ds, 0, exp_raster, att_raster, hebi_att, 0],
            },
            "normal":{
                "single":   [score_min, score_max, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, score_max, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, 9999, 0.1, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
            },
            "high_dose_scan":{
                "single":   [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, 9999, 0.05, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
            },
            "ultra_high_dose_scan":{
                "single":   [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "helical":  [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "multi":    [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "mixed":    [score_min, score_max, 0.2, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
            },
            "phasing":{
                "single":   [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999, 0.05, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, score_max, 0.1, 5, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
            },
            "rapid":{
                "single":   [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "helical":  [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "multi":    [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
                "mixed":    [score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, 100, 100, cover_flag],
            },
        }

        return self.param[desired_exp_string][mode]
    
    def checkLN2flag(self):
        # self.dfのカラム "ln2_flag" について以下のパターンで処理を行う
        # 'NaN'であれば ０
        # 'Yes' or 'yes' or "YES" であれば １
        # 'Unavailable' であれば ０
        # それ以外であれば ０
        self.df['ln2_flag'] = self.df['ln2_flag'].fillna(0)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('Yes', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('yes', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('YES', 1)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('Unavailable', 0)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('-', 0)

        #print(self.df)

    def checkZoomFlag(self):
        # self.dfのカラム "ln2_flag" について以下のパターンで処理を行う
        # 'NaN'であれば ０
        # 'Yes' or 'yes' or "YES" であれば １
        # 'Unavailable' であれば ０
        # それ以外であれば ０
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].fillna(0)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('Yes', 1)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('yes', 1)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('YES', 1)
        # self.df['zoomcap_flag']が　'No' or 'no' or 'NO' or 'Unavailable' であれば ０
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('No', 0)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('no', 0)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('NO', 0)
        self.df['zoomcap_flag'] = self.df['zoomcap_flag'].replace('Unavailable', 0)

        # DataFrameを省略することなく表示する
        pd.set_option('display.max_rows', None)
        #print(self.df)

    def checkPinFlag(self):
        #print(self.df['pin_flag'])
        # self.df['warm_time']の初期値を30.0とする
        self.df['warm_time'] = 30.0
        # self.df にはすでに"pin_flag"があるので、それを利用する
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "spine"　であれば self.df['warm_time'] = 10.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'spine', 'warm_time'] = 10.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "als + ssrl"　であれば self.df['warm_time'] = 20.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'als + ssrl', 'warm_time'] = 20.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "copper"　であれば self.df['warm_time'] = 60.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'copper', 'warm_time'] = 60.0
        # self.df['pin_flag']の文字列を小文字に変換した文字列が "no-wait"　であれば self.df['warm_time'] = 0.0
        self.df.loc[self.df['pin_flag'].str.lower() == 'no-wait', 'warm_time'] = 0.0

    def fillFlux(self):
        # self.df['flux']の数値を読み込む
        # self.bsconf.getFluxAtWavelength(hbeam, vbeam, wavelength)を呼び出す
        # この関数の引数に self.df['hbeam'], self.df['vbeam'], self.df['wavelength']を渡す
        # 戻り値はfluxである
        # fluxの値をself.df['flux']に代入する
        self.df['flux'] = self.df.apply(lambda x: self.bsconf.getFluxAtWavelength(x['ds_hbeam'], x['ds_vbeam'], x['wavelength']), axis=1)

    def splitBeamsizeInfo(self):
        # self.df['beamsize']の文字列をself.checkBeamsizeの引数として渡す
        # self.checkBeamsize()は self.df['beamsize']を引数とし、戻り値は(hbeam, vbeam)である(どちらもfloatのタプル)
        # hbeam, vbeamの数値は新たなカラムとしてself.dfに追加される 'hbeam', 'vbeam'
        self.df['ds_hbeam'], self.df['ds_vbeam'] = zip(*self.df['beamsize'].map(self.checkBeamsize))
        self.df['raster_hbeam'], self.df['raster_vbeam'] = zip(*self.df['beamsize'].map(self.checkBeamsize))

    # Raster scanの露光条件を定義する
    # Pandas dataframeに対して一気に処理を行う
    def defineScanCondition(self):
        # Dose estimation will be conducted by KUMA
        kuma = KUMA.KUMA()
    
        # self.df['wavelgnth']からself.df['energy']を計算する
        self.df['energy'] = 12.3984 / self.df['wavelength']

        # self.df['desired_exp']の文字列を小文字に変換した文字列が "normal", "scan_only", "phasing", "rapid"の場合は以下の処理を行う
        # photons_per_image は 4E10 で固定する
        # photons_per_exptime は flux * exp_raster で計算する
        # df['att_raster'] = photons_per_image / photons_per_exptime * 100.0 とする
        # df['hebi_att'] = photons_per_image / photons_per_exptime * 100.0 とする
        # maskを利用して条件ごとに処理をしていく
        mask1 = (self.df['desired_exp'] == 'normal') | (self.df['desired_exp'] == 'scan_only') | (self.df['desired_exp'] == 'phasing') | (self.df['desired_exp'] == 'rapid')
        photons_per_image = 4E10
        # 1 secあたりの最大フォトン数を計算する
        photons_per_exptime = self.df['flux'] * self.df['exp_raster']
        # 1 frameあたりに必要なフォトン数を入れるためのatt_factorを計算する
        self.df.loc[mask1, 'att_raster'] = photons_per_image / photons_per_exptime * 100.0
        # 1 frameあたりに必要なフォトン数を入れるためのhebi_att_factorを計算する
        self.df.loc[mask1, 'hebi_att'] = photons_per_image / photons_per_exptime * 100.0
        # 1 frameあたりのphotonsを計算する
        self.df.loc[mask1, 'ppf_raster'] = photons_per_image
        # 1 frameあたりのdoseを計算する
        # kuma.getDose()の引数は hbeam, vbeam, flux, energy, exp_raster
        # dose_per_frame = kuma.getDose(hbeam, vbeam, flux, energy, exp_raster) * self.df['att_raster'] / 100.0
        self.df.loc[mask1, 'dose_per_frame'] = kuma.getDose(self.df['ds_hbeam'], self.df['ds_vbeam'], self.df['flux'], self.df['energy'], self.df['exp_raster']) * self.df['att_raster'] / 100.0

        # mask2 
        mask2 = (self.df['desired_exp'] == 'high_dose_scan')
        dose_for_raster = 0.30 # MGy
        # 1 frameあたりのdoseを計算する
        self.df.loc[mask2, 'dose_per_frame'] = kuma.getDose(self.df['ds_hbeam'], self.df['ds_vbeam'], self.df['flux'], self.df['energy'], self.df['exp_raster'])
        # transmissionは dose_for_raster / dose_per_frame * 100.0 で計算する
        self.df.loc[mask2, 'att_raster'] = dose_for_raster / self.df['dose_per_frame'] * 100.0
        self.df.loc[mask2, 'hebi_att'] = dose_for_raster / self.df['dose_per_frame'] * 100.0
        # 'ppf' = photons per frame
        self.df.loc[mask2, 'ppf_raster'] = self.df['flux'] * self.df['exp_raster'] * self.df['att_raster'] / 100.0
        # dose_per_frame = kuma.getDose(hbeam, vbeam, flux, energy, exp_raster) * self.df['att_raster'] / 100.0
        self.df.loc[mask2, 'dose_per_frame'] = kuma.getDose(self.df['ds_hbeam'], self.df['ds_vbeam'], self.df['flux'], self.df['energy'], self.df['exp_raster']) * self.df['att_raster'] / 100.0

        # masks
        mask3 = (self.df['desired_exp'] == 'ultra_high_dose_scan')
        dose_for_raster = 1.0 # MGy
        # 1 frame あたりのdoseを計算する
        self.df.loc[mask3, 'dose_per_frame'] = kuma.getDose(self.df['ds_hbeam'], self.df['ds_vbeam'], self.df['flux'], self.df['energy'], self.df['exp_raster'])
        # transmissionは dose_for_raster / dose_per_frame * 100.0 で計算する
        self.df.loc[mask3, 'att_raster'] = dose_for_raster / self.df['dose_per_frame'] * 100.0
        self.df.loc[mask3, 'hebi_att'] = dose_for_raster / self.df['dose_per_frame'] * 100.0
        # 'ppf' = photons per frame
        self.df.loc[mask3, 'ppf_raster'] = self.df['flux'] * self.df['exp_raster'] * self.df['att_raster'] / 100.0
        # dose_per_frame = kuma.getDose(hbeam, vbeam, flux, energy, exp_raster) * self.df['att_raster'] / 100.0
        self.df.loc[mask3, 'dose_per_frame'] = kuma.getDose(self.df['ds_hbeam'], self.df['ds_vbeam'], self.df['flux'], self.df['energy'], self.df['exp_raster']) * self.df['att_raster'] / 100.0

        #print(self.df)


    # end of defineScanCondition()

    def makeExpWarning(self): 
        # 1 frameあたりのdoseが0.3MGyを超えていて、self.df['desired_exp'] が 'high_dose_scan' もしくは 'ultra_high_dose_scan'出ない場合は警告を出す
        # 丁寧な文字列でloggerを出力する
        # "Warning: dose/frame exceeds 0.3 MGy. Please check the exposure condition."
        # "puckid: 'sample' pinid: 01 dose/frame 0.5 MGy"
        mask = (self.df['dose_per_frame'] > 0.3) & (self.df['desired_exp'] != 'high_dose_scan') & (self.df['desired_exp'] != 'ultra_high_dose_scan')
        
        if mask.any():
            for i in range(len(self.df)):
                if mask[i]:
                    self.logger.warning("Warning: dose/frame exceeds 0.3 MGy. Please check the exposure condition.")
                    self.logger.warning("puckid: {} pinid: {} dose/frame {} MGy".format(self.df['puckid'][i], self.df['pinid'][i], self.df['dose_per_frame'][i]))
        else:
            self.logger.info("No warning message for dose/frame check.")

        # self.df['ppf_raster']が 4.0E10 を下回る場合には警告を出す
        # "Warning: ppf_raster is less than 4.0E10. Please check the exposure condition."
        mask2 = (self.df['ppf_raster'] < 4.0E10)
        if mask2.any():
            for i in range(len(self.df)):
                if mask2[i]:
                    self.logger.warning("Warning: ppf_raster is less than 4.0E10. Please check the exposure condition.")
                    self.logger.warning("puckid: {} pinid: {} ppf_raster {}".format(self.df['puckid'][i], self.df['pinid'][i], self.df['ppf_raster'][i]))
        else:
            self.logger.info("No warning message for photons/frame check.")

    def sizeWarning(self):
        # self.df['mode']が 'multi' である場合、self.df['max_crystal_size']と self.df['beam_size']を比較して、
        # self.df['hbeam']と self.df['vbeam']を比較して大きい方を tmp_beamsize とする
        # self.df['max_crystal_size']が tmp_beamsize の2倍よりも大きい場合には警告を出す
        # "Warning: max_crystal_size is larger than 2 times of beam_size. Please check the exposure condition."
        mask = (self.df['mode'] == 'multi')
        if mask.any():
            for i in range(len(self.df)):
                if mask[i]:
                    tmp_beamsize = max(self.df['ds_hbeam'][i], self.df['ds_vbeam'][i])
                    if self.df['max_crystal_size'][i] > tmp_beamsize * 2.0:
                        self.logger.warning("Warning: max_crystal_size is larger than 2 times of the larger dimension of the beam size.")
                        self.logger.warning("Please re-confirm the conditions of 'multi' mode.")
                        self.logger.warning("puckid: {} pinid: {} max_crystal_size:{:.1f}um beam size:{}um".format(self.df['puckid'][i], self.df['pinid'][i], self.df['max_crystal_size'][i], tmp_beamsize))
        
    # self.dfに格納されているから、データexp_rasterに変更を加える必要がある場合には変更を加える
    def modifyExposureConditions(self):
        # self.df['att_raster']　が 100.0 を超えている場合
        # さらにself.df['exp_raster']を長くして、その分 self.df['att_raster'] = 100.0とする
        # その場合、self.df['hebi_att']も変更する必要がある
        # extend_ratio = self.df['att_raster'] / 100.0
        # new_exp_raster = self.df['exp_raster'] * extend_ratio
        # この数値を self.df['exp_raster'] に代入する
        mask = (self.df['att_raster'] > 100.0)
        self.df.loc[mask, 'exp_raster'] = self.df['exp_raster'] * self.df['att_raster'] / 100.0
        self.df.loc[mask, 'att_raster'] = 100.0
        self.df.loc[mask, 'hebi_att'] = 100.0
        # self.loggerにWarningを出す
        # mask が Trueの場合のみ、Warningを出す
        # そのとき 'puckid', 'pinid' を出力する
        # さらに exp_raster の数値も同時に出力する
        if mask.any():
            self.logger.warning("att_raster > 100.0 -> 'exp_raster' was modified")
            self.logger.warning("Please carefully check 'beam size' and 'desired experimental mode'")
            self.logger.warning(self.df.loc[mask, ['puckid', 'pinid', 'sample_name', 'exp_raster']])

        # self.dfに含まれる露光条件で
        # ppf_rasterが 4.0E10 を下回る場合
        # dose_per_frameが 0.3 MGy を超える場合 にWarning messageを出す
        # loggingに記録する
        self.makeExpWarning()

    def makeCSV(self, zoo_csv=None):
        if not zoo_csv:
            return None

        ctime=datetime.datetime.now()
        time_str = datetime.datetime.strftime(ctime, '%y%m%d%H%M%S')
        db_fname = "zoo_%s.db"%time_str

        import ESA
        esa = ESA.ESA(db_fname)
        if os.path.exists(self.csvout):
            esa.makeTable(self.csvout, force_to_make=True)

        return

    def read_new(self):
        # pandasを利用して.xlsxファイルを読み込む
        # tabの名前を指定して読む "ZOOPREP_YYMMDD_NAME_BLNAME_v2"
        # pandasを利用してエクセルのタブのリストを取得して表示する
        #print(pd.ExcelFile(self.fname).sheet_names)

        # エクセルのタブ名が "ZOOPREP_YYMMDD_NAME_BLNAME_v2" であるタブを読み込む
        # Index(['PuckID', 'PinID', 'SampleName', 'Objective', 'Mode', 'HA',
        # 'Wavelength [Å]', 'Hor. scan length [µm]', 'Resolution limit [Å]',
        # 'Beam size [um]\n(H x V)', 'Crystal size [µm]',
        # '# of crystals\n / Loop', 'Total osc \n/ Crystal', 'Osc. Width',
        # 'LN2\nSplash', 'PIN Type', 'Zoom\nCapture', 'Unnamed: 17',
        # 'Confirmation required'],
        # column名を指定する
        columns = ['puckid', 'pinid', 'sample_name', 'desired_exp', 'mode', 'anomalous_flag', \
            'wavelength', 'loopsize', 'resolution_limit', 'beamsize', 'max_crystal_size', 'maxhits', 'total_osc', 'osc_width', \
                'ln2_flag', 'pin_flag', 'zoomcap_flag', 'what', 'confirmation_require']

        # データは4行目から
        self.df = pd.read_excel(self.fname, sheet_name="ZOOPREP_YYMMDD_NAME_BLNAME_v2", header=2)
        # 列名を指定する
        self.df.columns = columns
        self.isPrep = True
        
    def calcDist(self, wavelength, resolution_limit):
        # beamline.ini　の experiment セクション　から min_camera_dim を読んで min_dimに代入
        # wavelength と resolution_limit から camera_len を計算する
        # camera_len が min_dim 以下なら min_dim を返す
        # camera_len が min_dim より大きいなら camera_len を返す
        min_camera_len = self.config.getfloat("detector", "min_camera_len")
        min_camera_dim = self.config.getfloat("detector", "min_camera_dim")
        theta = numpy.arcsin(wavelength / 2.0 / resolution_limit)
        bunbo = 2.0 * numpy.tan(2.0 * theta)
        camera_len = min_camera_dim / bunbo
        # camera_len が　min_camera_len 以下なら min_camera_len を返す
        if camera_len < min_camera_len:
            camera_len = min_camera_len

        # 小数点第一位に丸める camera_len
        camera_len = round(camera_len, 1)

        return camera_len

    def checkBeamsize(self, beamsize_char):
        cols = beamsize_char.split('x')
        if len(cols) > 1:
            hbeam = float(cols[0])
            vbeam = float(cols[1])
            return hbeam, vbeam

    # データフレームの分解能限界からカメラ長を計算して格納する
    def addDistance(self):
        # dataframe中の 'wavelength', 'resolution_limit'を利用してカメラ長を計算する
        # 各数値は、self.df['wavelength'], self.df['resolution_limit']で取得できるが文字列の可能性があるので数値にしてから利用する
        self.df['wavelength'] = self.df['wavelength'].astype(float)
        self.df['resolution_limit'] = self.df['resolution_limit'].astype(float)
        self.df['dist_ds'] = self.df.apply(lambda x: self.calcDist(x['wavelength'], x['resolution_limit']), axis=1)
        # resolution limit は beamline.iniから読み込む
        # self.config : section=experiment, option=resol_raster
        self.df['dist_raster'] = self.df.apply(lambda x: self.calcDist(x['wavelength'], self.config.getfloat("experiment", "resol_raster")), axis=1)

    def makeCondList(self):
        # DataFrameとしてExcelファイルを読み込む　 →　self.df
        self.read_new()
        # 液体窒素ぶっ掛けの情報を管理してCSV用の情報へ変換
        self.checkLN2flag()
        # カメラのZoomに関する情報を管理してCSV用の情報へ変換
        self.checkZoomFlag()
        # カメラ長に関する情報をCSV用の情報へ変換
        self.addDistance()
        # ピンの温めに関する情報を管理してCSV用の情報へ変換
        self.checkPinFlag()
        self.splitBeamsizeInfo()
        # beam sizeから beamsize.config → Fluxを読み込んでDataFrameに入れる
        self.fillFlux()
        # default parameterをDataFrameに入れていく（beamline.iniからほとんど読み込んでいる）
        self.setDefaults()
        # raster scanの露光条件の決定
        self.defineScanCondition()
        # 露光条件について検討。transmission > 100% のときに露光時間とtransmissionを編集する
        self.modifyExposureConditions()
        # 結晶サイズについてのWarning（今は multi だけ)
        self.sizeWarning()

        # self.dfの内容をCSVファイルに書き出す
        # column の並び順は以下のように変更する
        # root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,raster_hbeam,att_raster,
        # hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,
        # exp_ds,dist_ds,dose_ds,offset_angle,reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,
        # hel_full_osc,hel_part_osc, raster_roi, ln2_flag, cover_scan_flag, zoomcap_flag, warm_time 
        # その他の値は self.df から読み込む
        self.columns = ['root_dir', 'p_index', 'mode', 'puckid', 'pinid', 'sample_name', 'wavelength', 'raster_vbeam', 'raster_hbeam', 'att_raster', \
                        'hebi_att', 'exp_raster', 'dist_raster', 'loopsize', 'score_min', 'score_max', 'maxhits', 'total_osc', 'osc_width', 'ds_vbeam', 'ds_hbeam', \
                        'exp_ds', 'dist_ds', 'dose_ds', 'offset_angle', 'reduced_fact', 'ntimes', 'meas_name', 'cry_min_size_um', 'cry_max_size_um', \
                        'hel_full_osc', 'hel_part_osc', 'raster_roi', 'ln2_flag', 'cover_scan_flag', 'zoomcap_flag', 'warm_time']       

        # float については小数点以下第一位までに丸める
        # floatのフォーマットを指定
        float_format = '%.2f'
        # to_csv()メソッドでファイルに書き出す際にfloatのフォーマットを指定して書き出す
        zoo_csv_name = f"{self.csv_prefix}.csv"
        self.df.to_csv(zoo_csv_name, columns=self.columns, index=False, float_format=float_format)
        
        #line_str = "%s,%d,%s,%s,%s,%s," % (root_dir,p_index,mode,puckid,pinid,sample_name)
        #line_str += "%7.5f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%f,%f,%f,0.02,%f,%f,%f,%f,%f,%s,%f,%f,%f," \
        #               "%f,%d,%d,%d,%d,%d" % \ (wavelength,vbeam,hbeam,att_raster,hebi_att,exp_raster,dist_raster, \
        #       loop_size,score_min,score_max,n_crystals,total_osc,osc_width,vbeam,hbeam,distance,dose_ds,0.0,1.0,1.0, \
        #        desired_exp,cry_min_size,cry_max_size,60,40,raster_roi,ln2_flag,cover_flag,zoom_flag,warm_time) 
    
    def makeCondList_obsoleted(self):
        if self.isGot:
            return
        if self.fname.count("_zoo.csv"):
            self.csvout = self.fname
            return
        if not self.isPrep:
            self.exRealList()

        self.conds  = []
        p_index = 0

        keys = "root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,raster_hbeam,att_raster,\
        hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,\
        exp_ds,dist_ds,dose_ds,offset_angle,reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,\
        hel_full_osc,hel_part_osc".split(",")

        pin_param = []
        line_strs = []
        line_strs.append("root_dir,p_index,mode,puckid,pinid,sample_name,wavelength,raster_vbeam,"
                         "raster_hbeam,att_raster,hebi_att,exp_raster,dist_raster,loopsize,score_min,score_max,"
                         "maxhits,total_osc,osc_width,ds_vbeam,ds_hbeam,exp_ds,dist_ds,dose_ds,offset_angle,"
                         "reduced_fact,ntimes,meas_name,cry_min_size_um,cry_max_size_um,hel_full_osc,hel_part_osc,"
                         "raster_roi,ln2_flag,cover_scan_flag,zoomcap_flag,warm_time")

        for cols in self.contents:
            puckid              = cols[0].replace("-", "")
            pinid               = cols[1]
            mode                = cols[4]
            print((cols[6]))
            wavelength          = float(cols[6])
            loop_size           = float(cols[7])
            # resolution_limitが10.0より大きい場合は1.5に設定するという意味だそうな
            resolution_limit    = float(cols[8]) if float(cols[8]) <= 10.0 else 1.5
            max_crystal_size    = float(cols[10])
            beamsize            = cols[9]
            # sample名に()が入っている場合は-に置換する
            sample_name         = cols[2].replace("(", "-").replace(")", "-")
            desired_exp         = cols[3]
            n_crystals          = int(cols[11])
            total_osc           = float(cols[12])
            osc_width           = float(cols[13])
            anomalous_flag      = cols[5]
            # LN2 flagについては、"no"の場合は0、それ以外は1とする
            ln2_flag            = 0 if cols[14].lower == "no" else 1
            pin_flag            = cols[15]
            # Zoom flag については、"no"の場合は0、それ以外は1とする
            zoom_flag           = 0 if cols[16].lower == "no" else 1

            if pin_flag.lower() == "spine":
                warm_time = 10
            elif pin_flag.lower() == "als + ssrl":
                warm_time = 20
            elif pin_flag.lower() == "copper": 
                warm_time = 60
            elif pin_flag.lower() == "no-wait":
                warm_time = 0
            else:
                warm_time = 30

            # カメラ長を計算する 小数点以下1位に丸める
            distance = math.floor(self.calcDist(wavelength, resolution_limit)*10)/10 # 2020/11/24 modified by HM 
            hbeam, vbeam = self.checkBeamsize(beamsize)

            # Reading flux value
            flux = self.bsconf.getFluxAtWavelength(hbeam, vbeam, wavelength)
            print("Flux value is read from beamsize.conf: %5.2e\n" % flux)

            # Dose estimation for raster scan
            score_min, score_max, raster_dose, dose_ds, raster_roi, exp_raster, att_raster, hebi_att, cover_flag = self.getParams(desired_exp, mode)
            # Calculate 'att_raster', 'exp_raster'
            att_raster, mod_exp_raster = self.defineScanCondition(desired_exp, wavelength, hbeam, vbeam, flux, exp_raster)

            exp_raster = round(mod_exp_raster, 3)
            hebi_att = round(att_raster,3)
            att_raster = hebi_att

            cry_min_size = max_crystal_size
            cry_max_size = max_crystal_size
            # Special code
            if mode == "multi" and cry_max_size > 100.0:
                cry_min_size = 25.0
                cry_max_size = 25.0

            self.conds.append((puckid, pinid, mode, wavelength, loop_size, resolution_limit, max_crystal_size, beamsize, 
                sample_name, desired_exp, n_crystals, total_osc, osc_width, anomalous_flag))

            if self.beamline.lower() == "bl32xu":
                dist_raster = 200.0
            elif self.beamline.lower() == "bl45xu":
#                dist_raster = 500.0
                dist_raster = math.floor(self.calcDist(wavelength, 2.53)/10)*10

            line_str = "%s,%d,%s,%s,%s,%s," % (root_dir,p_index,mode,puckid,pinid,sample_name)
            line_str += "%7.5f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%f,%f,%f,0.02,%f,%f,%f,%f,%f,%s,%f,%f,%f," \
                        "%f,%d,%d,%d,%d,%d" % \
                (wavelength,vbeam,hbeam,att_raster,hebi_att,exp_raster,dist_raster,
                loop_size,score_min,score_max,n_crystals,total_osc,osc_width,vbeam,hbeam,distance,dose_ds,0.0,1.0,1.0,
                 desired_exp,cry_min_size,cry_max_size,60,40,raster_roi,ln2_flag,cover_flag,zoom_flag,warm_time)
            line_strs.append(line_str)
            pin_param = []
            p_index += 1

        self.csvout = "%s_zoo.csv"%self.basename[0]
        fin = open(self.csvout, "w")
        for line in line_strs:
            fin.write("%s\n" % line)
        fin.close()

        self.isGot = True
        return pin_param

if __name__ == "__main__":
    root_dir = os.getcwd()
    u2db = UserESA(sys.argv[1], root_dir, beamline="BL32XU")

    u2db.makeCondList()
    # u2db.df['ppf_raster']を 指数表記で出力
    pd.options.display.float_format = '{:.2e}'.format
    #print(u2db.df['dist_raster'])
    #print(u2db.df['dist_ds'])