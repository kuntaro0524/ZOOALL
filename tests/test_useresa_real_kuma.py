import math
import logging
import textwrap
import configparser

import pytest
import pandas as pd

import UserESA


@pytest.fixture
def useresa_env(monkeypatch, tmp_path):
    dose_csv = tmp_path / "dose.csv"
    dose_csv.write_text(textwrap.dedent("""\
        energy,dose_mgy_per_photon_density
        8.0,1.0e-10
        10.0,1.2e-10
        12.0,1.4e-10
        14.0,1.6e-10
        16.0,1.8e-10
    """))

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    beamline_ini = config_dir / "beamline.ini"
    beamline_ini.write_text(textwrap.dedent(f"""\
        [files]
        dose_csv = {dose_csv}

        [experiment]
        max_hori_scan_speed = 1000.0
        max_raster_frequency = 220
        dose_ds = 10.0
        dose_ds_phasing = 5.0
        thinnest_att_thick = 100.0
    """))

    monkeypatch.setenv("ZOOCONFIGPATH", str(config_dir))

    u = UserESA.UserESA.__new__(UserESA.UserESA)
    u.config = configparser.ConfigParser()
    u.config.read(beamline_ini)
    u.logger = logging.getLogger("test_useresa_real_kuma")
    u.logger.setLevel(logging.DEBUG)
    u.isDoseError = False
    return u


def make_df(**overrides):
    row = {
        "puckid": "P01",
        "pinid": 1,
        "sample_name": "sample01",
        "desired_exp": "normal",
        "mode": "single",
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "raster_vbeam": 10.0,
        "flux": 1.0e12,
        "wavelength": 1.0,
        "exp_raster": 0.04,
        "att_raster": 100.0,
        "hebi_att": 100.0,
        "dose_ds": 10.0,
        "dose_list": "",
        "dist_list": "",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def assert_exp_is_integer_hz(exp_raster, max_freq=220):
    freq = 1.0 / float(exp_raster)
    nearest = round(freq)
    assert abs(freq - nearest) < 1e-9
    assert 1 <= nearest <= max_freq
    return nearest


def test_define_scan_condition_normal_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="normal",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_exp_is_integer_hz(row["exp_raster"])

    assert freq == 25
    assert row["exp_raster"] == pytest.approx(0.04)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(4.0e10)
    assert row["dose_per_frame"] > 0.0

    expected_dose_ds = 10.0 - row["dose_per_frame"] * 2.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)


def test_define_scan_condition_low_flux_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="normal",
        mode="multi",
        flux=2.0e11,
        wavelength=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_exp_is_integer_hz(row["exp_raster"])

    assert freq == 5
    assert row["exp_raster"] == pytest.approx(0.2)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(4.0e10)

    expected_dose_ds = 10.0 - row["dose_per_frame"] * 1.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)


def test_define_scan_condition_high_dose_scan_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="high_dose_scan",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_exp_is_integer_hz(row["exp_raster"])

    assert freq == 10
    assert row["ppf_raster"] == pytest.approx(6.0e10)
    assert row["att_raster"] <= 100.0


def test_define_scan_condition_ultra_high_dose_scan_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="ultra_high_dose_scan",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    freq = assert_exp_is_integer_hz(row["exp_raster"])

    assert freq == 5
    assert row["ppf_raster"] == pytest.approx(1.2e11)
    assert row["att_raster"] <= 100.0


def test_define_scan_condition_phasing_uses_5mgy_budget_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="phasing",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
        dose_ds=5.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    expected_dose_ds = 5.0 - row["dose_per_frame"] * 2.0
    assert row["dose_ds"] == pytest.approx(expected_dose_ds)


def test_define_scan_condition_dose_list_keeps_scan_dose_1kgy_real_kuma(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="normal",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
        dose_list="5",
        dose_ds=10.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]
    assert_exp_is_integer_hz(row["exp_raster"])

    assert row["dose_per_frame"] == pytest.approx(0.001)
    assert row["att_raster"] <= 100.0

    # dose_list 有効時は dose_ds を scan dose で減算しない
    assert row["dose_ds"] == pytest.approx(10.0)


def test_modify_exposure_conditions_does_not_change_exp(useresa_env):
    u = useresa_env
    u.df = make_df(
        desired_exp="normal",
        mode="single",
        flux=1.0e12,
        wavelength=1.0,
    )

    u.defineScanCondition()

    before = float(u.df.iloc[0]["exp_raster"])
    u.modifyExposureConditions()
    after = float(u.df.iloc[0]["exp_raster"])

    assert after == pytest.approx(before)


def test_modify_exposure_conditions_raises_when_att_over_100(useresa_env):
    u = useresa_env
    u.df = make_df(att_raster=100.1)

    with pytest.raises(RuntimeError):
        u.modifyExposureConditions()

def test_valid_raster_frequency_finite_decimal(useresa_env):
    u = useresa_env

    # 許可される: f = 2^a * 5^b
    for f in [1, 2, 4, 5, 8, 10, 20, 25, 40, 50, 100, 125, 200]:
        assert u.isValidRasterFrequency(f)

    # 禁止される: 3, 6, 7, 12, 30, 36 など
    for f in [3, 6, 7, 12, 15, 30, 36, 60, 110]:
        assert not u.isValidRasterFrequency(f)


def test_allowed_raster_frequencies_are_finite_decimal(useresa_env):
    u = useresa_env

    allowed = u.getAllowedRasterFrequencies()

    assert 1 in allowed
    assert 200 in allowed
    assert 220 not in allowed
    assert 36 not in allowed
    assert 30 not in allowed

    for f in allowed:
        assert u.isValidRasterFrequency(f)
        assert 1 <= f <= 220


