import math
import sys
import types
import textwrap
import pytest


# ------------------------------------------------------------
# fixtures / helpers
# ------------------------------------------------------------
@pytest.fixture
def kuma_env(monkeypatch, tmp_path):
    """
    KUMA が読む beamline.ini / dose.csv をテスト用に作る。
    さらに KUMA.getBestCondsSingle/Multi が内部 import する
    dose.fields / Libs.dose.fields をスタブする。
    """
    # --- fake dose csv ---
    dose_csv = tmp_path / "dose.csv"
    dose_csv.write_text(
        textwrap.dedent("""\
        energy,dose_mgy_per_photon,density_limit_for10MGy
        8.0,1.0e-10,1.0e11
        10.0,1.2e-10,8.333333333e10
        12.0,1.4e-10,7.142857143e10
        14.0,1.6e-10,6.25e10
        16.0,1.8e-10,5.555555556e10
        """)
    )

    # --- fake beamline.ini ---
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

    # --- stub modules for imports inside KUMA ---
    def _get_dose_ds(cond):
        v = cond["dose_ds"]
        return [float(v)] if not isinstance(v, (list, tuple)) else [float(x) for x in v]

    def _get_dist_ds(cond):
        v = cond["dist_ds"]
        return [float(v)] if not isinstance(v, (list, tuple)) else [float(x) for x in v]

    dose_pkg = types.ModuleType("dose")
    dose_fields = types.ModuleType("dose.fields")
    dose_fields.get_dose_ds = _get_dose_ds
    dose_fields.get_dist_ds = _get_dist_ds
    sys.modules["dose"] = dose_pkg
    sys.modules["dose.fields"] = dose_fields

    libs_pkg = types.ModuleType("Libs")
    libs_dose_pkg = types.ModuleType("Libs.dose")
    libs_dose_fields = types.ModuleType("Libs.dose.fields")
    libs_dose_fields.get_dose_ds = _get_dose_ds
    libs_dose_fields.get_dist_ds = _get_dist_ds
    sys.modules["Libs"] = libs_pkg
    sys.modules["Libs.dose"] = libs_dose_pkg
    sys.modules["Libs.dose.fields"] = libs_dose_fields

    from KUMA import KUMA
    return KUMA()


def _n_frames(cond):
    return int(cond["total_osc"] / cond["osc_width"])


def _single_or_multi_density(flux, exp_time, transmission, cond):
    """
    LM single/multi path が実際に与える photon density [photons/um^2]
    """
    area = cond["ds_hbeam"] * cond["ds_vbeam"]
    n_frames = _n_frames(cond)
    return flux * exp_time * transmission * n_frames / area


def _helical_density(flux, exp_time, transmission, cond, dist_vec_mm):
    """
    LM helical path が実際に与える photon density [photons/um^2]
    """
    dist_vec_um = dist_vec_mm * 1000.0
    area = dist_vec_um * cond["ds_vbeam"]
    n_frames = _n_frames(cond)
    return flux * exp_time * transmission * n_frames / area


# ------------------------------------------------------------
# tests for the exact KUMA paths used by LoopMeasurement
# ------------------------------------------------------------
def test_kuma_single_path_matches_density_limit(kuma_env):
    kuma = kuma_env

    cond = {
        "mode": "single",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "reduced_fact": 1.0,
        "ntimes": 1,
    }
    flux = 1.0e12

    exp_time, transmission = kuma.getBestCondsSingle(cond.copy(), flux)
    density_limit = kuma.convDoseToDensityLimit(cond["dose_ds"], cond["wavelength"])
    actual_density = _single_or_multi_density(flux, exp_time, transmission, cond)

    assert exp_time > 0
    assert transmission > 0
    assert math.isclose(actual_density, density_limit, rel_tol=1e-6)


def test_kuma_multi_path_matches_density_limit(kuma_env):
    kuma = kuma_env

    cond = {
        "mode": "multi",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "reduced_fact": 1.0,
        "ntimes": 1,
    }
    flux = 1.0e12

    exp_time, transmission = kuma.getBestCondsMulti(cond.copy(), flux)
    density_limit = kuma.convDoseToDensityLimit(cond["dose_ds"], cond["wavelength"])
    actual_density = _single_or_multi_density(flux, exp_time, transmission, cond)

    assert exp_time > 0
    assert transmission > 0
    assert math.isclose(actual_density, density_limit, rel_tol=1e-6)


def test_kuma_helical_path_matches_density_limit(kuma_env):
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
    flux = 1.0e12
    dist_vec_mm = 0.1

    exp_time, transmission = kuma.getBestCondsHelical(cond.copy(), flux, dist_vec_mm)
    density_limit = kuma.convDoseToDensityLimit(cond["dose_ds"], cond["wavelength"])
    actual_density = _helical_density(flux, exp_time, transmission, cond, dist_vec_mm)

    assert exp_time > 0
    assert transmission > 0
    assert math.isclose(actual_density, density_limit, rel_tol=1e-6)


def test_kuma_helical_reduced_fact_scales_density(kuma_env):
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
        "reduced_fact": 0.2,
        "ntimes": 5,
    }
    flux = 1.0e12
    dist_vec_mm = 0.1

    exp_time, transmission = kuma.getBestCondsHelical(cond.copy(), flux, dist_vec_mm)
    density_limit = kuma.convDoseToDensityLimit(cond["dose_ds"], cond["wavelength"])
    actual_density = _helical_density(flux, exp_time, transmission, cond, dist_vec_mm)

    assert math.isclose(actual_density, density_limit * cond["reduced_fact"], rel_tol=1e-6)


# ------------------------------------------------------------
# known inconsistency outside the main LoopMeasurement path
# ------------------------------------------------------------
@pytest.mark.xfail(reason="Known inconsistency: getDose() path is scaled ~1/10 relative to convDoseToExptimeLimit()")
def test_getDose_roundtrip_is_inconsistent_but_not_used_by_loopmeasurement(kuma_env):
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
