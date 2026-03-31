import sys
import types
import pytest


def _install_stub_modules():
    stub_names = [
        "LoopMeasurement",
        "AttFactor",
        "StopWatch",
        "AnaHeatmap",
        "CrystalList",
    ]
    for name in stub_names:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod


_install_stub_modules()

from HEBI import HEBI
from ZooMyException import ZooMyException


class DummyHEBI(HEBI):
    def __init__(self):
        self.logger = types.SimpleNamespace(
            info=lambda *a, **k: None,
            debug=lambda *a, **k: None,
            warning=lambda *a, **k: None,
            error=lambda *a, **k: None,
        )
        self.zoo = types.SimpleNamespace(
            doDataCollection=lambda *a, **k: None,
            waitTillReady=lambda *a, **k: None,
        )
        self.lm = types.SimpleNamespace(
            genSingleSchedule=lambda *a, **k: {
                "dose_ds": a[3]["dose_ds"],
                "dist_ds": a[3]["dist_ds"],
                "prefix": a[5],
            },
            genHelical=lambda *a, **k: {
                "dose_ds": a[6]["dose_ds"],
                "dist_ds": a[6]["dist_ds"],
                "prefix": a[4],
            },
        )
        self.phosec_meas = 1.0e12


@pytest.fixture
def hebi():
    return DummyHEBI()


def make_cond(
    dose_ds=10.0,
    dist_ds=120.0,
    dose_list="",
    dist_list="",
):
    return {
        "dose_ds": dose_ds,
        "dist_ds": dist_ds,
        "dose_list": dose_list,
        "dist_list": dist_list,
        "total_osc": 10.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
    }


# -------------------------
# getDoseDistList
# -------------------------

def test_getDoseDistList_normal_operation(hebi):
    cond = make_cond(dose_ds=7.5, dist_ds=130.0)
    assert hebi.getDoseDistList(cond) == [(7.5, 130.0)]


def test_getDoseDistList_dose_list_only(hebi):
    cond = make_cond(
        dose_ds=999.0,
        dist_ds=140.0,
        dose_list="[1, 5, 10]",
        dist_list="",
    )
    assert hebi.getDoseDistList(cond) == [
        (1.0, 140.0),
        (5.0, 140.0),
        (10.0, 140.0),
    ]


def test_getDoseDistList_dose_and_dist_list(hebi):
    cond = make_cond(
        dose_ds=999.0,
        dist_ds=999.0,
        dose_list="[1, 5, 10]",
        dist_list="[120, 110, 100]",
    )
    assert hebi.getDoseDistList(cond) == [
        (1.0, 120.0),
        (5.0, 110.0),
        (10.0, 100.0),
    ]


def test_getDoseDistList_dist_list_only_is_invalid(hebi):
    cond = make_cond(
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="",
        dist_list="[120, 110]",
    )
    with pytest.raises(ZooMyException):
        hebi.getDoseDistList(cond)


def test_getDoseDistList_length_mismatch_is_invalid(hebi):
    cond = make_cond(
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="[1, 5]",
        dist_list="[120, 110, 100]",
    )
    with pytest.raises(ZooMyException):
        hebi.getDoseDistList(cond)


# -------------------------
# doSingle loop behavior
# -------------------------

def test_doSingle_runs_once_without_dose_list(hebi, monkeypatch):
    calls = []

    def fake_do(schedule):
        calls.append(schedule)

    hebi.zoo.doDataCollection = fake_do

    cond = make_cond(dose_ds=8.0, dist_ds=125.0)
    hebi.doSingle((0.0, 0.0, 0.0), cond, phi_face=0.0, prefix="single")

    assert len(calls) == 1
    assert calls[0]["dose_ds"] == 8.0
    assert calls[0]["dist_ds"] == 125.0


def test_doSingle_runs_multiple_with_dose_list(hebi, monkeypatch):
    calls = []

    def fake_do(schedule):
        calls.append(schedule)

    hebi.zoo.doDataCollection = fake_do

    cond = make_cond(
        dose_ds=999.0,
        dist_ds=130.0,
        dose_list="[1, 5, 10]",
        dist_list="",
    )
    hebi.doSingle((0.0, 0.0, 0.0), cond, phi_face=0.0, prefix="single")

    assert len(calls) == 3
    assert [(c["dose_ds"], c["dist_ds"]) for c in calls] == [
        (1.0, 130.0),
        (5.0, 130.0),
        (10.0, 130.0),
    ]


def test_doSingle_runs_multiple_with_dose_and_dist_list(hebi, monkeypatch):
    calls = []

    def fake_do(schedule):
        calls.append(schedule)

    hebi.zoo.doDataCollection = fake_do

    cond = make_cond(
        dose_ds=999.0,
        dist_ds=999.0,
        dose_list="[1, 5]",
        dist_list="[120, 110]",
    )
    hebi.doSingle((0.0, 0.0, 0.0), cond, phi_face=0.0, prefix="single")

    assert len(calls) == 2
    assert [(c["dose_ds"], c["dist_ds"]) for c in calls] == [
        (1.0, 120.0),
        (5.0, 110.0),
    ]
