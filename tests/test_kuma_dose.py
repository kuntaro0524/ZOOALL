import os
import math
import tempfile
import textwrap
import pytest

from KUMA import KUMA

@pytest.fixture
def kuma_env(monkeypatch, tmp_path):
    # beamline.ini と dose CSV をテスト用に作る
    dose_csv = tmp_path / "dose.csv"
    dose_csv.write_text(
        textwrap.dedent("""\
        energy,dose_mgy_per_photon_density
        8.0,1.0e-10
        10.0,1.2e-10
        12.0,1.4e-10
        14.0,1.6e-10
        16.0,1.8e-10
        """)
    )

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    beamline_ini = config_dir / "beamline.ini"
    beamline_ini.write_text(
        textwrap.dedent(f"""\
        [files]
        dose_csv = {dose_csv}
        """)
    )

    monkeypatch.setenv("ZOOCONFIGPATH", str(config_dir))
    return KUMA()


def test_getDose_monotonic_with_flux(kuma_env):
    kuma = kuma_env
    beam_h = 10.0
    beam_v = 10.0
    energy = 12.0
    exp_time = 0.02

    dose_low = kuma.getDose(beam_h, beam_v, 1.0e12, energy, exp_time)
    dose_high = kuma.getDose(beam_h, beam_v, 2.0e12, energy, exp_time)

    assert dose_high > dose_low
    assert math.isclose(dose_high / dose_low, 2.0, rel_tol=1e-6)


def test_getDose_monotonic_with_beam_area(kuma_env):
    kuma = kuma_env
    energy = 12.0
    flux = 1.0e12
    exp_time = 0.02

    dose_small_beam = kuma.getDose(10.0, 10.0, flux, energy, exp_time)
    dose_large_beam = kuma.getDose(20.0, 20.0, flux, energy, exp_time)

    assert dose_large_beam < dose_small_beam
    # 面積4倍なら dose は1/4になるはず
    assert math.isclose(dose_small_beam / dose_large_beam, 4.0, rel_tol=1e-6)


def test_getDose_monotonic_with_exptime(kuma_env):
    kuma = kuma_env
    beam_h = 10.0
    beam_v = 10.0
    flux = 1.0e12
    energy = 12.0

    dose_short = kuma.getDose(beam_h, beam_v, flux, energy, 0.01)
    dose_long = kuma.getDose(beam_h, beam_v, flux, energy, 0.02)

    assert dose_long > dose_short
    assert math.isclose(dose_long / dose_short, 2.0, rel_tol=1e-6)


def test_convDoseToExptimeLimit_roundtrip(kuma_env):
    kuma = kuma_env
    beam_h = 10.0
    beam_v = 10.0
    flux = 1.0e12
    wavelength = 12.3984 / 12.0  # energy=12 keV
    energy = 12.0
    target_dose = 10.0

    exptime_limit = kuma.convDoseToExptimeLimit(
        target_dose, beam_h, beam_v, flux, wavelength
    )
    estimated_dose = kuma.getDose(beam_h, beam_v, flux, energy, exptime_limit)

    # 実装が内部で一貫していれば target_dose に近いはず
    assert math.isclose(estimated_dose, target_dose, rel_tol=1e-3)


def test_getDoseLimitParams_density_matches_inverse_relation(kuma_env):
    kuma = kuma_env
    energy = 12.0

    dose_per_photon, density_limit = kuma.getDoseLimitParams(aimed_dose=10.0, energy=energy)

    # 10 MGy 到達密度と 1 photon あたり dose の積は概ね 10 MGy
    # CSV の意味づけが一貫しているかの確認
    total = dose_per_photon * density_limit
    assert math.isclose(total, 10.0, rel_tol=1e-3)

def test_kuma_helical_consistency(kuma_env):
    kuma = kuma_env

    cond = {
        "mode": "helical",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 360.0,
        "osc_width": 0.1,
        "reduced_fact": 1.0,
        "ntimes": 1,
    }

    flux = 1e12
    dist_vec = 0.1  # mm

    exp_time, trans = kuma.getBestCondsHelical(cond, flux, dist_vec)

    assert exp_time > 0
    assert trans > 0

def test_convDoseToExptimeLimit_roundtrip(kuma_env):
    kuma = kuma_env
    beam_h = 10.0
    beam_v = 10.0
    flux = 1.0e12
    wavelength = 12.3984 / 12.0
    energy = 12.0
    target_dose = 10.0

    exptime_limit = kuma.convDoseToExptimeLimit(
        target_dose, beam_h, beam_v, flux, wavelength
    )
    estimated_dose = kuma.getDose(beam_h, beam_v, flux, energy, exptime_limit)

    assert math.isclose(estimated_dose, target_dose, rel_tol=1e-3)


import numpy as np

def test_getDose_matches_definition():
    """
    dose = flux_density * exposure_time * dose_coeff
    が成立しているか確認
    """

    from KUMA import KUMA

    kuma = KUMA()

    # テスト条件（適当だが現実的な値）
    beam_h = 10.0  # um
    beam_v = 10.0  # um
    flux = 1e12    # photons/sec
    energy = 12.3984
    exp_time = 0.1 # sec

    # KUMAの計算
    dose = kuma.getDose(beam_h, beam_v, flux, energy, exp_time)

    # 手計算
    flux_density = flux / (beam_h * beam_v)
    dose_coeff = kuma.getDoseCoeffPerPhoton(energy)
    expected = flux_density * exp_time * dose_coeff

    # 比較
    assert np.isclose(dose, expected, rtol=1e-6), \
        f"dose mismatch: got={dose}, expected={expected}"

def test_getDose_linear_with_time():
    from KUMA import KUMA
    kuma = KUMA()

    beam_h = 10
    beam_v = 10
    flux = 1e12
    energy = 12.3984

    d1 = kuma.getDose(beam_h, beam_v, flux, energy, 0.1)
    d2 = kuma.getDose(beam_h, beam_v, flux, energy, 0.2)

    assert abs(d2 - 2*d1) / d1 < 1e-6


def test_getDose_inverse_with_area():
    from KUMA import KUMA
    kuma = KUMA()

    flux = 1e12
    energy = 12.3984
    exp_time = 0.1

    d1 = kuma.getDose(10, 10, flux, energy, exp_time)
    d2 = kuma.getDose(20, 20, flux, energy, exp_time)

    assert d2 < d1


