import sys
import types
import pytest
from UserESA import DoseDistanceHandler
import logging


def _install_stub_modules():
    stub_names = [
        "Zoo",
        "AttFactor",
        "LoopMeasurement",
        "BeamsizeConfig",
        "StopWatch",
        "Device",
        "DumpRecover",
        "AnaHeatmap",
        "ESA",
        "KUMA",
        "CrystalList",
        "MyDate",
        "DiffscanMaster",
        "cv2",
        "html_log_maker",
    ]
    for name in stub_names:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    sys.modules["html_log_maker"].ZooHtmlLog = object

    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")
    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")
    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])

    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod

    if "ErrorCode" not in sys.modules:
        err_mod = types.ModuleType("ErrorCode")

        class _ECItem:
            def __init__(self, v):
                self.v = v

            def to_db_value(self):
                return self.v

        class ErrorCode:
            SUCCESS = _ECItem(1)
            UNKNOWN_MODE = _ECItem(8001)
            CENTERING_FAILURE = _ECItem(1001)
            RASTER_SCAN_FAILURE_MEASUREMENT = _ECItem(2001)
            RASTER_SCAN_FAILURE_ANALYSIS = _ECItem(2002)
            RASTER_SCAN_NO_CRYSTAL = _ECItem(2003)
            RASTER_SCAN_UNKNOWN_ERROR = _ECItem(2004)
            DATA_COLLECTION_UNKNOWN_ERROR = _ECItem(3003)
            DATA_COLLECTION_NO_CRYSTAL = _ECItem(3002)
            SPACE_ACCIDENT = _ECItem(9999)
            SPACE_WARNING_LHEAD_PUSHED = _ECItem(9002)
            SPACE_WARNING_SUSPECTED = _ECItem(9001)
            SPACE_WARNING_ROTATE_TOO_MUCH = _ECItem(9003)
            SPACE_UNKNOWN_ACCIDENT = _ECItem(9998)

        err_mod.ErrorCode = ErrorCode
        sys.modules["ErrorCode"] = err_mod


_install_stub_modules()

from ZooMyException import ZooMyException
import HEBI as hebi_module
import ZooNavigator as zn_module
from HEBI import HEBI
from ZooNavigator import ZooNavigator


def _dummy_logger():
    return types.SimpleNamespace(
        info=lambda *a, **k: None,
        debug=lambda *a, **k: None,
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )


class DummyZoo:
    def __init__(self, records):
        self.records = records

    def doDataCollection(self, schedule):
        self.records["dc"].append(schedule)

    def waitTillReady(self):
        self.records["wait"].append("ready")

    def doRaster(self, schedule):
        self.records["raster"].append(schedule)

    def mountSample(self, trayid, pinid):
        self.records["mount"].append((trayid, pinid))

    def getSampleInformation(self):
        self.records["sample_info"] += 1

    def getWavelength(self):
        return 1.0

    def setWavelength(self, wl):
        self.records["wavelength"].append(wl)

    def getBeamsize(self):
        return 1

    def setBeamsize(self, idx):
        self.records["beamsize"].append(idx)

    def dismountCurrentPin(self):
        self.records["dismount"].append("dismount")

    def skipSample(self):
        self.records["skip"].append("skip")

    def cleaning(self):
        self.records["cleaning"].append("cleaning")

    def waitSPACE(self):
        self.records["space"].append("waitSPACE")

    def exposeLN2(self, sec):
        self.records["ln2"].append(sec)

    def runScriptOnBSS(self, script):
        self.records["bss_script"].append(script)

class DummyLoopMeasurement:
    def __init__(self, blf=None, root_dir=".", prefix="pin"):
        import os
        self.prefix = prefix
        self.raster_dir = "/tmp/raster"
        os.makedirs(self.raster_dir, exist_ok=True)
        self.raster_start_phi = 0.0

    def prepDataCollection(self):
        return 0

    def setWavelength(self, wl):
        pass

    def closeCapture(self):
        pass

    def captureImage(self, name):
        pass

    def roughCentering(self, *args, **kwargs):
        return None

    def centering(self, *args, **kwargs):
        return (50.0, 100.0)

    def rasterMaster(self, *args, **kwargs):
        return ("dummy_raster_schedule", self.raster_dir)

    def genMultiSchedule(self, sphi, glist, cond, flux, prefix="single"):
        return {
            "kind": "multi",
            "prefix": prefix,
            "dose_ds": float(cond["dose_ds"]),
            "dist_ds": float(cond["dist_ds"]),
            "glist": glist,
            "flux": flux,
        }

    def genSingleSchedule(self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True):
        return {
            "kind": "single",
            "prefix": prefix,
            "dose_ds": float(cond["dose_ds"]),
            "dist_ds": float(cond["dist_ds"]),
        }

    def genHelical(self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond):
        return {
            "kind": "helical",
            "prefix": prefix,
            "dose_ds": float(cond["dose_ds"]),
            "dist_ds": float(cond["dist_ds"]),
        }

