
import logging
import sys
import types
import pytest

# --- Stub external modules that HEBI imports but this test does not use ---
for name in ["LoopMeasurement", "AttFactor", "StopWatch", "AnaHeatmap", "CrystalList"]:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

if "ZooMyException" not in sys.modules:
    zm = types.ModuleType("ZooMyException")
    class ZooMyException(Exception):
        pass
    zm.ZooMyException = ZooMyException
    sys.modules["ZooMyException"] = zm

from ZooMyException import ZooMyException
from HEBI import HEBI


class DummyZoo:
    def __init__(self):
        self.calls = []

    def doDataCollection(self, schedule):
        self.calls.append(("doDataCollection", schedule))

    def waitTillReady(self):
        self.calls.append(("waitTillReady", None))

    def doRaster(self, schedule):
        self.calls.append(("doRaster", schedule))


class DummyLM:
    def __init__(self):
        self.single_calls = []
        self.helical_calls = []

    def genSingleSchedule(self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True):
        call = {
            "start_phi": start_phi,
            "end_phi": end_phi,
            "center_xyz": center_xyz,
            "cond": cond.copy(),
            "phosec": phosec,
            "prefix": prefix,
            "same_point": same_point,
        }
        self.single_calls.append(call)
        return {"kind": "single", "prefix": prefix, "cond": cond.copy()}

    def genHelical(self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond):
        call = {
            "start_phi": start_phi,
            "end_phi": end_phi,
            "left_xyz": left_xyz,
            "right_xyz": right_xyz,
            "cond": cond.copy(),
            "phosec": phosec,
            "prefix": prefix,
        }
        self.helical_calls.append(call)
        return {"kind": "helical", "prefix": prefix, "cond": cond.copy()}


class DummyStopWatch:
    pass


def make_hebi():
    logger = logging.getLogger("ZOO.HEBI")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)

    zoo = DummyZoo()
    lm = DummyLM()
    sw = DummyStopWatch()
    hebi = HEBI(zoo, lm, sw, phosec=1.23e12)
    return hebi, zoo, lm


def test_parse_series_empty():
    hebi, _, _ = make_hebi()
    assert hebi._parse_series_like_text("") == []
    assert hebi._parse_series_like_text(None) == []
    assert hebi._parse_series_like_text("nan") == []


def test_parse_series_single():
    hebi, _, _ = make_hebi()
    assert hebi._parse_series_like_text("5") == [5.0]


def test_parse_series_bracketed():
    hebi, _, _ = make_hebi()
    assert hebi._parse_series_like_text("[5, 10, 20]") == [5.0, 10.0, 20.0]


def test_getDoseDistList_normal_case():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": ""}
    assert hebi.getDoseDistList(cond) == [(10.0, 125.0)]


def test_getDoseDistList_dose_only():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": ""}
    assert hebi.getDoseDistList(cond) == [(1.0, 125.0), (2.0, 125.0)]


def test_getDoseDistList_dose_and_dist():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": "[100, 110]"}
    assert hebi.getDoseDistList(cond) == [(1.0, 100.0), (2.0, 110.0)]


def test_getDoseDistList_rejects_dist_only():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": "[100, 110]"}
    with pytest.raises(ZooMyException, match="dist_list only"):
        hebi.getDoseDistList(cond)


def test_getDoseDistList_rejects_length_mismatch():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": "[100]"}
    with pytest.raises(ZooMyException, match="length mismatch"):
        hebi.getDoseDistList(cond)


def test_doSingle_generates_unique_prefixes_and_updates_cond():
    hebi, zoo, lm = make_hebi()
    cond = {
        "total_osc": 20.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1, 2]",
        "dist_list": "[100, 110]",
    }

    hebi.doSingle((0.0, 0.0, 0.0), cond, phi_face=30.0, prefix="cry00_single")

    assert [c["prefix"] for c in lm.single_calls] == ["cry00_single_00", "cry00_single_01"]
    assert lm.single_calls[0]["cond"]["dose_ds"] == 1.0
    assert lm.single_calls[0]["cond"]["dist_ds"] == 100.0
    assert lm.single_calls[1]["cond"]["dose_ds"] == 2.0
    assert lm.single_calls[1]["cond"]["dist_ds"] == 110.0
    assert len([c for c in zoo.calls if c[0] == "doDataCollection"]) == 2


def test_doHelical_generates_unique_prefixes_and_updates_cond():
    hebi, zoo, lm = make_hebi()
    cond = {
        "total_osc": 40.0,
        "ds_hbeam": 10.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1, 2]",
        "dist_list": "[130, 140]",
    }

    hebi.doHelical((0.0, 0.0, 0.0), (0.0, 0.1, 0.0), cond, phi_face=45.0, prefix="cry03_hel")

    assert [c["prefix"] for c in lm.helical_calls] == ["cry03_hel_00", "cry03_hel_01"]
    assert lm.helical_calls[0]["cond"]["dose_ds"] == 1.0
    assert lm.helical_calls[0]["cond"]["dist_ds"] == 130.0
    assert lm.helical_calls[1]["cond"]["dose_ds"] == 2.0
    assert lm.helical_calls[1]["cond"]["dist_ds"] == 140.0
    assert len([c for c in zoo.calls if c[0] == "doDataCollection"]) == 2


def test_doHelical_with_single_entry_still_uses_helical_prefix():
    hebi, _, lm = make_hebi()
    cond = {
        "total_osc": 40.0,
        "ds_hbeam": 10.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[3]",
        "dist_list": "[150]",
    }

    hebi.doHelical((0.0, 0.0, 0.0), (0.0, 0.1, 0.0), cond, phi_face=45.0, prefix="cry07_hel")

    assert [c["prefix"] for c in lm.helical_calls] == ["cry07_hel_00"]


class DummyCrystal:
    def __init__(self, rpos, lpos):
        self._rpos = rpos
        self._lpos = lpos

    def getRoughEdges(self):
        return self._rpos, self._lpos


def test_mainLoop_small_crystal_calls_doSingle_with_single_prefix(monkeypatch):
    hebi, _, _ = make_hebi()

    monkeypatch.setattr(hebi, "getSortedCryList", lambda *args, **kwargs: [
        DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.005, 0.0))
    ])
    monkeypatch.setattr(hebi, "edgeCentering", lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz)

    called = {}
    def fake_doSingle(center_xyz, cond, phi_face, prefix):
        called["prefix"] = prefix
        called["center_xyz"] = center_xyz

    monkeypatch.setattr(hebi, "doSingle", fake_doSingle)

    cond = {
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "cry_min_size_um": 5.0,
        "ds_hbeam": 10.0,
    }

    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)

    assert n == 1
    assert called["prefix"] == "cry00_single"


def test_mainLoop_large_crystal_calls_doHelical_with_helical_prefix(monkeypatch):
    hebi, _, _ = make_hebi()

    monkeypatch.setattr(hebi, "getSortedCryList", lambda *args, **kwargs: [
        DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.050, 0.0))
    ])
    monkeypatch.setattr(hebi, "edgeCentering", lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz)

    called = {}
    def fake_doHelical(left_xyz, right_xyz, cond, phi_face, prefix):
        called["prefix"] = prefix
        called["left_xyz"] = left_xyz
        called["right_xyz"] = right_xyz

    monkeypatch.setattr(hebi, "doHelical", fake_doHelical)

    cond = {
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "cry_min_size_um": 5.0,
        "ds_hbeam": 10.0,
    }

    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)

    assert n == 1
    assert called["prefix"] == "cry00_hel"
