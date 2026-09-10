import pytest
from KUMA import KUMA


@pytest.fixture
def kuma():
    return KUMA()


def test_kuma_single_path_with_realistic_cond(kuma):
    cond = {
        "mode": "single",
        "dose_ds": 5.0,
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

    exp_time, mod_trans = kuma.getBestCondsSingle(cond, flux)

    assert exp_time > 0.0
    assert 0.0 < mod_trans <= 1.0


def test_kuma_multi_path_with_realistic_cond(kuma):
    cond = {
        "mode": "multi",
        "dose_ds": 5.0,
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

    exp_time, mod_trans = kuma.getBestCondsMulti(cond, flux)

    assert exp_time > 0.0
    assert 0.0 < mod_trans <= 1.0

def test_kuma_helical_path_with_realistic_cond(kuma):
    cond = {
        "mode": "helical",
        "dose_ds": 5.0,
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
    dist_vec_mm = 0.1

    exp_time, mod_trans = kuma.getBestCondsHelical(cond, flux, dist_vec_mm)

    assert exp_time > 0.0
    assert 0.0 < mod_trans <= 1.0