class DummyAnaHeatmap:
    def __init__(self, path):
        self.path = path

    def setMinMax(self, min_score, max_score):
        self.min_score = min_score
        self.max_score = max_score

    def searchPixelBunch(self, scan_id, naname_include=True):
        # collectSingle / HEBI edgeCentering 用
        return [(1.0, 0.025, 0.0)]

    def searchMulti(self, scan_id, cry_size_mm):
        return [(0.0, 0.025, 0.0)]


class DummyCrystalListForSingle:
    def __init__(self, arr):
        self.arr = arr

    def getBestCrystalCode(self):
        return (1.0, 2.0, 3.0)

    def getSortedPeakCodeList(self):
        return [(1.0, 2.0, 3.0)]


class DummyCrystalForHEBI:
    def __init__(self, peak=(1.0, 0.025, 0.0), left=(1.0, 0.050, 0.0), right=(1.0, 0.000, 0.0)):
        self._peak = peak
        self._left = left
        self._right = right

    def getRoughEdges(self):
        # mainLoop 用: y差 0.05 mm = 50 um → helical branch
        return self._left, self._right

    def getPeakCode(self):
        # edgeCentering / anaVscan 用
        return self._peak

    def getLLedge(self):
        return self._left

    def getRUedge(self):
        return self._right


class DummyCrystalListForHEBI:
    def __init__(self, arr):
        self.arr = arr

    def getSortedCrystalList(self):
        # HEBI.getSortedCryList() → mainLoop / anaVscan の両方で使われる
        # 1個だけ有効 crystal を返せば十分
        return [DummyCrystalForHEBI()]

    def getBestCrystalCode(self):
        return (1.0, 0.025, 0.0)


class DummyStopWatch:
    def setTime(self, *args, **kwargs):
        pass

    def calcTimeFrom(self, *args, **kwargs):
        return 0.0


class DummyBLFactory:
    def __init__(self, records):
        self.zoo = DummyZoo(records)
        self.ms = types.SimpleNamespace()
        self.device = types.SimpleNamespace(
            zoom=types.SimpleNamespace(zoomOut=lambda: None, move=lambda x: None),
            gonio=types.SimpleNamespace(
                moveXYZPhi=lambda *a, **k: None,
                getXYZmm=lambda: (0.0, 0.0, 0.0),
                getXYZPhi=lambda: (0.0, 0.0, 0.0, 0.0),
                rotatePhi=lambda *a, **k: None,
            ),
            capture=types.SimpleNamespace(capture=lambda *a, **k: None, disconnect=lambda: None),
            prepCentering=lambda *a, **k: None,
            measureFlux=lambda: 1.0e12,
        )


def _base_cond(mode="single", dose_list="", dist_list=""):
    return {
        "root_dir": "/tmp/zoo_test",
        "o_index": 0,
        "p_index": 0,
        "zoo_samplepin_id": 310,
        "mode": mode,
        "puckid": "CPS4474",
        "pinid": 7,
        "sample_name": "sample",
        "wavelength": 1.0,
        "raster_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "att_raster": 10.0,
        "hebi_att": 10.0,
        "exp_raster": 0.02,
        "dist_raster": 300.0,
        "loopsize": 200.0,
        "score_min": 10,
        "score_max": 200,
        "maxhits": 5,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "ds_vbeam": 10.0,
        "ds_hbeam": 10.0,
        "exp_ds": 0.02,
        "dist_ds": 120.0,
        "dose_ds": 10.0,
        "offset_angle": 0.0,
        "reduced_fact": 1.0,
        "ntimes": 1,
        "meas_name": "test",
        "cry_min_size_um": 10.0,
        "cry_max_size_um": 100.0,
        "raster_roi": 0,
        "ln2_flag": 0,
        "cover_scan_flag": 0,
        "zoomcap_flag": 0,
        "warm_time": 0.0,
        "dose_list": dose_list,
        "dist_list": dist_list,
    }


