import sys
import types
import logging
import pytest


# =========================================================
# Stub external modules required by ZooNavigator / HEBI
# =========================================================

def _install_stub_module(name, attrs=None):
    mod = types.ModuleType(name)
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ZooMyException
if "ZooMyException" not in sys.modules:
    class ZooMyException(Exception):
        pass
    _install_stub_module("ZooMyException", {"ZooMyException": ZooMyException})
else:
    from ZooMyException import ZooMyException


# Generic empty modules
for name in [
    "Zoo", "AttFactor", "LoopMeasurement", "BeamsizeConfig", "StopWatch",
    "Device", "DumpRecover", "AnaHeatmap", "ESA", "KUMA", "CrystalList",
    "MyDate", "DiffscanMaster", "cv2"
]:
    if name not in sys.modules:
        _install_stub_module(name)

# html_log_maker
if "html_log_maker" not in sys.modules:
    class ZooHtmlLog:
        pass
    _install_stub_module("html_log_maker", {"ZooHtmlLog": ZooHtmlLog})

# ErrorCode
if "ErrorCode" not in sys.modules:
    class _Code:
        def __init__(self, value):
            self._value = value
        def to_db_value(self):
            return self._value

    class ErrorCode:
        UNKNOWN_MODE = _Code(99901)
        DATA_COLLECTION_NO_CRYSTAL = _Code(50001)
        DATA_COLLECTION_UNKNOWN_ERROR = _Code(50002)
    _install_stub_module("ErrorCode", {"ErrorCode": ErrorCode})

# Libs.BSSconfig
if "Libs" not in sys.modules:
    libs = _install_stub_module("Libs")
else:
    libs = sys.modules["Libs"]

if "Libs.BSSconfig" not in sys.modules:
    class BSSconfig:
        def getCmount(self):
            return (0.0, 0.0, 0.0)
    bss_mod = _install_stub_module("Libs.BSSconfig", {"BSSconfig": BSSconfig})
    setattr(libs, "BSSconfig", bss_mod)

# HEBI dependency helpers
if "AnaHeatmap" in sys.modules:
    class AnaHeatmap:
        def __init__(self, *args, **kwargs):
            pass
        def setMinMax(self, *args, **kwargs):
            pass
        def searchPixelBunch(self, *args, **kwargs):
            return []
    sys.modules["AnaHeatmap"].AnaHeatmap = AnaHeatmap

if "CrystalList" in sys.modules:
    class CrystalList:
        def __init__(self, arr):
            self.arr = arr
        def getSortedCrystalList(self):
            return self.arr
        def getBestCrystalCode(self):
            return (0.0, 0.0, 0.0)
    sys.modules["CrystalList"].CrystalList = CrystalList

# Import current project files after stubbing
from HEBI import HEBI
import HEBI as HEBI_module
from ZooNavigator import ZooNavigator


# =========================================================
# Shared dummy classes
# =========================================================

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
        self.multi_calls = []
        self.closed = False

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

    def genMultiSchedule(self, sphi, glist, cond, flux, prefix="multi"):
        call = {
            "sphi": sphi,
            "glist": list(glist),
            "cond": cond.copy(),
            "flux": flux,
            "prefix": prefix,
        }
        self.multi_calls.append(call)
        return {"kind": "multi", "prefix": prefix, "cond": cond.copy()}

    def rasterMaster(self, *args, **kwargs):
        return ("dummy_schedule", "dummy_raster_path")

    def closeCapture(self):
        self.closed = True


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


def make_zn():
    zn = ZooNavigator.__new__(ZooNavigator)
    zn.logger = logging.getLogger("ZOO.ZooNavigator")
    zn.logger.handlers.clear()
    zn.logger.addHandler(logging.NullHandler())
    zn.logger.setLevel(logging.DEBUG)
    zn.zoo = DummyZoo()
    zn.lm = DummyLM()
    zn.stopwatch = DummyStopWatch()
    zn.phosec_meas = 1.23e12
    zn.rwidth = 50.0
    zn.rheight = 50.0
    zn.center_xyz = (0.0, 0.0, 0.0)
    zn.sx = 0.0
    zn.sy = 0.0
    zn.sz = 0.0
    zn.isSpecialRasterStep = False
    zn.data_proc_file = types.SimpleNamespace(write=lambda *a, **k: None, flush=lambda: None)
    zn.updateTime = lambda *a, **k: None
    zn.updateDBinfo = lambda *a, **k: None
    return zn


# =========================================================
# HEBI unit/integration tests
# =========================================================

class DummyCrystal:
    def __init__(self, rpos, lpos):
        self._rpos = rpos
        self._lpos = lpos

    def getRoughEdges(self):
        return self._rpos, self._lpos


def test_hebi_getDoseDistList_normal_case():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": ""}
    assert hebi.getDoseDistList(cond) == [(10.0, 125.0)]


def test_hebi_getDoseDistList_dose_and_dist():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": "[100, 110]"}
    assert hebi.getDoseDistList(cond) == [(1.0, 100.0), (2.0, 110.0)]