def test_select_raster_exposure_rejects_repeating_decimal_36hz(useresa_env):
    u = useresa_env

    # required が 1/36 より少し小さい場合、
    # 旧実装なら 36Hz = 0.027777... を選んだ。
    # 新仕様では 36Hz は禁止なので、次に長い有限小数候補を選ぶ。
    required = 1.0 / 36.0

    exp_raster, freq = u.selectRasterExposureByFrequency(required)

    assert freq != 36
    assert u.isValidRasterFrequency(freq)
    assert exp_raster >= required

    # 36Hzの次に条件を満たす有限小数候補は 32Hz = 0.03125 s
    assert freq == 32
    assert exp_raster == pytest.approx(0.03125)


def test_select_raster_exposure_chooses_40hz_for_25ms(useresa_env):
    u = useresa_env

    required = 0.025

    exp_raster, freq = u.selectRasterExposureByFrequency(required)

    assert freq == 40
    assert exp_raster == pytest.approx(0.025)


def test_select_raster_exposure_chooses_200hz_for_short_required(useresa_env):
    u = useresa_env

    required = 0.004

    exp_raster, freq = u.selectRasterExposureByFrequency(required)

    # 220Hzは有限小数にならないので禁止。
    # 最大の有効候補は200Hz。
    assert freq == 200
    assert exp_raster == pytest.approx(0.005)


def test_define_scan_condition_ultra_high_dose_scan_avoids_36hz(useresa_env):
    u = useresa_env

    # ultra_high_dose_scan:
    # target_ppf = 1.2e11
    # flux = 4.32e12 にすると required_exp = 1.2e11 / 4.32e12 = 1/36
    # 旧実装なら 36Hz を選ぶが、新仕様では 25Hz = 0.04 s を選ぶ。
    u.df = make_df(
        desired_exp="ultra_high_dose_scan",
        mode="single",
        flux=4.32e12,
        wavelength=1.0,
        raster_hbeam=1.0,  # scan speed制約を十分ゆるくする
    )

    u.defineScanCondition()

    row = u.df.iloc[0]

    freq = round(1.0 / row["exp_raster"])

    assert freq != 36
    assert freq == 20
    assert row["exp_raster"] == pytest.approx(0.05)
    assert row["att_raster"] <= 100.0
    assert row["ppf_raster"] == pytest.approx(1.2e11)

def test_thinnest_att_thick_is_read_from_beamline_ini(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    assert u.getThinnestAttenuatorThickness() == pytest.approx(100.0)


def test_attenuation_hardware_allows_100_percent(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    assert u.isAttenuationHardwareAllowed(
        wavelength=1.0,
        att_raster=100.0,
    )


def test_attenuation_hardware_rejects_between_thinnest_and_100(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    thinnest_trans = u.calcThinnestAttenuatorTransmission(1.0)
    thinnest_percent = thinnest_trans * 100.0

    # 最薄アッテネータ透過率より少し大きく、100%未満
    # → ハード的に実現不能
    bad_att = (thinnest_percent + 100.0) / 2.0

    assert thinnest_percent < bad_att < 100.0
    assert not u.isAttenuationHardwareAllowed(
        wavelength=1.0,
        att_raster=bad_att,
    )


def test_attenuation_hardware_allows_below_thinnest(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    thinnest_trans = u.calcThinnestAttenuatorTransmission(1.0)
    thinnest_percent = thinnest_trans * 100.0

    good_att = thinnest_percent * 0.8

    assert good_att < thinnest_percent
    assert u.isAttenuationHardwareAllowed(
        wavelength=1.0,
        att_raster=good_att,
    )


def test_define_scan_condition_skips_unavailable_att_range(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    # flux を調整して、
    # exp=0.1 s だと att=80% になるようにする。
    #
    # normal target_ppf = 4E10
    # flux = 5E11
    # exp = 0.1
    # att = 4E10 / (5E11 * 0.1) * 100 = 80%
    #
    # Al 100um, 1A の最薄透過率はおよそ 75% 程度なので、
    # 80% は禁止領域。
    #
    # 次の候補 exp=0.125 s なら
    # att = 64%
    # となり採用されるはず。
    u.df = make_df(
        desired_exp="normal",
        mode="single",
        flux=5.0e11,
        wavelength=1.0,
        raster_hbeam=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]

    assert row["exp_raster"] == pytest.approx(0.125)
    assert round(1.0 / row["exp_raster"]) == 8
    assert row["att_raster"] == pytest.approx(64.0)
    assert u.isAttenuationHardwareAllowed(
        wavelength=row["wavelength"],
        att_raster=row["att_raster"],
    )


def test_define_scan_condition_keeps_100_percent_without_attenuator(useresa_env):
    u = useresa_env

    u.config.set("experiment", "thinnest_att_thick", "100.0")

    # target_ppf = 4E10
    # flux = 4E11
    # exp=0.1
    # att=100%
    # これは attenuator 不使用なので許可。
    u.df = make_df(
        desired_exp="normal",
        mode="single",
        flux=4.0e11,
        wavelength=1.0,
        raster_hbeam=1.0,
    )

    u.defineScanCondition()

    row = u.df.iloc[0]

    assert row["exp_raster"] == pytest.approx(0.1)
    assert row["att_raster"] == pytest.approx(100.0)
    assert u.isAttenuationHardwareAllowed(
        wavelength=row["wavelength"],
        att_raster=row["att_raster"],
    )