@pytest.fixture
def patch_common(monkeypatch):
    monkeypatch.setattr(zn_module, "LoopMeasurement", types.SimpleNamespace(LoopMeasurement=DummyLoopMeasurement))
    monkeypatch.setattr(zn_module, "AnaHeatmap", types.SimpleNamespace(AnaHeatmap=DummyAnaHeatmap))
    monkeypatch.setattr(zn_module, "CrystalList", types.SimpleNamespace(CrystalList=DummyCrystalListForSingle))
    monkeypatch.setattr(zn_module, "BeamsizeConfig", types.SimpleNamespace(BeamsizeConfig=lambda: types.SimpleNamespace(
        getBeamIndexHV=lambda h, v: 1,
        getFluxAtWavelength=lambda h, v, wl: 1.0e12,
    )))
    monkeypatch.setattr(zn_module, "BSSconfig", types.SimpleNamespace(BSSconfig=lambda: types.SimpleNamespace(
        getCmount=lambda: (0.0, 0.0, 0.0)
    )))
    monkeypatch.setattr(zn_module, "time", types.SimpleNamespace(sleep=lambda x: None))

    # HEBI 側
    monkeypatch.setattr(hebi_module, "AnaHeatmap", types.SimpleNamespace(AnaHeatmap=DummyAnaHeatmap))
    monkeypatch.setattr(hebi_module, "CrystalList", types.SimpleNamespace(CrystalList=DummyCrystalListForHEBI))
    monkeypatch.setattr(hebi_module, "numpy", __import__("numpy"))

def _make_znav(records):
    blf = DummyBLFactory(records)
    z = object.__new__(ZooNavigator)
    z.blf = blf
    z.zoo = blf.zoo
    z.ms = blf.ms
    z.dev = blf.device
    z.logger = _dummy_logger()
    z.stopwatch = DummyStopWatch()
    z.dump_recov = types.SimpleNamespace(checkAndRecover=lambda *a, **k: True)
    z.recoverOption = False
    z.backimg = "dummy.ppm"
    z.config_file = "dummy.conf"
    z.backimage_dir = "/tmp"
    z.isECHA = True
    z.beamline = "BL32XU"
    z.back_mean_thresh = 10
    z.att = types.SimpleNamespace()
    z.limit_of_vert_velocity = 400.0
    z.isOpenDPfile = True
    z.data_proc_file = types.SimpleNamespace(write=lambda *a, **k: None, flush=lambda: None)
    z.isDPheader = False
    z.sx = 0.0
    z.sy = 0.0
    z.sz = 0.0
    z.mx = 0.0
    z.my = 0.0
    z.mz = 0.0
    z.phosec_meas = 1.0e12
    z.is_renew_db = False
    z.isCaptured = True
    z.helical_debug = False
    z.meas_beamh_list = []
    z.meas_beamv_list = []
    z.meas_flux_list = []
    z.meas_wavelength_list = []
    z.needMeasureFlux = False
    z.doesBSSchangeBeamsize = True
    z.num_pins = 0
    z.n_pins_for_cleaning = 16
    z.cleaning_interval_hours = 9999.0
    z.time_for_elongation = 0.0
    z.isZoomCapture = False
    z.time_limit_ds = 9999.0
    z.isSpecialRasterStep = False
    z.beamsize_thresh_special_raster = 50.0
    z.special_raster_step = 25.0
    z.isDark = False

    # 追加: direct collectHelical / collectSingle 用
    z.lm = DummyLoopMeasurement(prefix="direct")
    z.rheight = 100.0
    z.rwidth = 100.0
    z.center_xyz = (0.0, 0.0, 0.0)

    z.echa_esa = types.SimpleNamespace(
        isSkipped=lambda zoo_samplepin_id: False,
        postResult=lambda zoo_samplepin_id, payload: records["post"].append((zoo_samplepin_id, payload)),
        setDone=lambda p_index, zoo_samplepin_id, value: records["done"].append((p_index, zoo_samplepin_id, value)),
    )
    return z

