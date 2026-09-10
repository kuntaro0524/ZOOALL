import sys
import types
import logging
from pathlib import Path

# =========================
# パス設定
# =========================
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
# import前に重い依存だけダミー化
# KUMA は本物を使う
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
        self.trans = None
        self.exp_time = None
        self.camera_length = None
        self.scan_condition = None
        self.schedule_path = None

    def setTrans(self, v):
        self.trans = v

    def setAttIdx(self, v):
        self.att_idx = v

    def setPrefix(self, v):
        self.prefix = v

    def setCrystalID(self, v):
        self.crystal_id = v

    def setWL(self, v):
        self.wl = v

    def setBeamsizeIndex(self, v):
        self.beamsize_index = v

    def setExpTime(self, v):
        self.exp_time = v

    def setCameraLength(self, v):
        self.camera_length = v

    def setScanCondition(self, a, b, c):
        self.scan_condition = (a, b, c)

    def setDir(self, v):
        self.dir = v

    def setShutterlessOn(self):
        pass

    def makeMultiDoseSlicing(self, schedule_path, glist, ntimes=1):
        self.schedule_path = schedule_path
        self.glist = glist
        self.ntimes = ntimes

    def makeMultiDoseSlicingAtSamePoint(self, schedule_path, glist, ntimes=1):
        self.schedule_path = schedule_path
        self.glist = glist
        self.ntimes = ntimes


class DummyAttFactorClass:
    def checkThinnestAtt(self, wavelength, exp_time, best_transmission):
        # 実機都合の丸めはここではやらず、そのまま返す
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
        # y方向0.1 mm
        return [0.0, 0.1, 0.0]


class DummyScheduleBSSClass:
    def __init__(self, *args, **kwargs):
        self.trans = None
        self.exp_time = None
        self.camera_length = None
        self.schedule_file = None

    def setTrans(self, v):
        self.trans = v

    def setAttIdx(self, v):
        self.att_idx = v

    def setDir(self, v):
        self.dir = v

    def setDataName(self, v):
        self.data_name = v

    def setBeamsizeIndex(self, v):
        self.beamsize_index = v

    def setOffset(self, v):
        self.offset = v

    def setWL(self, v):
        self.wl = v

    def setExpTime(self, v):
        self.exp_time = v

    def setCameraLength(self, v):
        self.camera_length = v

    def setAdvanced(self, *args):
        self.advanced = args

    def setAdvancedVector(self, *args):
        self.vector = args

    def setScanCondition(self, *args):
        self.scan_condition = args

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


def make_bare_lm():
    lm = LMModule.LoopMeasurement.__new__(LMModule.LoopMeasurement)
    lm.beamline = "BL32XU"
    lm.beamsizeconf = DummyBeamSizeConfClass()
    lm.isBeamsizeIndexOnScheduleFile = True
    lm.wavelength = 1.0
    lm.multi_dir = "/tmp/data"
    lm.prepPath = lambda path: None
    lm.logger = logging.getLogger("accept.loopmeasurement")
    return lm


def main():
    logging.basicConfig(level=logging.INFO)

    lm = make_bare_lm()
    flux = 1.0e12

    print("=== SINGLE ===")
    cond_single = {
        "sample_name": "SAMPLE_SINGLE",
        "mode": "single",
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
    sch_single = lm.genSingleSchedule(
        phi_start=0.0,
        phi_end=10.0,
        cenxyz=(0.0, 0.0, 0.0),
        cond=cond_single,
        flux=flux,
        prefix="single_accept",
        same_point=True,
    )
    print("single schedule:", sch_single)

    print("=== MULTI ===")
    cond_multi = {
        "sample_name": "SAMPLE_MULTI",
        "mode": "multi",
        "dose_ds": 5.0,
        "dist_ds": 130.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "reduced_fact": 1.0,
        "ntimes": 2,
    }
    sch_multi = lm.genMultiSchedule(
        phi_mid=20.0,
        glist=[(0.0, 0.0, 0.0)],
        cond=cond_multi,
        flux=flux,
        prefix="multi_accept",
        same_point=False,
    )
    print("multi schedule:", sch_multi)

    print("=== HELICAL ===")
    cond_helical = {
        "sample_name": "SAMPLE_HELICAL",
        "mode": "helical",
        "dose_ds": 5.0,
        "dist_ds": 140.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "reduced_fact": 1.0,
        "ntimes": 1,
    }
    sch_helical = lm.genHelical(
        startphi=0.0,
        endphi=10.0,
        left_xyz=(0.0, 0.0, 0.0),
        right_xyz=(0.0, 0.1, 0.0),
        prefix="helical_accept",
        flux=flux,
        cond=cond_helical,
    )
    print("helical schedule:", sch_helical)

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