def test_hebi_getDoseDistList_rejects_dist_only():
    hebi, _, _ = make_hebi()
    cond = {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": "[100, 110]"}
    with pytest.raises(ZooMyException, match="dist_list only"):
        hebi.getDoseDistList(cond)


def test_hebi_doSingle_generates_unique_prefixes():
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
    assert len([c for c in zoo.calls if c[0] == "doDataCollection"]) == 2


def test_hebi_doHelical_generates_unique_prefixes():
    hebi, zoo, lm = make_hebi()
    cond = {
        "total_osc": 40.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1, 2]",
        "dist_list": "[130, 140]",
    }
    hebi.doHelical((0.0, 0.0, 0.0), (0.0, 0.1, 0.0), cond, phi_face=45.0, prefix="cry03_hel")
    assert [c["prefix"] for c in lm.helical_calls] == ["cry03_hel_00", "cry03_hel_01"]
    assert len([c for c in zoo.calls if c[0] == "doDataCollection"]) == 2


def test_hebi_mainLoop_small_crystal_calls_single_prefix(monkeypatch):
    hebi, _, _ = make_hebi()
    monkeypatch.setattr(hebi, "getSortedCryList", lambda *a, **k: [DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.005, 0.0))])
    monkeypatch.setattr(hebi, "edgeCentering", lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz)

    called = {}
    monkeypatch.setattr(hebi, "doSingle", lambda center_xyz, cond, phi_face, prefix: called.setdefault("prefix", prefix))

    cond = {"score_min": 10, "score_max": 200, "maxhits": 3, "cry_min_size_um": 5.0, "ds_hbeam": 10.0}
    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)
    assert n == 1
    assert called["prefix"] == "cry00_single"


def test_hebi_mainLoop_large_crystal_calls_helical_prefix(monkeypatch):
    hebi, _, _ = make_hebi()
    monkeypatch.setattr(hebi, "getSortedCryList", lambda *a, **k: [DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.050, 0.0))])
    monkeypatch.setattr(hebi, "edgeCentering", lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz)

    called = {}
    monkeypatch.setattr(hebi, "doHelical", lambda left_xyz, right_xyz, cond, phi_face, prefix: called.setdefault("prefix", prefix))

    cond = {"score_min": 10, "score_max": 200, "maxhits": 3, "cry_min_size_um": 5.0, "ds_hbeam": 10.0}
    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)
    assert n == 1
    assert called["prefix"] == "cry00_hel"


# =========================================================
# ZooNavigator tests using HEBI
# =========================================================

def test_zn_build_dc_condition_list_normal():
    zn = make_zn()
    cond = {"mode": "single", "dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": ""}
    out = zn._build_dc_condition_list(cond)
    assert out == [{"dose": 10.0, "dist": 125.0}]


def test_zn_build_dc_condition_list_dose_and_dist():
    zn = make_zn()
    cond = {"mode": "single", "dose_ds": "10", "dist_ds": "125", "dose_list": "[1,2]", "dist_list": "[100,110]"}
    out = zn._build_dc_condition_list(cond)
    assert out == [{"dose": 1.0, "dist": 100.0}, {"dose": 2.0, "dist": 110.0}]


def test_zn_build_dc_condition_list_rejects_dist_only():
    zn = make_zn()
    cond = {"mode": "single", "dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": "[100]"}
    with pytest.raises(ZooMyException, match="dist_list only"):
        zn._build_dc_condition_list(cond)


def test_zn_build_dc_condition_list_rejects_ssrox_multiple():
    zn = make_zn()
    cond = {"mode": "ssrox", "dose_ds": "10", "dist_ds": "125", "dose_list": "[1,2]", "dist_list": ""}
    with pytest.raises(ZooMyException, match="does not allow multiple"):
        zn._build_dc_condition_list(cond)


def test_zn_run_single_dc_loop_applies_each_condition():
    zn = make_zn()
    cond = {"mode": "single", "dose_ds": 10.0, "dist_ds": 125.0, "dose_list": "[1,2]", "dist_list": "[100,110]"}
    zn._run_single_dc_loop(cond, sphi=30.0, glist=[(0.0, 0.0, 0.0)], flux=1.23e12, data_prefix="single")

    prefixes = [c["prefix"] for c in zn.lm.multi_calls]
    doses = [c["cond"]["dose_ds"] for c in zn.lm.multi_calls]
    dists = [c["cond"]["dist_ds"] for c in zn.lm.multi_calls]

    assert prefixes == ["single", "single"]
    assert doses == [1.0, 2.0]
    assert dists == [100.0, 110.0]


def test_zn_collectHelical_passes_cond_to_hebi(monkeypatch):
    zn = make_zn()

    class FakeHEBI:
        last_cond = None

        def __init__(self, zoo, lm, stopwatch, flux):
            self.zoo = zoo
            self.lm = lm
            self.stopwatch = stopwatch
            self.flux = flux

        def getDoseDistList(self, cond):
            FakeHEBI.last_cond = cond.copy()
            return [(1.0, 130.0), (2.0, 140.0)]

        def mainLoop(self, raspath, scan_id, sphi, cond, precise_face_scan=False):
            FakeHEBI.last_cond = cond.copy()
            return 2

    monkeypatch.setattr(HEBI_module, "HEBI", FakeHEBI)

    cond = {
        "o_index": 0,
        "root_dir": "/tmp",
        "sample_name": "sample",
        "wavelength": 1.0,
        "mode": "helical",
        "raster_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1,2]",
        "dist_list": "[130,140]",
        "cry_min_size_um": 5.0,
        "hebi_att": 10.0,
        "exp_raster": 0.02,
        "total_osc": 10.0,
    }

    zn.collectHelical("PCK", 1, "PCK-01", cond, sphi=30.0)

    assert FakeHEBI.last_cond["dose_list"] == "[1,2]"
    assert FakeHEBI.last_cond["dist_list"] == "[130,140]"