def test_collectHelical_smoke_large_crystal_loops(patch_common, monkeypatch):
    records = {
        "dc": [],
        "raster": [],
        "wait": [],
        "mount": [],
        "sample_info": 0,
        "wavelength": [],
        "beamsize": [],
        "dismount": [],
        "skip": [],
        "cleaning": [],
        "space": [],
        "ln2": [],
        "bss_script": [],
        "post": [],
        "done": [],
    }

    monkeypatch.setattr(
        hebi_module.HEBI,
        "edgeCentering",
        lambda self, cond, phi_face, rough_xyz, LorR="Left", cry_index=0:
            (1.0, 0.050, 0.0) if LorR == "Left" else (1.0, 0.000, 0.0)
    )

    z = _make_znav(records)

    cond = _base_cond(
        mode="helical",
        dose_list="[1, 5, 10]",
        dist_list="[120, 110, 100]",
    )

    z.collectHelical("CPS4474", 7, "CPS4474-07", cond, sphi=0.0)

    helical_dc = [x for x in records["dc"] if x["kind"] == "helical"]
    assert len(helical_dc) == 3
    assert [(x["dose_ds"], x["dist_ds"]) for x in helical_dc] == [
        (1.0, 120.0),
        (5.0, 110.0),
        (10.0, 100.0),
    ]


def test_processLoop_smoke_single_echa_path(patch_common):
    records = {
        "dc": [],
        "raster": [],
        "wait": [],
        "mount": [],
        "sample_info": 0,
        "wavelength": [],
        "beamsize": [],
        "dismount": [],
        "skip": [],
        "cleaning": [],
        "space": [],
        "ln2": [],
        "bss_script": [],
        "post": [],
        "done": [],
    }

    z = _make_znav(records)
    cond = _base_cond(
        mode="single",
        dose_list="[1, 5]",
        dist_list="",
    )

    z.processLoop(cond, checkEnergyFlag=True)

    # mount された
    assert records["mount"] == [("CPS4474", 7)]

    # raster は少なくとも 2回
    assert len(records["raster"]) >= 2

    # data collection は dose_list の要素数ぶん
    multi_dc = [x for x in records["dc"] if x["kind"] == "multi"]
    assert len(multi_dc) == 2
    assert [(x["dose_ds"], x["dist_ds"]) for x in multi_dc] == [
        (1.0, 120.0),
        (5.0, 120.0),
    ]

    # ECHA result post が走っている
    posted_keys = []
    for _, payload in records["post"]:
        for row in payload.get("data", []):
            posted_keys.extend(row.keys())

    assert "t_meas_start" in posted_keys
    assert "isMount" in posted_keys
    assert "isRaster" in posted_keys
    assert "isDS" in posted_keys

    # 完了更新
    assert records["done"][-1] == (0, 310, 1)

def test_helical_failure_sets_error(patch_common, monkeypatch):
    records = {
        "dc": [],
        "raster": [],
        "wait": [],
        "mount": [],
        "sample_info": 0,
        "wavelength": [],
        "beamsize": [],
        "dismount": [],
        "skip": [],
        "cleaning": [],
        "space": [],
        "ln2": [],
        "bss_script": [],
        "post": [],
        "done": [],
    }

    # helical の途中で失敗させる
    monkeypatch.setattr(
        hebi_module.HEBI,
        "mainLoop",
        lambda self, raspath, scan_id, sphi, cond, precise_face_scan=False:
            (_ for _ in ()).throw(Exception("helical failed"))
    )

    z = _make_znav(records)
    cond = _base_cond(mode="helical")

    z.collectHelical("CPS4474", 7, "CPS4474-07", cond, sphi=0.0)

    # collectHelical except 節で error 登録されるはず
    assert records["done"][-1] == (0, 310, 3003)

    posted_keys = []
    for _, payload in records["post"]:
        for row in payload.get("data", []):
            posted_keys.extend(row.keys())

    assert "meas_record" in posted_keys
    assert "t_ds_end" in posted_keys
    assert "t_meas_end" in posted_keys

def test_pad_lists_by_policy_truncate_dist_list():
    h = DoseDistanceHandler(logger=logging.getLogger("test"))
    dose, dist = h._pad_lists_by_policy([0.1, 1.0], [300.0, 200.0, 150.0])
    assert dose == [0.1, 1.0]
    assert dist == [300.0, 200.0]

def test_pad_lists_by_policy_short_dist_list_raises():
    h = DoseDistanceHandler(logger=logging.getLogger("test"))
    with pytest.raises(ValueError):
        h._pad_lists_by_policy([0.1, 1.0, 1.0], [300.0, 200.0])

def test_kuma_helical_consistency(kuma_env):
    kuma = kuma_env

    cond = {
        "dose_ds": 10.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "total_osc": 360.0,
    }

    flux = 1e12
    dist_vec = 0.1  # mm

    exp_time, trans = kuma.getBestCondsHelical(cond, flux, dist_vec)

    dose = kuma.getDose(
        cond["ds_hbeam"],
        cond["ds_vbeam"],
        flux * trans,
        12.0,
        exp_time
    )

    assert dose > 0