import sys
import types
import logging


# =========================================================
# Stub modules
# =========================================================

def install_stub_module(name, attrs=None):
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
    install_stub_module("ZooMyException", {"ZooMyException": ZooMyException})
else:
    from ZooMyException import ZooMyException


# Generic empty modules
for name in [
    "Zoo", "AttFactor", "LoopMeasurement", "BeamsizeConfig", "StopWatch",
    "Device", "DumpRecover", "AnaHeatmap", "ESA", "KUMA", "CrystalList",
    "MyDate", "DiffscanMaster", "cv2"
]:
    if name not in sys.modules:
        install_stub_module(name)

# html_log_maker
if "html_log_maker" not in sys.modules:
    class ZooHtmlLog:
        pass
    install_stub_module("html_log_maker", {"ZooHtmlLog": ZooHtmlLog})

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

    install_stub_module("ErrorCode", {"ErrorCode": ErrorCode})

# Libs.BSSconfig
if "Libs" not in sys.modules:
    libs = install_stub_module("Libs")
else:
    libs = sys.modules["Libs"]

if "Libs.BSSconfig" not in sys.modules:
    class BSSconfig:
        def getCmount(self):
            return (0.0, 0.0, 0.0)

    bss_mod = install_stub_module("Libs.BSSconfig", {"BSSconfig": BSSconfig})
    setattr(libs, "BSSconfig", bss_mod)

# AnaHeatmap / CrystalList
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


# =========================================================
# Import target modules
# =========================================================

from HEBI import HEBI
from ZooNavigator import ZooNavigator


# =========================================================
# Dummy classes
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

    def genSingleSchedule(self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True):
        call = {
            "kind": "single",
            "prefix": prefix,
            "dose_ds": cond["dose_ds"],
            "dist_ds": cond["dist_ds"],
            "center_xyz": center_xyz,
        }
        self.single_calls.append(call)
        return call

    def genHelical(self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond):
        call = {
            "kind": "helical",
            "prefix": prefix,
            "dose_ds": cond["dose_ds"],
            "dist_ds": cond["dist_ds"],
            "left_xyz": left_xyz,
            "right_xyz": right_xyz,
        }
        self.helical_calls.append(call)
        return call

    def genMultiSchedule(self, sphi, glist, cond, flux, prefix="multi"):
        call = {
            "kind": "multi",
            "prefix": prefix,
            "dose_ds": cond["dose_ds"],
            "dist_ds": cond["dist_ds"],
            "glist": glist,
        }
        self.multi_calls.append(call)
        return call

    def rasterMaster(self, *args, **kwargs):
        return ("dummy_schedule", "dummy_raster_path")

    def closeCapture(self):
        pass


class DummyStopWatch:
    pass


class DummyCrystal:
    def __init__(self, rpos, lpos):
        self._rpos = rpos
        self._lpos = lpos

    def getRoughEdges(self):
        return self._rpos, self._lpos


# =========================================================
# Factory helpers
# =========================================================

def make_hebi():
    logger = logging.getLogger("ZOO.HEBI")
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    zoo = DummyZoo()
    lm = DummyLM()
    sw = DummyStopWatch()
    hebi = HEBI(zoo, lm, sw, phosec=1.23e12)
    return hebi, zoo, lm


def make_zn():
    zn = ZooNavigator.__new__(ZooNavigator)
    zn.logger = logging.getLogger("ZOO.ZooNavigator")
    zn.logger.handlers.clear()
    zn.logger.addHandler(logging.StreamHandler())
    zn.logger.setLevel(logging.INFO)
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
# Printers
# =========================================================

