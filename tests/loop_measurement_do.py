# loop_measurement_do.py
import sys
import types
import logging
from pathlib import Path

# --- パス設定 ---
ROOT = Path("/Users/kuntaro/kundev/zooall_echa")
KUNPY = Path("/Users/kuntaro/kundev/kunpy")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(KUNPY))


def install_dummy_module(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# =========================
# import 前に重い依存をダミー化
# =========================

class DummyZooMyException(Exception):
    pass

class DummyINOCCClass:
    def __init__(self, *args, **kwargs):
        pass
    def init(self):
        pass

class DummyMultiCrystalClass:
    def __init__(self, *args, **kwargs):
        self.exp_time = None
        self.trans = None
    def setTrans(self, v): self.trans = v
    def setAttIdx(self, v): self.att_idx = v
    def setPrefix(self, v): self.prefix = v
    def setCrystalID(self, v): self.crystal_id = v
    def setWL(self, v): self.wl = v
    def setBeamsizeIndex(self, v): self.beamsize_index = v
    def setExpTime(self, v): self.exp_time = v
    def setCameraLength(self, v): self.camera_length = v
    def setScanCondition(self, a, b, c): self.scan_condition = (a, b, c)
    def setDir(self, v): self.dir = v
    def setShutterlessOn(self): pass
    def makeMultiDoseSlicing(self, *args, **kwargs): pass
    def makeMultiDoseSlicingAtSamePoint(self, *args, **kwargs): pass

class DummyAttFactorClass:
    def checkThinnestAtt(self, wavelength, exp_time, best_transmission):
        return exp_time, best_transmission
    def getBestAtt(self, wavelength, best_transmission):
        return 100.0
    def getAttIndexConfig(self, thick):
        return 3

class DummyBeamSizeConfClass:
    def getBeamIndexHV(self, h, v):
        return 7

class DummyGonioVecClass:
    def makeLineVec(self, left_xyz, right_xyz):
        return [0.0, 0.1, 0.0]

class DummyScheduleBSSClass:
    def __init__(self, *args, **kwargs):
        pass
    def setTrans(self, v): self.trans = v
    def setAttIdx(self, v): self.att_idx = v
    def setDir(self, v): self.dir = v
    def setDataName(self, v): self.data_name = v
    def setBeamsizeIndex(self, v): self.beamsize_index = v
    def setOffset(self, v): self.offset = v
    def setWL(self, v): self.wl = v
    def setExpTime(self, v): self.exp_time = v
    def setCameraLength(self, v): self.camera_length = v
    def setAdvanced(self, *args): self.advanced = args
    def setAdvancedVector(self, *args): self.vector = args
    def setScanCondition(self, *args): self.scan_condition = args
    def make(self, schedule_file):
        self.schedule_file = schedule_file
    def makeMulti(self, schedule_file, ntimes):
        self.schedule_file = schedule_file
        self.ntimes = ntimes

class DummyDirectoryProcClass:
    def __init__(self, *args, **kwargs):
        pass
    def makeRoundDir(self, *args, **kwargs):
        return "/tmp/scan00", 0


install_dummy_module("ZooMyException", ZooMyException=DummyZooMyException)
install_dummy_module("INOCC", INOCC=DummyINOCCClass)
install_dummy_module("RasterSchedule")
install_dummy_module("MultiCrystal", MultiCrystal=DummyMultiCrystalClass)
install_dummy_module("AttFactor", AttFactor=DummyAttFactorClass)
install_dummy_module("Beamsize")
install_dummy_module("BeamsizeConfig", BeamsizeConfig=DummyBeamSizeConfClass)
install_dummy_module("GonioVec", GonioVec=DummyGonioVecClass)
install_dummy_module("ScheduleBSS", ScheduleBSS=DummyScheduleBSSClass)
install_dummy_module("CrystalSpot")
install_dummy_module("DirectoryProc", DirectoryProc=DummyDirectoryProcClass)

# ここで初めて import
import LoopMeasurement as LMModule


class DummyKUMAForSingle:
    def getBestCondsSingle(self, cond, flux):
        return 0.015, 0.5


# KUMA も差し替え
LMModule.KUMA.KUMA = DummyKUMAForSingle

# =========================
# bare instance を作る
# =========================
lm = LMModule.LoopMeasurement.__new__(LMModule.LoopMeasurement)
lm.beamline = "BL32XU"
lm.beamsizeconf = DummyBeamSizeConfClass()
lm.isBeamsizeIndexOnScheduleFile = True
lm.wavelength = 1.0
lm.multi_dir = "/tmp/data"
lm.prepPath = lambda path: None
lm.logger = logging.getLogger("loop_measurement_do")

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

print("=== START ===")
schedule = lm.genSingleSchedule(
    phi_start=0.0,
    phi_end=10.0,
    cenxyz=(0.0, 0.0, 0.0),
    cond=cond,
    flux=1.0e12,
    prefix="single_test",
    same_point=True,
)
print("schedule =", schedule)
print("=== SUCCESS ===")
