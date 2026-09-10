# test_useresa_raster_exposure.py
import os
import math
import logging
import types
import configparser

import pytest
import pandas as pd


# UserESA.py と同じディレクトリで pytest を実行する想定
import UserESA


class DummyKUMA:
    """
    KUMA.KUMA.getDose() の代用品。

    ここでは単純に、
        dose = dose_rate_per_sec * exp_time
    とする。

    dose_rate_per_sec はテストで扱いやすいよう 1.0 MGy/s に固定。
    """
    def getDose(self, hbeam, vbeam, flux, wavelength, exp_time):
        return 1.0 * float(exp_time)


def make_test_config():
    config = configparser.ConfigParser()
    config.add_section("experiment")
    config.set("experiment", "max_hori_scan_speed", "1000.0")
    config.set("experiment", "max_raster_frequency", "220")
    config.set("experiment", "dose_ds", "10.0")
    config.set("experiment", "dose_ds_phasing", "5.0")
    return config


def make_useresa_for_test(monkeypatch):
    """
    __init__ を呼ばずに UserESA インスタンスを作る。
    beamline.ini, BeamsizeConfig などに依存しないため。
    """
    monkeypatch.setattr(UserESA.KUMA, "KUMA", lambda: DummyKUMA())

    u = UserESA.UserESA.__new__(UserESA.UserESA)
    u.config = make_test_config()
    u.logger = logging.getLogger("test_useresa")
    u.logger.setLevel(logging.DEBUG)
    u.debug = True
    u.isDoseError = False

    return u


def make_base_df(**overrides):
    row = {
        "puckid": "P01",
        "pinid": 1,
        "sample_name": "sample01",
        "desired_exp": "normal",
        "mode": "single",

        # beam / raster
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "raster_vbeam": 10.0,

        # flux と wavelength
        "flux": 1.0e12,
        "wavelength": 1.0,

        # initial values
        "exp_raster": 0.04,
        "att_raster": 100.0,
        "hebi_att": 100.0,
        "dose_ds": 10.0,

        # optional columns
        "dose_list": "",
        "dist_list": "",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def assert_integer_frequency_exp(exp_raster, max_freq=220):
    """
    exp_raster = 1 / f になっていて、
    f が整数かつ 1 <= f <= max_freq であることを確認する。
    """
    freq = 1.0 / exp_raster
    nearest = round(freq)

    assert abs(freq - nearest) < 1e-9
    assert 1 <= nearest <= max_freq

    return nearest


def test_select_raster_exposure_by_frequency_basic(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # required = 0.004 sec なら、220 Hz上限により 1/220 sec
    exp, f = u.selectRasterExposureByFrequency(0.004)
    assert f == 220
    assert exp == pytest.approx(1.0 / 220.0)

    # required = 0.0101 sec なら floor(1/0.0101)=99 Hz
    exp, f = u.selectRasterExposureByFrequency(0.0101)
    assert f == 99
    assert exp == pytest.approx(1.0 / 99.0)
    assert exp >= 0.0101

    # required = 0.040 sec なら 25 Hz
    exp, f = u.selectRasterExposureByFrequency(0.040)
    assert f == 32
    assert exp == pytest.approx(0.03125)


def test_select_raster_exposure_too_long_raises(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # 1 Hz でも足りない required exposure
    with pytest.raises(ValueError):
        u.selectRasterExposureByFrequency(1.5)


def test_define_scan_condition_normal_uses_integer_frequency(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # flux=1e12, target photons=4e10
    # required_exp_by_signal = 4e10 / 1e12 = 0.04 sec
    # max_scan_speed側 required = 10 / 1000 = 0.01 sec
    # maxは0.04 secなので f=25 Hz, exp=0.04 sec
    u.df = make_base_df(
        desired_exp="normal",
        mode="single",
        flux=1.0e12,
        raster_hbeam=10.0,
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 32
    assert row["exp_raster"] == pytest.approx(0.03125)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(4.0e10)

    # DummyKUMA: base dose = exp_raster
    # dose_per_frame = exp * att/100
    assert row["dose_per_frame"] == pytest.approx(
        row["exp_raster"] * row["att_raster"] / 100.0
    )

    # single は scan 2回分
    expected_dose_ds = 10.0 - row["dose_per_frame"] * 2.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)


def test_define_scan_condition_low_flux_extends_exposure(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # flux=2e11, target photons=4e10
    # required_exp_by_signal = 0.2 sec
    # f=5 Hz, exp=0.2 sec
    u.df = make_base_df(
        desired_exp="normal",
        mode="multi",
        flux=2.0e11,
        raster_hbeam=10.0,
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 5
    assert row["exp_raster"] == pytest.approx(0.2)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(4.0e10)

    # multi は scan 1回分
    expected_dose_ds = 10.0 - row["dose_per_frame"] * 1.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)


def test_define_scan_condition_high_dose_scan_factor(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # high_dose_scan は normal の 1.5 倍 photon 相当
    # target = 6e10
    # flux=1e12 -> required = 0.06 sec
    # floor(1/0.06)=16 Hz -> exp=0.0625 sec
    u.df = make_base_df(
        desired_exp="high_dose_scan",
        mode="single",
        flux=1.0e12,
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 16
    assert row["exp_raster"] == pytest.approx(1.0 / 16.0)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(6.0e10)


def test_define_scan_condition_ultra_high_dose_scan_factor(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # ultra_high_dose_scan は normal の 3倍 photon 相当
    # target = 1.2e11
    # flux=1e12 -> required = 0.12 sec
    # floor(1/0.12)=8 Hz -> exp=0.125 sec
    u.df = make_base_df(
        desired_exp="ultra_high_dose_scan",
        mode="single",
        flux=1.0e12,
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 8
    assert row["exp_raster"] == pytest.approx(1.0 / 8.0)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(1.2e11)


def test_define_scan_condition_phasing_uses_5mgy_budget(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    u.df = make_base_df(
        desired_exp="phasing",
        mode="single",
        flux=1.0e12,
        dose_ds=5.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]

    expected_dose_ds = 5.0 - row["dose_per_frame"] * 2.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)

def test_define_scan_condition_dose_list_scan_dose_fixed(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    u.df = make_base_df(
        desired_exp="normal",
        mode="single",
        flux=1.0e12,
        raster_hbeam=1.0,   # scan speed 制約を緩くする
        dose_list="5",
        dist_list="",
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 220
    assert row["dose_per_frame"] == pytest.approx(0.001)
    assert row["att_raster"] <= 100.0

    # dose_list 有効時は dose_ds を scan dose で減算しない
    assert row["dose_ds"] == pytest.approx(10.0)


def test_check_scan_speed_selects_integer_frequency(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    # raster_hbeam=100 um, max speed=1000 um/s
    # required_exp_by_speed=0.1 sec
    # f=10 Hz, exp=0.1 sec
    u.df = make_base_df(
        raster_hbeam=100.0,
        exp_raster=0.04,
    )

    u.checkScanSpeed()

    row = u.df.iloc[0]
    freq = assert_integer_frequency_exp(row["exp_raster"])

    assert freq == 10
    assert row["exp_raster"] == pytest.approx(0.1)


def test_modify_exposure_conditions_raises_if_att_over_100(monkeypatch):
    u = make_useresa_for_test(monkeypatch)

    u.df = make_base_df(
        att_raster=101.0,
    )

    with pytest.raises(RuntimeError):
        u.modifyExposureConditions()