def print_title(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_schedule_calls(lm):
    if lm.single_calls:
        print("[single schedules]")
        for c in lm.single_calls:
            print(f"  prefix={c['prefix']}, dose_ds={c['dose_ds']}, dist_ds={c['dist_ds']}")
    if lm.helical_calls:
        print("[helical schedules]")
        for c in lm.helical_calls:
            print(f"  prefix={c['prefix']}, dose_ds={c['dose_ds']}, dist_ds={c['dist_ds']}")
    if lm.multi_calls:
        print("[multi schedules]")
        for c in lm.multi_calls:
            print(f"  prefix={c['prefix']}, dose_ds={c['dose_ds']}, dist_ds={c['dist_ds']}")


# =========================================================
# Simulation cases
# =========================================================

def simulate_hebi_getDoseDistList():
    hebi, _, _ = make_hebi()

    cases = [
        {
            "name": "A1: normal single condition",
            "cond": {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": ""},
        },
        {
            "name": "A2: dose_list only",
            "cond": {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": ""},
        },
        {
            "name": "A3: dose_list + dist_list",
            "cond": {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": "[130, 140]"},
        },
        {
            "name": "A4: dist_list only (invalid)",
            "cond": {"dose_ds": "10", "dist_ds": "125", "dose_list": "", "dist_list": "[130, 140]"},
        },
        {
            "name": "A5: length mismatch (invalid)",
            "cond": {"dose_ds": "10", "dist_ds": "125", "dose_list": "[1, 2]", "dist_list": "[130]"},
        },
    ]

    print_title("HEBI.getDoseDistList simulation")
    for case in cases:
        print(f"\n--- {case['name']} ---")
        try:
            out = hebi.getDoseDistList(case["cond"])
            print("result:", out)
        except Exception as e:
            print("ERROR:", e)


def simulate_hebi_mainLoop_small_large():
    print_title("HEBI.mainLoop branching simulation")

    # Small crystal -> single
    hebi, _, lm = make_hebi()
    hebi.getSortedCryList = lambda *a, **k: [
        DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.005, 0.0))  # 5 um
    ]
    hebi.edgeCentering = lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz

    cond_small = {
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "cry_min_size_um": 5.0,
        "ds_hbeam": 10.0,
        "total_osc": 10.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1, 2]",
        "dist_list": "[130, 140]",
    }

    print("\n--- B1: small crystal -> single ---")
    hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond_small, precise_face_scan=False)
    print_schedule_calls(lm)

    # Large crystal -> helical
    hebi2, _, lm2 = make_hebi()
    hebi2.getSortedCryList = lambda *a, **k: [
        DummyCrystal((0.0, 0.000, 0.0), (0.0, 0.050, 0.0))  # 50 um
    ]
    hebi2.edgeCentering = lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz

    cond_large = {
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "cry_min_size_um": 5.0,
        "ds_hbeam": 10.0,
        "total_osc": 10.0,
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "[1, 2]",
        "dist_list": "[130, 140]",
    }

    print("\n--- B2: large crystal -> helical ---")
    hebi2.mainLoop("dummy_path", "dummy_prefix", 30.0, cond_large, precise_face_scan=False)
    print_schedule_calls(lm2)


def simulate_zn_single_loop():
    zn = make_zn()

    print_title("ZooNavigator single-loop simulation")

    cases = [
        {
            "name": "C1: single + dose_list/dist_list",
            "cond": {
                "mode": "single",
                "dose_ds": 10.0,
                "dist_ds": 125.0,
                "dose_list": "[1,2]",
                "dist_list": "[100,110]",
            }
        },
        {
            "name": "C2: single + dose_list only",
            "cond": {
                "mode": "single",
                "dose_ds": 10.0,
                "dist_ds": 125.0,
                "dose_list": "[1,2]",
                "dist_list": "",
            }
        },
        {
            "name": "C3: ssrox + multiple dose_list (invalid)",
            "cond": {
                "mode": "ssrox",
                "dose_ds": 10.0,
                "dist_ds": 125.0,
                "dose_list": "[1,2]",
                "dist_list": "",
            }
        },
    ]

    for case in cases:
        print(f"\n--- {case['name']} ---")
        try:
            dc_list = zn._build_dc_condition_list(case["cond"])
            print("expanded conditions:", dc_list)

            if case["cond"]["mode"] == "single":
                zn.lm = DummyLM()
                zn._run_single_dc_loop(
                    case["cond"],
                    sphi=30.0,
                    glist=[(0.0, 0.0, 0.0)],
                    flux=1.23e12,
                    data_prefix="single"
                )
                print_schedule_calls(zn.lm)

        except Exception as e:
            print("ERROR:", e)


def main():
    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")

    simulate_hebi_getDoseDistList()
    simulate_hebi_mainLoop_small_large()
    simulate_zn_single_loop()


if __name__ == "__main__":
    main()
