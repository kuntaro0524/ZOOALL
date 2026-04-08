import sys
import types
import logging
import pytest


def install_dummy_module(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ---- import前に必要なダミークラスを定義 ----

class DummyZooMyException(Exception):
    pass


class DummyMultiCrystalImportClass:
    pass


class DummyScheduleBSSImportClass:
    pass


class DummyAttFactorImportClass:
    pass


class DummyGonioVecImportClass:
    pass


# ---- LoopMeasurement import 前に重い依存をダミー化 ----

install_dummy_module("ZooMyException", ZooMyException=DummyZooMyException)
install_dummy_module("INOCC")
install_dummy_module("RasterSchedule")
install_dummy_module("MultiCrystal", MultiCrystal=DummyMultiCrystalImportClass)
install_dummy_module("AttFactor", AttFactor=DummyAttFactorImportClass)
install_dummy_module("Beamsize")
install_dummy_module("BeamsizeConfig")
install_dummy_module("GonioVec", GonioVec=DummyGonioVecImportClass)
install_dummy_module("ScheduleBSS", ScheduleBSS=DummyScheduleBSSImportClass)
install_dummy_module("CrystalSpot")
install_dummy_module("DirectoryProc")

import LoopMeasurement as LMModule


class DummyBeamSizeConf:
    def getBeamIndexHV(self, h, v):
        return 7


class DummyMultiCrystal:
    def __init__(self):
        self.exp_time = None
        self.trans = None
        self.att_idx = None
        self.camera_length = None
        self.scan_condition = None
        self.dir = None
        self.prefix = None
        self.crystal_id = None
        self.wl = None
        self.beamsize_index = None
        self.same_point_called = False
        self.multi_called = False

    def setTrans(self, value):
        self.trans = value

    def setAttIdx(self, value):
        self.att_idx = value

    def setPrefix(self, value):
        self.prefix = value

    def setCrystalID(self, value):
        self.crystal_id = value

    def setWL(self, value):
        self.wl = value

    def setBeamsizeIndex(self, value):
        self.beamsize_index = value

    def setExpTime(self, value):
        self.exp_time = value

    def setCameraLength(self, value):
        self.camera_length = value

    def setScanCondition(self, start_phi, end_phi, osc_width):
        self.scan_condition = (start_phi, end_phi, osc_width)

    def setDir(self, value):
        self.dir = value

    def setShutterlessOn(self):
        pass

    def makeMultiDoseSlicing(self, schedule_path, glist, ntimes=1):
        self.multi_called = True
        self.schedule_path = schedule_path
        self.glist = glist
        self.ntimes = ntimes

    def makeMultiDoseSlicingAtSamePoint(self, schedule_path, glist, ntimes=1):
        self.same_point_called = True
        self.schedule_path = schedule_path
        self.glist = glist
        self.ntimes = ntimes


class DummyAttFactor:
    def checkThinnestAtt(self, wavelength, exp_time, best_transmission):
        return exp_time, best_transmission

    def getBestAtt(self, wavelength, best_transmission):
        return 100.0

    def getAttIndexConfig(self, thick):
        return 3


class DummyScheduleBSS:
    def __init__(self):
        self.exp_time = None
        self.trans = None
        self.att_idx = None
        self.dir = None
        self.data_name = None
        self.beamsize_index = None
        self.offset = None
        self.wl = None
        self.camera_length = None
        self.advanced = None
        self.vector = None
        self.scan_condition = None
        self.made = False
        self.made_multi = False

    def setTrans(self, value):
        self.trans = value

    def setAttIdx(self, value):
        self.att_idx = value

    def setDir(self, value):
        self.dir = value

    def setDataName(self, value):
        self.data_name = value

    def setBeamsizeIndex(self, value):
        self.beamsize_index = value

    def setOffset(self, value):
        self.offset = value

    def setWL(self, value):
        self.wl = value

    def setExpTime(self, value):
        self.exp_time = value

    def setCameraLength(self, value):
        self.camera_length = value

    def setAdvanced(self, n_irrad, step_length, nframes_per_point):
        self.advanced = (n_irrad, step_length, nframes_per_point)

    def setAdvancedVector(self, left_xyz, right_xyz):
        self.vector = (left_xyz, right_xyz)

    def setScanCondition(self, startphi, endphi, stepphi):
        self.scan_condition = (startphi, endphi, stepphi)

    def make(self, schedule_file):
        self.made = True
        self.schedule_file = schedule_file

    def makeMulti(self, schedule_file, ntimes):
        self.made_multi = True
        self.schedule_file = schedule_file
        self.ntimes = ntimes


class DummyGonioVec:
    def makeLineVec(self, left_xyz, right_xyz):
        return [0.0, 0.1, 0.0]


class DummyKUMAForSingle:
    def getBestCondsSingle(self, cond, flux):
        return 0.015, 0.5


class DummyKUMAForMulti:
    def getBestCondsMulti(self, cond, flux):
        return 0.018, 0.4


class DummyKUMAForHelical:
    def getBestCondsHelical(self, cond, flux, dist_vec):
        return 0.022, 0.3


@pytest.fixture
def bare_lm(tmp_path):
    lm = LMModule.LoopMeasurement.__new__(LMModule.LoopMeasurement)
    lm.beamline = "BL32XU"
    lm.beamsizeconf = DummyBeamSizeConf()
    lm.isBeamsizeIndexOnScheduleFile = True
    lm.wavelength = 1.0
    lm.multi_dir = str(tmp_path / "data")
    lm.prepPath = lambda path: None
    lm.logger = logging.getLogger("test.loopmeasurement")
    return lm


def test_genSingleSchedule_uses_kuma_result(monkeypatch, bare_lm):
    created = {}

    def fake_mc_factory():
        obj = DummyMultiCrystal()
        created["mc"] = obj
        return obj

    monkeypatch.setattr(LMModule.MultiCrystal, "MultiCrystal", fake_mc_factory)
    monkeypatch.setattr(LMModule.AttFactor, "AttFactor", DummyAttFactor)
    monkeypatch.setattr(LMModule.KUMA, "KUMA", DummyKUMAForSingle)

    cond = {
        "sample_name": "SAMPLE1",
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "dist_ds": 120.0,
        "osc_width": 0.1,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "dose_ds": 5.0,
        "reduced_fact": 1.0,
        "ntimes": 1,
        "mode": "single",
    }

    schedule = bare_lm.genSingleSchedule(
        phi_start=0.0,
        phi_end=10.0,
        cenxyz=(0.0, 0.0, 0.0),
        cond=cond,
        flux=1.0e12,
        prefix="single_test",
        same_point=True,
    )

    mc = created["mc"]
    assert schedule.endswith("/single.sch")
    assert mc.exp_time == pytest.approx(0.015)
    assert mc.trans == pytest.approx(50.0)
    assert mc.camera_length == 120.0
    assert mc.scan_condition == (0.0, 10.0, 0.1)
    assert mc.same_point_called is True


def test_genMultiSchedule_uses_kuma_result(monkeypatch, bare_lm):
    created = {}

    def fake_mc_factory():
        obj = DummyMultiCrystal()
        created["mc"] = obj
        return obj

    monkeypatch.setattr(LMModule.MultiCrystal, "MultiCrystal", fake_mc_factory)
    monkeypatch.setattr(LMModule.AttFactor, "AttFactor", DummyAttFactor)
    monkeypatch.setattr(LMModule.KUMA, "KUMA", DummyKUMAForMulti)

    cond = {
        "sample_name": "SAMPLE2",
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "dist_ds": 130.0,
        "osc_width": 0.1,
        "total_osc": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "dose_ds": 5.0,
        "reduced_fact": 1.0,
        "ntimes": 2,
        "mode": "multi",
    }

    schedule = bare_lm.genMultiSchedule(
        phi_mid=20.0,
        glist=[(0.0, 0.0, 0.0)],
        cond=cond,
        flux=1.0e12,
        prefix="multi_test",
        same_point=False,
    )

    mc = created["mc"]
    assert schedule.endswith("/multi.sch")
    assert mc.exp_time == pytest.approx(0.018)
    assert mc.trans == pytest.approx(40.0)
    assert mc.camera_length == 130.0
    assert mc.multi_called is True


def test_genHelical_uses_kuma_result(monkeypatch, bare_lm):
    created = {}

    def fake_sch_factory():
        obj = DummyScheduleBSS()
        created["sch"] = obj
        return obj

    monkeypatch.setattr(LMModule.ScheduleBSS, "ScheduleBSS", fake_sch_factory)
    monkeypatch.setattr(LMModule.GonioVec, "GonioVec", DummyGonioVec)
    monkeypatch.setattr(LMModule.AttFactor, "AttFactor", DummyAttFactor)
    monkeypatch.setattr(LMModule.KUMA, "KUMA", DummyKUMAForHelical)

    cond = {
        "sample_name": "SAMPLE3",
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "dist_ds": 140.0,
        "osc_width": 0.1,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "dose_ds": 5.0,
        "reduced_fact": 1.0,
        "ntimes": 1,
        "mode": "helical",
    }

    schedule = bare_lm.genHelical(
        startphi=0.0,
        endphi=10.0,
        left_xyz=(0.0, 0.0, 0.0),
        right_xyz=(0.0, 0.1, 0.0),
        prefix="heli_test",
        flux=1.0e12,
        cond=cond,
    )

    sch = created["sch"]
    assert schedule.endswith("/heli_test.sch")
    assert sch.exp_time == pytest.approx(0.022)
    assert sch.trans == pytest.approx(30.0)
    assert sch.camera_length == 140.0
    assert sch.made is True

def test_exp_time_changes_with_flux():
    from KUMA import KUMA

    kuma = KUMA()

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

    t1, _ = kuma.getBestCondsSingle(cond, flux=1e11)
    t2, _ = kuma.getBestCondsSingle(cond, flux=1e12)

    assert t2 < t1
