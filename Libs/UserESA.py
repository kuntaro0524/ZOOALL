#coding: UTF-8
"""
(C) RIKEN/JASRI 2020 :
Author: Kunio Hirata
ESA -> the main function : the class to read & write zoo database file
This code is originally written by K.Hirata and modified by N.Mizuno.
NM added function to read xlsx file directly and output zoo.db by using ESA class.

The second author: Nobuhiro Mizuno
"""
import sys, os, math, numpy, csv, re, datetime, xlrd, codecs
import configparser
import pandas as pd
import numpy as np
import KUMA
import AttFactor
# logger の設定
import logging
from configparser import ConfigParser, ExtendedInterpolation
#from dose.fields import get_dose_ds, get_dist_ds

class DoseDistanceHandler:
    def __init__(self, logger, debug: bool = False):
        self.logger = logger
        self.debug = debug

    def validate_dose_dist(self, cond):
        mode = str(cond.get("mode", "")).strip().lower()

        raw_dose = cond.get("dose_list", "")
        raw_dist = cond.get("dist_list", "")

        has_dose = (not pd.isna(raw_dose)) and str(raw_dose).strip() != ""
        has_dist = (not pd.isna(raw_dist)) and str(raw_dist).strip() != ""

        # dist_list 単独は禁止
        if (not has_dose) and has_dist:
            raise ValueError(
                "[UserESA] dist_list cannot be specified without dose_list. "
                f"dose_list={raw_dose!r}, dist_list={raw_dist!r}"
            )

        dose_vals = self._parse_series_like(raw_dose) if has_dose else None
        dist_vals = self._parse_series_like(raw_dist) if has_dist else None

        # 両方あるなら長さ一致必須
        if dose_vals is not None and dist_vals is not None:
            if len(dose_vals) != len(dist_vals):
                raise ValueError(
                    "[UserESA] dose_list and dist_list must have the same length. "
                    f"dose_list={dose_vals}, dist_list={dist_vals}"
                )

        # mode 制約
        if mode in ("multi", "mixed", "ssrox"):
            n_dose = len(dose_vals) if dose_vals is not None else 0
            n_dist = len(dist_vals) if dist_vals is not None else 0
            if n_dose > 1 or n_dist > 1:
                raise ValueError(
                    f"[UserESA] mode='{mode}' does not allow multiple values. "
                    f"dose_list={dose_vals}, dist_list={dist_vals}"
                )
        elif mode in ("single", "helical", "quick", "screening","sponge"):
            pass
        else:
            raise ValueError(f"[UserESA] Unknown mode='{mode}' in condition.")

    def check_dose_list(self, df):
        self.logger.info(f"columns={df.columns.tolist()}")
        work_df = df.copy()

        for col in ("dose_list", "dist_list"):
            if col not in work_df.columns:
                work_df[col] = ""

        normalized_rows = []
        for _, row in work_df.iterrows():
            # 先に1行単位の検証
            self.validate_dose_dist(row)

            raw_dose = row.get("dose_list", "")
            raw_dist = row.get("dist_list", "")

            has_dose = (not pd.isna(raw_dose)) and str(raw_dose).strip() != ""
            has_dist = (not pd.isna(raw_dist)) and str(raw_dist).strip() != ""

            dose_vals = self._parse_series_like(raw_dose) if has_dose else None
            dist_vals = self._parse_series_like(raw_dist) if has_dist else None

            out_dose_list = self._serialize_list_for_csv(dose_vals) if dose_vals is not None else ""
            out_dist_list = self._serialize_list_for_csv(dist_vals) if dist_vals is not None else ""

            row_out = row.copy()
            row_out["dose_list"] = out_dose_list
            row_out["dist_list"] = out_dist_list
            normalized_rows.append(row_out)

        return pd.DataFrame(normalized_rows)

    def _parse_series_like(self, text):
        if text is None or (isinstance(text, float) and pd.isna(text)):
            return None

        s = str(text).strip()
        if not s:
            return None

        trans = str.maketrans({
            '（': '(', '）': ')',
            '［': '[', '］': ']',
            '｛': '{', '｝': '}',
            '，': ',',
            '＋': '+',
            '；': ';'
        })
        s = s.translate(trans).strip()

        if (s.startswith('{') and s.endswith('}')) or \
           (s.startswith('[') and s.endswith(']')) or \
           (s.startswith('(') and s.endswith(')')):
            s = s[1:-1].strip()

        if s == "":
            return []

        parts = [p.strip() for p in re.split(r'[,;+]', s) if p.strip()]
        vals = []
        for p in parts:
            if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?', p):
                raise ValueError(f"[UserESA] Bad numeric token in dose/dist list: {p!r}")
            vals.append(float(p))
        return vals

    def _serialize_list_for_csv(self, vals):
        if vals is None or len(vals) == 0:
            return ""
        if len(vals) == 1:
            return f"{vals[0]:g}"
        return "[" + ", ".join(f"{v:g}" for v in vals) + "]"
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

        self.debug=True
        self.isDoseError = False

        # configure file から情報を読む: beamlineの名前
        self.beamline = self.config.get("beamline", "beamline")
        import BeamsizeConfig
        self.bsconf = BeamsizeConfig.BeamsizeConfig()

        # CSV prefix
        self.csv_prefix = self.fname.replace(".xlsx","")

        # logger の設定
        self.logger = logging.getLogger("ZOO")
        # output log string with level 'info'
        self.logger.setLevel(logging.INFO)
        # levelがwarningのときには標準出力とファイル両方に出力する
        
        # create file handler which logs even debug messages
        self.logger_fh = logging.FileHandler('useresa.log')
        self.logger_fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        self.logger_ch = logging.StreamHandler()
        self.logger_ch.setLevel(logging.WARNING)
        # create formatter and add it to the handlers
        self.logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # set formatter to handlers
        self.logger_fh.setFormatter(self.logger_formatter)
        self.logger_ch.setFormatter(self.logger_formatter)
        # add the handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(self.logger_fh)
            self.logger.addHandler(self.logger_ch)

        self.root_dir = root_dir
        self.dose_distance_handler = DoseDistanceHandler(self.logger, debug=self.debug)

    # ChatGPT 2024-10-07 
    # dose_ds, dist_ds は mode = 'multi', 'mixed' は複数不可
        # spec 5.1.7:
    # multi / mixed では dose_list, dist_list の複数要素指定を禁止する
    def validateDoseDist(self, cond):
        """mode に応じて dose_list / dist_list の形式をチェック"""
        return self.dose_distance_handler.validate_dose_dist(cond)

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

        if "score_max" not in self.df.columns:
            self.df["score_max"] = self.config.getfloat("experiment", "score_max")
        else:
            self.df["score_max"] = self.df["score_max"].fillna(
                self.config.getfloat("experiment", "score_max")
            )
        self.df["raster_dose"] = self.config.getfloat("experiment", "raster_dose")
        self.df["dose_ds"] = self.config.getfloat("experiment", "dose_ds")
        self.df["raster_roi"] = self.config.getint("experiment", "raster_roi")
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
        self.df.loc[self.df['desired_exp'] == "scan_only", 'score_max'] = 9999
        self.df.loc[self.df['desired_exp'] == "scan_only", 'raster_dose'] = 0.3
        self.df.loc[self.df['desired_exp'] == "scan_only", 'dose_ds'] = 0.0
        self.df.loc[self.df['desired_exp'] == "scan_only", 'cover_scan_flag'] = 0

        # 2) desired_exp が "normal" のとき
        # mode が "helical" または "mixed" の場合には、score_max を 9999 とする
        self.df.loc[
            (self.df['desired_exp'] == "normal") &
            (self.df['mode'].astype(str).str.strip().str.lower().isin(["helical", "mixed"])),
            'score_max'
        ] = 9999

        # 3) desired_exp が "ultra_high_dose_scan" のとき
        # dose_dsは固定値ではなく defineScanCondition() 内で dose_per_frame をもとに計算して設定することとする
        pass
        # 4) desired_exp が "phasing" のとき
        # dose_dsの最終値は defineScanCondition() 内で dose_per_frame をもとに計算して設定することとする
        pass

    # modeごとにスキャン回数が異なるのでそれを考慮したDoseにしたときって話
    # 正直、ここまで厳密ではなくてよいのだが
    def getScanDoseRepeat(self, mode):
        mode_norm = str(mode).strip().lower()

        if mode_norm == "single":
            return 2.0
        elif mode_norm == "multi":
            return 1.0
        elif mode_norm == "helical":
            return 2.0
        elif mode_norm in ("mixed", "ssrox", "quick", "screening","sponge"):
            return 1.0
        else:
            raise ValueError(f"[UserESA] Unknown mode for scan dose: {mode}")

    def getMaxRasterFrequency(self):
        """
        raster detector frequency の最大値 [Hz] を返す。
        beamline.ini に max_raster_frequency があればそれを使い、
        なければ仕様上の既定値 220 Hz を使う。
        """
        return int(self.config.getfloat("experiment", "max_raster_frequency", fallback=220.0))

    def isValidRasterFrequency(self, freq):
        """
        仕様 5.9.2:
        exp_raster = 1 / f が小数点以下4桁までで正確に表現可能な
        raster detector frequency のみ許可する。
        """
        freq = int(freq)

        if freq < 1:
            return False

        exp_raster = 1.0 / float(freq)

        # 小数点以下4桁で丸めても値が変わらないものだけ許可
        return abs(exp_raster - round(exp_raster, 4)) < 1.0e-12

    def getAllowedRasterFrequencies(self):
        """
        使用可能な raster detector frequency の候補を返す。
        
        条件:
        - 1 <= f <= max_raster_frequency
        - f は整数
        - exp_raster = 1/f が小数点以下4桁で正確に表現可能
        """
        max_freq = self.getMaxRasterFrequency()

        allowed = [
            f for f in range(1, max_freq + 1)
            if self.isValidRasterFrequency(f)
        ]

        if len(allowed) == 0:
            raise ValueError(
                "[UserESA] No valid raster frequency candidates were found."
            )

        return allowed

    def selectRasterExposureByFrequency(self, required_exp_raster):
        """
        仕様 5.9.2:
        exp_raster = 1 / f
        
        f は以下を満たす:
        - 整数 Hz
        - 1 <= f <= max_raster_frequency
        - 1/f が小数点以下4桁で正確に表現可能

        required_exp_raster 以上となる候補のうち、
        最短の exp_raster を返す。
        """
        required_exp_raster = float(required_exp_raster)

        allowed_freqs = self.getAllowedRasterFrequencies()

        candidates = []
        for f in allowed_freqs:
            exp_raster = 1.0 / float(f)

            if exp_raster + 1.0e-12 >= required_exp_raster:
                candidates.append((exp_raster, f))

        if len(candidates) == 0:
            max_exp = max(1.0 / float(f) for f in allowed_freqs)

            raise ValueError(
                "[UserESA] required_exp_raster is too long for finite-decimal "
                "integer-frequency control: "
                f"required_exp_raster={required_exp_raster:.6f} s, "
                f"allowed maximum exposure is {max_exp:.6f} s"
            )

        exp_raster, freq = min(candidates, key=lambda x: x[0])

        return exp_raster, freq

    def getAllowedRasterExposureCandidates(self, required_exp_raster=0.0):
        """
        5.9.2 の条件を満たす exp_raster 候補を短い順に返す。
        """
        required_exp_raster = float(required_exp_raster)

        candidates = []
        for f in self.getAllowedRasterFrequencies():
            exp_raster = 1.0 / float(f)
            if exp_raster + 1.0e-12 >= required_exp_raster:
                candidates.append((exp_raster, f))

        candidates.sort(key=lambda x: x[0])

        if len(candidates) == 0:
            raise ValueError(
                "[UserESA] No raster exposure candidate satisfies required_exp_raster: "
                f"{required_exp_raster:.6f} s"
            )

        return candidates

    def getThinnestAttenuatorThickness(self):
        """
        最薄 attenuator thickness [um] を beamline.ini から読む。
        AttFactor.readAttConfig() は使わない。
        """
        return self.config.getfloat(
            "experiment",
            "thinnest_att_thick"
        )

    def calcThinnestAttenuatorTransmission(self, wavelength):
        """
        beamline.ini の thinnest_att_thick [um] と wavelength [Å] から、
        最薄 attenuator の transmission を計算する。
        戻り値は 0.0〜1.0。
        """
        thinnest_att_thick = self.getThinnestAttenuatorThickness()

        attfac = AttFactor.AttFactor()
        transmission = attfac.calcAttFac(
            float(wavelength),
            thinnest_att_thick,
            material="Al"
        )

        if transmission <= 0.0 or transmission > 1.0:
            raise ValueError(
                "[UserESA] Invalid thinnest attenuator transmission: "
                f"wavelength={wavelength}, "
                f"thinnest_att_thick={thinnest_att_thick}, "
                f"transmission={transmission}"
            )

        return transmission

    def isAttenuationHardwareAllowed(self, wavelength, att_raster):
        """
        att_raster [%] が attenuator hardware constraint を満たすか判定する。

        許容:
        - att_raster == 100%
        - att_raster <= 最薄 attenuator transmission [%]

        禁止:
        - thinnest_transmission*100 < att_raster < 100
        """
        att_raster = float(att_raster)

        if att_raster > 100.0 + 1.0e-6:
            return False

        if abs(att_raster - 100.0) <= 1.0e-6:
            return True

        transmission = att_raster / 100.0
        thinnest_transmission = self.calcThinnestAttenuatorTransmission(wavelength)

        return transmission <= thinnest_transmission + 1.0e-12

    # ビームライン、実験モードと結晶のタイプから実験パラメータを取得する
    # 2023/05/09 type_crystal は使わない
    def getParams(self, desired_exp_string, mode):
        # dose_ds はここでは確定しない。
        # 最終的な dose_ds は defineScanCondition() で
        # dose_ds = total_dose - dose_scan_total
        # により決定する。
        # phasing と ultra_high_dose_scan の dose_ds は beamline.ini から読む
        desired_exp_string = str(desired_exp_string).strip().lower()
        mode = str(mode).strip().lower()

        if mode not in ("single", "multi", "helical", "mixed", "ssrox", "quick", "screening","sponge"):
            raise ValueError(f"[UserESA] Unknown mode: {mode}")

        # DEFAULT PARAMETER
        # beamline.ini から読む
        #self.beamline = self.config.get("beamline", "beamline")
        score_min   = self.config.getfloat("experiment", "score_min")
        score_max   = self.config.getfloat("experiment", "score_max")
        raster_dose = self.config.getfloat("experiment", "raster_dose")
        dose_ds     = self.config.getfloat("experiment", "dose_ds")
        raster_roi  = self.config.getint("experiment", "raster_roi")
        exp_raster = self.config.getfloat("experiment", "exp_raster")
        att_raster  = self.config.getfloat("experiment", "att_raster")
        hebi_att    = self.config.getfloat("experiment", "hebi_att")
        cover_flag  = self.config.getint("experiment", "cover_flag")
        # dose_ds はここでは確定しない。
        # 最終的な dose_ds は defineScanCondition() で
        # dose_ds = total_dose - dose_scan_total
        # により決定する。

        # PARAMTER CONDITION
        # raster_dose は初期補填値であり、最終的な raster scan 条件は
        # defineScanCondition() において desired_exp / dose_list / scan speed /
        # attenuator constraint を考慮して再計算される。
        # spongeは ROI 前提であるため、raster_roi は 1 とする
        self.param = {
            "scan_only":{
                "single":   [9999, 9999, raster_dose, None, 0, exp_raster, att_raster, hebi_att, 0],
                "helical":  [9999, 9999, raster_dose, None, 0, exp_raster, att_raster, hebi_att, 0],
                "multi":    [9999, 9999, raster_dose, None, 0, exp_raster, att_raster, hebi_att, 0],
                "mixed":    [9999, 9999, raster_dose, None, 0, exp_raster, att_raster, hebi_att, 0],
                "sponge":   [9999, 9999, raster_dose, None, 1, exp_raster, att_raster, hebi_att, 0],
            },

            "normal":{
                "single":   [score_min, score_max, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999,      raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, 9999,      raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "sponge":   [score_min, score_max, raster_dose, None, 1,           exp_raster, att_raster, hebi_att, cover_flag],
            },

            "high_dose_scan":{
                "single":   [score_min, 9999, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, 9999, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, 9999, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "sponge":   [score_min, score_max, raster_dose, None, 1, exp_raster, att_raster, hebi_att, cover_flag],
            },

            "ultra_high_dose_scan":{
                "single":   [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "helical":  [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "multi":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "mixed":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "sponge":   [score_min, score_max, raster_dose, None, 1, exp_raster, 100, 100, cover_flag],
            },

            "phasing":{
                "single":   [score_min, score_max, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "helical":  [score_min, 9999,      raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "multi":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "mixed":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, att_raster, hebi_att, cover_flag],
                "sponge":   [score_min, score_max, raster_dose, None, 1, exp_raster, att_raster, hebi_att, cover_flag],
            },

            "rapid":{
                "single":   [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "helical":  [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "multi":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "mixed":    [score_min, score_max, raster_dose, None, raster_roi, exp_raster, 100, 100, cover_flag],
                "sponge":   [score_min, score_max, raster_dose, None, 1, exp_raster, 100, 100, cover_flag],
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
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('NO', 0)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('No', 0)
        self.df['ln2_flag'] = self.df['ln2_flag'].replace('no', 0)
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
        pin_flag_norm = self.df['pin_flag'].astype(str).str.strip().str.lower()
        self.df.loc[pin_flag_norm == 'spine', 'warm_time'] = 10.0
        self.df.loc[pin_flag_norm == 'als + ssrl', 'warm_time'] = 20.0
        self.df.loc[pin_flag_norm == 'copper', 'warm_time'] = 60.0
        self.df.loc[pin_flag_norm == 'no-wait', 'warm_time'] = 0.0

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

    def defineScanCondition(self):
        """
        raster scan 条件を決定する。

        仕様:
        - exp_raster は 5.9.2 の有限小数・整数Hz制約を満たす。
        - exp_raster は 5.9.3 の attenuator hardware constraint も満たす。
        - att_raster は透過率 [%] として扱う。
        - 最薄 attenuator 厚みは beamline.ini [experiment] thinnest_att_thick [um] から読む。
        """
        kuma = KUMA.KUMA()

        def _has_value(v):
            return (not pd.isna(v)) and str(v).strip() != ""

        def _base_dose(row, exp_raster):
            return kuma.getDose(
                row["ds_hbeam"],
                row["ds_vbeam"],
                row["flux"],
                row["wavelength"],
                exp_raster
            )

        if "dose_list" not in self.df.columns:
            self.df["dose_list"] = ""
        if "dist_list" not in self.df.columns:
            self.df["dist_list"] = ""

        photons_per_image_normal = 4.0E10
        target_scan_dose_ext = 0.001  # MGy/frame

        max_scan_speed = self.config.getfloat("experiment", "max_hori_scan_speed")
        if max_scan_speed <= 0.0:
            raise ValueError("[UserESA] max_hori_scan_speed must be positive.")

        self.df["ppf_raster"] = np.nan
        self.df["dose_per_frame"] = np.nan

        for i, row in self.df.iterrows():
            desired_exp = str(row["desired_exp"]).strip().lower()
            mode = str(row["mode"]).strip().lower()
            has_dose_list = _has_value(row.get("dose_list", ""))

            flux = float(row["flux"])
            wavelength = float(row["wavelength"])
            raster_hbeam = float(row["raster_hbeam"])

            if flux <= 0.0:
                raise ValueError(f"[UserESA] flux must be positive. idx={i}, flux={flux}")

            required_exp_by_speed = raster_hbeam / max_scan_speed

            if has_dose_list:
                dose_per_sec_full_att = _base_dose(row, 1.0)
                if dose_per_sec_full_att <= 0.0:
                    raise ValueError(
                        f"[UserESA] base dose per second must be positive. idx={i}, "
                        f"dose_per_sec_full_att={dose_per_sec_full_att}"
                    )

                required_exp_by_signal = target_scan_dose_ext / dose_per_sec_full_att
                target_type = "dose_list"
                target_ppf = None
                target_dose = target_scan_dose_ext

            else:
                if desired_exp in ("normal", "scan_only", "phasing", "rapid"):
                    factor = 1.0
                elif desired_exp == "high_dose_scan":
                    factor = 1.5
                elif desired_exp == "ultra_high_dose_scan":
                    factor = 3.0
                else:
                    raise ValueError(
                        f"[UserESA] Unknown desired_exp='{desired_exp}' in defineScanCondition()."
                    )

                target_ppf = photons_per_image_normal * factor
                required_exp_by_signal = target_ppf / flux
                target_type = "photons"
                target_dose = None

            required_exp_raster = max(required_exp_by_speed, required_exp_by_signal)

            selected = None

            for exp_raster, freq in self.getAllowedRasterExposureCandidates(required_exp_raster):
                base_dose_full_att = _base_dose(row, exp_raster)

                if target_type == "dose_list":
                    att_raster = target_dose / base_dose_full_att * 100.0
                    ppf_raster = flux * exp_raster * att_raster / 100.0
                    dose_per_frame = target_dose
                else:
                    att_raster = target_ppf / (flux * exp_raster) * 100.0
                    ppf_raster = target_ppf
                    dose_per_frame = base_dose_full_att * att_raster / 100.0

                if att_raster > 100.0 + 1.0E-6:
                    continue

                att_raster = min(att_raster, 100.0)

                if self.isAttenuationHardwareAllowed(wavelength, att_raster):
                    selected = {
                        "exp_raster": exp_raster,
                        "freq": freq,
                        "att_raster": att_raster,
                        "ppf_raster": ppf_raster,
                        "dose_per_frame": dose_per_frame,
                    }
                    break

            if selected is None:
                thinnest_att_thick = self.getThinnestAttenuatorThickness()
                thinnest_trans = self.calcThinnestAttenuatorTransmission(wavelength)

                raise ValueError(
                    "[UserESA] No valid raster exposure satisfies attenuator hardware constraint. "
                    f"idx={i}, puckid={row.get('puckid', '')}, pinid={row.get('pinid', '')}, "
                    f"desired_exp={desired_exp}, mode={mode}, "
                    f"required_exp={required_exp_raster:.6f}, "
                    f"wavelength={wavelength:.6f}, "
                    f"thinnest_att_thick={thinnest_att_thick:.3f} um, "
                    f"thinnest_transmission={thinnest_trans:.6f}"
                )

            exp_raster = selected["exp_raster"]
            freq = selected["freq"]
            att_raster = selected["att_raster"]
            ppf_raster = selected["ppf_raster"]
            dose_per_frame = selected["dose_per_frame"]

            self.df.at[i, "exp_raster"] = exp_raster
            self.df.at[i, "att_raster"] = att_raster
            self.df.at[i, "hebi_att"] = att_raster
            self.df.at[i, "ppf_raster"] = ppf_raster
            self.df.at[i, "dose_per_frame"] = dose_per_frame

            thinnest_trans = self.calcThinnestAttenuatorTransmission(wavelength)

            self.logger.info(
                "[RasterExposure] idx=%d puck=%s pin=%s desired_exp=%s mode=%s "
                "required_speed=%.6f required_signal=%.6f selected_exp=%.6f freq=%dHz "
                "att=%.3f ppf=%.3e dose_per_frame=%.6f "
                "thinnest_trans=%.6f",
                i,
                row.get("puckid", ""),
                row.get("pinid", ""),
                desired_exp,
                mode,
                required_exp_by_speed,
                required_exp_by_signal,
                exp_raster,
                freq,
                att_raster,
                ppf_raster,
                dose_per_frame,
                thinnest_trans,
            )

        total_dose_default = self.config.getfloat("experiment", "dose_ds")
        total_dose_phasing = self.config.getfloat("experiment", "dose_ds_phasing")

        extended_mask = self.df["dose_list"].apply(_has_value)

        total_dose_series = pd.Series(total_dose_default, index=self.df.index)
        total_dose_series.loc[
            self.df["desired_exp"].astype(str).str.strip().str.lower() == "phasing"
        ] = total_dose_phasing

        scan_multiplier = self.df["mode"].apply(self.getScanDoseRepeat)
        dose_scan_total = self.df["dose_per_frame"] * scan_multiplier

        desired_norm = self.df["desired_exp"].astype(str).str.strip().str.lower()

        dose_control_mask = (
            (~extended_mask) &
            (desired_norm != "scan_only")
        )

        self.df.loc[dose_control_mask, "dose_ds"] = (
            total_dose_series.loc[dose_control_mask] -
            dose_scan_total.loc[dose_control_mask]
        )

        self.df.loc[desired_norm == "scan_only", "dose_ds"] = 0.0

        neg_mask = (self.df["dose_ds"] < 0) & (~extended_mask)
        if neg_mask.any():
            self.logger.error("dose_ds < 0 detected. total dose budget exceeded.")
            self.logger.error(
                self.df.loc[
                    neg_mask,
                    ["puckid", "pinid", "desired_exp", "dose_per_frame", "dose_ds"]
                ]
            )
            self.df.loc[neg_mask, "dose_ds"] = 0.0
            self.isDoseError = True
        else:
            self.isDoseError = False

        self.logger.info("Scan conditions estimated results")
        for i, row in self.df.iterrows():
            self.logger.info(
                "PuckID: %s PinID: %s exp_raster: %.6f att_raster: %.3f "
                "ppf_raster: %.3e dose_per_frame: %.6f dose_ds: %.6f",
                row.get("puckid", ""),
                row.get("pinid", ""),
                row.get("exp_raster", 0.0),
                row.get("att_raster", 0.0),
                row.get("ppf_raster", 0.0),
                row.get("dose_per_frame", 0.0),
                row.get("dose_ds", 0.0),
            )

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
        mask2 = (
            (self.df['ppf_raster'] < 4.0E10) &
            (self.df['dose_list'].isna() | (self.df['dose_list'].astype(str).str.strip() == ""))
        )
        if mask2.any():
            for i in range(len(self.df)):
                if mask2[i]:
                    self.logger.warning("Warning: ppf_raster is less than 4.0E10. Please check the exposure condition.")
                    self.logger.warning("puckid: {} pinid: {} ppf_raster {}".format(self.df['puckid'][i], self.df['pinid'][i], self.df['ppf_raster'][i]))
        else:
            self.logger.info("No warning message for photons/frame check")

    def sizeWarning(self):
        # self.df['mode']が 'multi' である場合、self.df['max_crystal_size']と self.df['beam_size']を比較して、
        # self.df['hbeam']と self.df['vbeam']を比較して大きい方を tmp_beamsize とする
        # self.df['max_crystal_size']が tmp_beamsize の2倍よりも大きい場合には警告を出す
        # "Warning: max_crystal_size is larger than 2 times of beam_size. Please check the exposure condition."
        mask = (self.df['mode'].astype(str).str.strip().str.lower() == 'multi')
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
        """
        defineScanCondition() で exp_raster を整数 Hz 制約に従って決定済みである。
        したがって、この関数では exp_raster を再変更しない。

        ここで exp_raster を変更すると、
        att_raster / ppf_raster / dose_per_frame / dose_ds の再計算が必要になり、
        条件不整合の原因になるため、異常検出と warning のみに限定する。
        """
        mask = self.df["att_raster"] > 100.0 + 1.0E-6

        if mask.any():
            self.logger.error(
                "att_raster > 100.0 detected after defineScanCondition(). "
                "This should not happen with integer-frequency exposure selection."
            )
            self.logger.error(
                self.df.loc[
                    mask,
                    ["puckid", "pinid", "sample_name", "exp_raster", "att_raster"]
                ]
            )
            raise RuntimeError(
                "att_raster > 100.0 detected after raster exposure optimization."
            )

        # warning 出力のみ行う
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
        # Excel 読み込み
        self.df = pd.read_excel(self.fname, sheet_name="Sheet", header=2)

        # 元の列名をログ
        raw_columns = self.df.columns.tolist()
        self.logger.info(f"Raw columns from Excel: {raw_columns}")

        # 列名正規化関数
        def _norm_col(c):
            if pd.isna(c):
                return ""
            s = str(c).strip().lower()
            s = s.replace("\n", " ")
            s = re.sub(r"\s+", " ", s)

            # よくある表記ゆれを吸収
            rename_map = {
                "puckid": "puckid",
                "puck id": "puckid",

                "pinid": "pinid",
                "pin id": "pinid",

                "samplename": "sample_name",
                "sample name": "sample_name",

                "objective": "desired_exp",
                "desired_exp": "desired_exp",
                "desired exp": "desired_exp",

                "mode": "mode",

                "ha": "anomalous_flag",
                "anomalous_flag": "anomalous_flag",

                "wavelength [å]": "wavelength",
                "wavelength": "wavelength",

                "hor. scan length [µm]": "loopsize",
                "hor. scan length [um]": "loopsize",
                "loopsize": "loopsize",

                "resolution limit [å]": "resolution_limit",
                "resolution_limit": "resolution_limit",
                "resolution limit": "resolution_limit",

                "beam size [um] (h x v)": "beamsize",
                "beam size [um](h x v)": "beamsize",
                "beam size": "beamsize",
                "beamsize": "beamsize",

                "crystal size [µm]": "max_crystal_size",
                "crystal size [um]": "max_crystal_size",
                "max_crystal_size": "max_crystal_size",
                "crystal size": "max_crystal_size",

                "# of crystals / loop": "maxhits",
                "# of crystals /loop": "maxhits",
                "maxhits": "maxhits",

                "total osc / crystal": "total_osc",
                "total osc /crystal": "total_osc",
                "total_osc": "total_osc",

                "osc. width": "osc_width",
                "osc_width": "osc_width",

                "ln2 splash": "ln2_flag",
                "ln2_flag": "ln2_flag",

                "pin type": "pin_flag",
                "pin_flag": "pin_flag",

                "zoom capture": "zoomcap_flag",
                "zoomcap_flag": "zoomcap_flag",

                "confirmation required": "confirmation_require",
                "confirmation_require": "confirmation_require",

                "dose_list": "dose_list",
                "dose list": "dose_list",

                "dist_list": "dist_list",
                "dist list": "dist_list",
            }
            return rename_map.get(s, s.replace(" ", "_"))

        # 正規化した列名に変換
        normalized_columns = [_norm_col(c) for c in self.df.columns]
        self.df.columns = normalized_columns

        self.logger.info(f"Normalized columns: {self.df.columns.tolist()}")

        # 必須列チェック
        required_columns = [
            "puckid",
            "pinid",
            "sample_name",
            "desired_exp",
            "mode",
            "wavelength",
            "loopsize",
            "resolution_limit",
            "beamsize",
            "max_crystal_size",
            "maxhits",
            "total_osc",
            "osc_width",
            "ln2_flag",
            "pin_flag",
            "zoomcap_flag",
            "confirmation_require",
        ]

        missing = [c for c in required_columns if c not in self.df.columns]
        if missing:
            raise ValueError(
                "[UserESA] Missing required columns in Excel: "
                + ", ".join(missing)
            )

        # 任意列はなければ追加
        for optional_col in ["dose_list", "dist_list"]:
            if optional_col not in self.df.columns:
                self.df[optional_col] = ""

        # データ数ログ
        self.logger.info("Number of data: %d" % len(self.df))

        # puckid がない行を削除
        self.df = self.df.dropna(subset=["puckid"])

        self.logger.info("Number of data after polishment: %d" % len(self.df))

        # dose_list / dist_list の冒頭確認
        self.logger.info(f"dose_list preview: {self.df['dose_list'].head().tolist()}")
        self.logger.info(f"dist_list preview: {self.df['dist_list'].head().tolist()}")

        self.isPrep = True

    # 高分解能データ収集用に設定したものについて以下のような仕様でチェック
    # 1) column name: "dose_list": "+"で区切られた文字列
    # 例) "0.1+1.0+1.0+1.0": [0.1, 1.0, 1.0, 1.0] 
    # というリストのこと
    # 2) column name: "dist_list": "+"で区切られた文字列
    # 例) "150.0+110.0+110.0+120.0": [150.0, 110.0, 110.0, 120.0] 
    # というリストのこと
    # この２つは必ず同じ数の要素を持つのでそうでない場合にはエラーで落ちるようにする
    def makeValueList(self, column_value):
        # column_valueが intもしくはfloatの場合には単一のリストにして返す
        if isinstance(column_value, (int, float)):
            # "[10.0]" というような文字列にして返す
            #return_value = f"[{column_value}]"
            # [columnn_value] のようなリストに変換して返す
            return_value = [column_value]
            return return_value
        else:
            # column_valueが文字列の場合には "+", ",", ";" の区切りを許容してリストに変換する
            tokens = [x.strip() for x in re.split(r'[,;+]', str(column_value)) if x.strip()]
            return list(map(float, tokens))
        
    def checkDoseList(self):
        self.df = self.dose_distance_handler.check_dose_list(self.df)

    def expandPinRange(self, pinstr):
        # pinid_str = "1-4" のような文字列を受け取る
        # 1-4 の場合は、1,2,3,4 のリストを返す
        # 1+2+3 の場合は、1,2,3 のリストを返す
        # 1;2;3 の場合は、1,2,3 のリストを返す
        # それ以外はそのままの文字列を返す
        if '-' in pinstr:
            start, end = map(int, pinstr.split('-'))
            return list(range(start, end + 1))
        elif '+' in pinstr:
            return list(map(int, pinstr.split('+')))
        elif ';' in pinstr:
            return list(map(int, pinstr.split(';')))
        else:
            return [pinstr]

    def dividePinInfo(self, pin_char):
        import re
        # ステップ1: 区切り文字で分割
        parts = re.split(r'[;+.]', pin_char)
        
        # ステップ2: 各部分を range に変換
        ranges = []
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges.append(range(start, end + 1))
            else:
                num = int(part)
                ranges.append(range(num, num + 1))
        
        # ステップ3: 必要ならすべての値をフラットなリストに
        flattened = [i for r in ranges for i in r]
        print(f"flattened={flattened}")  # [1, 2, 3, 4, 5, 10, 11, 12, 15, 16]
        return flattened

    def expandCompressedPinInfo(self):
        # The new dataframe of expanded pins
        new_df_list = []
        isFound=False
        for i, row in self.df.iterrows():
            pinid_str = str(row['pinid'])
            print(f"##### pinid_str= {pinid_str}")
            flattened_ids = self.dividePinInfo(pinid_str)
            for pinid in flattened_ids:
                new_row = row.copy()
                new_row['pinid'] = int(pinid)
                new_df_list.append(new_row)

        # 4. Create a new dataframe from the list of expanded rows
        new_df = pd.DataFrame(new_df_list)
        # 5. Reset the index of the new dataframe
        new_df.reset_index(drop=True, inplace=True)
        # 6. new_df -> self.df
        self.df = new_df

    def calcDist(self, wavelength, resolution_limit, isROI=False, roi_edge_mm=None):
        # beamline.ini　の experiment セクション　から min_camera_lim を読んで min_camera_len に代入する
        min_camera_len = self.config.getfloat("detector", "min_camera_len")

        # ROIがない場合
        if isROI == False:
            self.logger.info(f"ROI is False")
            # wavelength と resolution_limit から camera_len を計算する
            # camera_len が min_camera_len 以下なら min_camera_len を返す
            min_camera_dim = self.config.getfloat("detector", "min_camera_dim")
        else:
            self.logger.info(f"ROI is True")

            if roi_edge_mm is None:
                roi_edge_mm = self.config.getfloat("experiment", "raster_roi_edge_mm")
        
            # calcDistFromLength() は直径を要求するため、ROI中心から端までの距離を2倍する
            min_camera_dim = float(roi_edge_mm) * 2.0

        camera_len = self.calcDistFromLength(wavelength, resolution_limit, min_camera_dim)
        self.logger.info(f"calcuated camera_len: {camera_len}")

        # camera_len が　min_camera_len 以下なら min_camera_len を返す
        # camera_len が min_dim より大きいなら camera_len を返す
        if camera_len < min_camera_len:
            camera_len = min_camera_len

        # 小数点第一位に丸める camera_len
        camera_len = round(camera_len, 1)

        return camera_len

    def calcDistFromLength(self, wavelength, resolution_limit, detector_diameter_mm):
        # wavelength と resolution_limit から camera_len を計算する
        # camera_len が min_dim 以下なら min_dim を返す
        # camera_len が min_dim より大きいなら camera_len を返す
        theta = numpy.arcsin(wavelength / 2.0 / resolution_limit)
        bunbo = 2.0 * numpy.tan(2.0 * theta)
        camera_len = detector_diameter_mm / bunbo
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
        dist_raster_list = []

        default_roi = self.config.getint("experiment", "raster_roi", fallback=0)
        default_resol_raster = self.config.getfloat("experiment", "resol_raster")

        for _, row in self.df.iterrows():

            mode = str(row["mode"]).strip().lower()

            # sponge mode
            if mode == "sponge":

                resol_raster = self.config.getfloat(
                    "experiment",
                    "resol_raster_sponge"
                )

                roi_edge_mm = self.config.getfloat(
                    "experiment",
                    "raster_roi_edge_sponge_mm"
                )

                is_roi = True

                dist_raster = self.calcDist(
                    row["wavelength"],
                    resol_raster,
                    isROI=is_roi,
                    roi_edge_mm=roi_edge_mm
                )

                # 最終CSVにも raster_roi=1 を出す
                self.df.at[row.name, "raster_roi"] = 1

                self.logger.info(
                    f"[sponge] resol_raster={resol_raster} "
                    f"roi_edge_mm={roi_edge_mm} "
                    f"dist_raster={dist_raster}"
                )

            # normal modes
            else:

                is_roi = (default_roi == 1)

                dist_raster = self.calcDist(
                    row["wavelength"],
                    default_resol_raster,
                    isROI=is_roi
                )

            dist_raster_list.append(dist_raster)

        self.df["dist_raster"] = dist_raster_list

        self.logger.info(
            f"dist_raster: {self.df['dist_raster'].tolist()}"
        )

    def checkScanSpeed(self):
        """
        raster scan speed 制約から必要最小 exp_raster を計算し、
        仕様 5.9.2 に従って整数 Hz に対応する離散 exposure へ補正する。

        ここでは photon/dose 条件はまだ考慮しない。
        それらは defineScanCondition() で再度まとめて最適化する。
        """
        max_scan_speed = self.config.getfloat("experiment", "max_hori_scan_speed")

        for i, row in self.df.iterrows():
            raster_hbeam = float(row["raster_hbeam"])

            if max_scan_speed <= 0.0:
                raise ValueError("[UserESA] max_hori_scan_speed must be positive.")

            required_exp_by_speed = raster_hbeam / max_scan_speed

            new_exp_raster, freq = self.selectRasterExposureByFrequency(required_exp_by_speed)

            old_exp_raster = float(row["exp_raster"])
            self.df.at[i, "exp_raster"] = new_exp_raster

            self.logger.info(
                "[ScanSpeed] idx=%d raster_hbeam=%.3f max_scan_speed=%.3f "
                "required_exp=%.6f old_exp=%.6f new_exp=%.6f freq=%d Hz",
                i,
                raster_hbeam,
                max_scan_speed,
                required_exp_by_speed,
                old_exp_raster,
                new_exp_raster,
                freq,
            )

    def makeCondList(self):
        self.read_new()
        self.expandCompressedPinInfo()

        self.checkLN2flag()
        self.checkZoomFlag()
        self.checkPinFlag()

        self.setDefaults()
        self.addDistance()
        self.splitBeamsizeInfo()
        self.fillFlux()

        self.checkScanSpeed()
        self.defineScanCondition()
        self.modifyExposureConditions()
        self.sizeWarning()

        # 1行ずつ明示的に検証
        try:
            self.logger.info("Validating dose_list and dist_list")
            for _, row in self.df.iterrows():
                self.validateDoseDist(row)
        except ValueError as e:
            self.logger.error(f"Error in validateDoseDist: {e}")
            raise

        # 正規化
        try:
            self.logger.info("Checking dose_list and dist_list")
            self.checkDoseList()
        except ValueError as e:
            self.logger.error(f"Error in checkDoseList: {e}")
            raise

        self.columns = [
            'root_dir', 'p_index', 'mode', 'puckid', 'pinid', 'sample_name',
            'wavelength', 'raster_vbeam', 'raster_hbeam', 'att_raster', 'hebi_att',
            'exp_raster', 'dist_raster', 'loopsize', 'score_min', 'score_max', 'maxhits',
            'total_osc', 'osc_width', 'ds_vbeam', 'ds_hbeam', 'exp_ds', 'dist_ds', 'dose_ds',
            'dist_list', 'dose_list', 'offset_angle', 'reduced_fact', 'ntimes', 'meas_name',
            'cry_min_size_um', 'cry_max_size_um', 'hel_full_osc', 'hel_part_osc', 'raster_roi',
            'ln2_flag', 'cover_scan_flag', 'zoomcap_flag', 'warm_time'
        ]

        set_types = {
            'wavelength': float,
            'raster_vbeam': float,
            'raster_hbeam': float,
            'att_raster': float,
            'hebi_att': float,
            'exp_raster': float,
            'dist_raster': float,
            'loopsize': float,
            'score_min': int,
            'score_max': int,
            'maxhits': int,
            'total_osc': float,
            'osc_width': float,
            'ds_vbeam': float,
            'ds_hbeam': float,
            'exp_ds': float,
            'dist_ds': float,
            'dose_ds': float,
            'dist_list': str,
            'dose_list': str,
            'offset_angle': float,
            'reduced_fact': float,
            'ntimes': int,
            'cry_min_size_um': float,
            'cry_max_size_um': float,
            'hel_full_osc': float,
            'hel_part_osc': float,
            'raster_roi': int,
            'ln2_flag': int,
            'cover_scan_flag': int,
            'zoomcap_flag': int,
            'warm_time': float,
            'resolution_limit': float,
            'max_crystal_size': float,
        }

        self.df = self.df.astype(set_types)

        if self.isDoseError:
            neg_rows = self.df[self.df['dose_ds'] < 0]

            errmsgs = []
            for _, row in neg_rows.iterrows():
                errmsgs.append(
                    f"{row['puckid']}-{row['pinid']} "
                    f"(desired_exp={row['desired_exp']}, "
                    f"dose/frame={row['dose_per_frame']:.3f} MGy, "
                    f"dose_ds={row['dose_ds']:.3f} MGy)"
                )

            raise RuntimeError(
                "dose_ds < 0 detected. CSV will not be generated. "
                + "; ".join(errmsgs)
            )

        zoo_csv_name = f"{self.csv_prefix}.csv"
        self.df.to_csv(zoo_csv_name, columns=self.columns, index=False, float_format='%.4f')
        self.logger.info(f"Data types of all parameters in the DataFrame: {self.df.dtypes}")

if __name__ == "__main__":
    root_dir = os.getcwd()
    u2db = UserESA(sys.argv[1], root_dir, beamline="BL32XU")
    # logger set
    # u2db.logger = logging.getLogger("ZOO")
    # u2db.logger.setLevel(logging.INFO)

    u2db.makeCondList()
    #u2db.checkDoseList()
    #u2db.read_new()
    #newdf = u2db.expandCompressedPinInfo()
    # CSV ファイルに書き出す
    #newdf.to_csv("check.csv", index=False)
    # u2db.df['ppf_raster']を 指数表記で出力
    #pd.options.display.float_format = '{:.2e}'.format
    #print(u2db.df['dist_raster'])
    #print(u2db.df['dist_ds'])