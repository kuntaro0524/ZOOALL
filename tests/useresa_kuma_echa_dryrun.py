"""
useresa_kuma_echa_dryrun.py

ECHA サーバーにだけ接続し、装置には接続しない dry-run スクリプト。

やること:
1. EXID から next pin または指定 pin の cond を取得
2. 取得した cond を 1 行 DataFrame にして UserESA の前処理に通す
   - setDefaults
   - addDistance
   - splitBeamsizeInfo
   - fillFlux
   - checkScanSpeed
   - defineScanCondition
   - modifyExposureConditions
   - validateDoseDist / checkDoseList
   ※ 実際にどのメソッドがあるかを見ながら順に呼ぶ
3. 前処理後の cond を使って、装置なしで schedule 相当ファイルを JSON として出力
   - single: ZooNavigator._build_dc_condition_list / _run_single_dc_loop
   - helical: HEBI.mainLoop
   - helical-small: HEBI.mainLoop の small crystal 分岐

注:
- KUMA は直接呼ばず、UserESA の dose 計算フローを通すことで間接的に利用する想定
- beamline.ini / ZOOCONFIGPATH / UserESA.py / ESAloaderAPI.py / ZooNavigator.py / HEBI.py が import 可能であること
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd


# ----------------------------------------------------------------------
# stubs for hardware-side dependencies
# ----------------------------------------------------------------------
def install_stub_module(name: str, attrs: dict | None = None):
    mod = types.ModuleType(name)
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


def ensure_external_stubs():
    if "ZooMyException" not in sys.modules:
        class ZooMyException(Exception):
            pass
        install_stub_module("ZooMyException", {"ZooMyException": ZooMyException})

    for name in [
        "Zoo", "AttFactor", "LoopMeasurement", "BeamsizeConfig", "StopWatch",
        "Device", "DumpRecover", "AnaHeatmap", "ESA", "CrystalList",
        "MyDate", "DiffscanMaster", "cv2"
    ]:
        if name not in sys.modules:
            install_stub_module(name)

    if "html_log_maker" not in sys.modules:
        class ZooHtmlLog:
            pass
        install_stub_module("html_log_maker", {"ZooHtmlLog": ZooHtmlLog})

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

    # minimal BeamsizeConfig stub only if real one is absent
    if "BeamsizeConfig" in sys.modules and not hasattr(sys.modules["BeamsizeConfig"], "BeamsizeConfig"):
        class _DummyBS:
            def getBeamIndexHV(self, h, v):
                return 1
        sys.modules["BeamsizeConfig"].BeamsizeConfig = _DummyBS


class DummyZoo:
    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild("DummyZoo")
        self.calls: List[Tuple[str, Any]] = []

    def doDataCollection(self, schedule):
        self.calls.append(("doDataCollection", schedule))
        self.logger.info(f"doDataCollection: {schedule}")

    def waitTillReady(self):
        self.calls.append(("waitTillReady", None))
        self.logger.info("waitTillReady")

    def doRaster(self, schedule):
        self.calls.append(("doRaster", schedule))
        self.logger.info(f"doRaster: {schedule}")


class DummyLM:
    def __init__(self, outdir: Path, logger: logging.Logger):
        self.outdir = outdir
        self.logger = logger.getChild("DummyLM")
        self.single_calls = []
        self.helical_calls = []
        self.multi_calls = []
        self.raster_calls = []

    def _write_schedule(self, filename: str, payload: dict) -> str:
        path = self.outdir / filename
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.logger.info(f"schedule written: {path}")
        return str(path)

    def genSingleSchedule(self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True):
        payload = {
            "kind": "single",
            "prefix": prefix,
            "start_phi": start_phi,
            "end_phi": end_phi,
            "center_xyz": center_xyz,
            "dose_ds": cond.get("dose_ds"),
            "dist_ds": cond.get("dist_ds"),
            "same_point": same_point,
            "mode": cond.get("mode"),
        }
        self.single_calls.append(payload)
        return self._write_schedule(f"{prefix}.single.json", payload)

    def genHelical(self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond):
        payload = {
            "kind": "helical",
            "prefix": prefix,
            "start_phi": start_phi,
            "end_phi": end_phi,
            "left_xyz": left_xyz,
            "right_xyz": right_xyz,
            "dose_ds": cond.get("dose_ds"),
            "dist_ds": cond.get("dist_ds"),
            "mode": cond.get("mode"),
        }
        self.helical_calls.append(payload)
        return self._write_schedule(f"{prefix}.helical.json", payload)

    def genMultiSchedule(self, sphi, glist, cond, flux, prefix="multi"):
        payload = {
            "kind": "multi",
            "prefix": prefix,
            "sphi": sphi,
            "glist": glist,
            "dose_ds": cond.get("dose_ds"),
            "dist_ds": cond.get("dist_ds"),
            "mode": cond.get("mode"),
            "flux": flux,
        }
        self.multi_calls.append(payload)
        return self._write_schedule(f"{prefix}.multi.json", payload)

    def rasterMaster(self, scan_id, scan_mode, center, vrange_um, hrange_um, vstep_um, hstep_um, phi, cond, isHEBI=False):
        payload = {
            "kind": "raster",
            "scan_id": scan_id,
            "scan_mode": scan_mode,
            "center": center,
            "vrange_um": vrange_um,
            "hrange_um": hrange_um,
            "vstep_um": vstep_um,
            "hstep_um": hstep_um,
            "phi": phi,
            "mode": cond.get("mode"),
            "isHEBI": isHEBI,
        }
        self.raster_calls.append(payload)
        schfile = self._write_schedule(f"{scan_id}.raster.json", payload)
        raspath = str(self.outdir / f"{scan_id}_raster")
        return schfile, raspath

    def closeCapture(self):
        self.logger.info("closeCapture")


class DummyStopWatch:
    pass


class DummyCrystal:
    def __init__(self, rpos, lpos):
        self._rpos = rpos
        self._lpos = lpos
    def getRoughEdges(self):
        return self._rpos, self._lpos


# ----------------------------------------------------------------------
# UserESA / KUMA path
# ----------------------------------------------------------------------
def normalize_base_cond(cond: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(cond)
    defaults = {
        "dose_ds": 10.0,
        "dist_ds": 125.0,
        "dose_list": "",
        "dist_list": "",
        "total_osc": 10.0,
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "raster_vbeam": 10.0,
        "score_min": 10,
        "score_max": 200,
        "maxhits": 3,
        "cry_min_size_um": 5.0,
        "wavelength": 1.0,
        "hebi_att": 10.0,
        "exp_raster": 0.02,
        "o_index": 0,
        "sample_name": "dummy_sample",
        "root_dir": str(Path.cwd()),
    }
    for k, v in defaults.items():
        out.setdefault(k, v)
    return out


def preprocess_with_useresa(logger: logging.Logger, raw_cond: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], pd.DataFrame]:
    """
    1行 DataFrame を UserESA に食わせて、KUMA を含む前処理フローを可能な範囲で通す。
    """
    from UserESA import UserESA

    cond = normalize_base_cond(raw_cond)
    df = pd.DataFrame([cond])

    ue = UserESA(fname="echa_dummy.xlsx", root_dir=cond.get("root_dir", "."))
    ue.df = df.copy()

    called_steps: List[str] = []

    # あるメソッドだけ順に呼ぶ。存在しない場合は飛ばす。
    steps = [
        "setDefaults",
        "addDistance",
        "splitBeamsizeInfo",
        "fillFlux",
        "checkScanSpeed",
        "defineScanCondition",
        "modifyExposureConditions",
        "sizeWarning",
    ]

    for step in steps:
        if hasattr(ue, step):
            logger.info(f"[UserESA] calling {step}()")
            getattr(ue, step)()
            called_steps.append(step)

    # dose/dist validation
    if hasattr(ue, "validateDoseDist"):
        logger.info("[UserESA] calling validateDoseDist(row)")
        ue.validateDoseDist(ue.df.iloc[0])
        called_steps.append("validateDoseDist")

    if hasattr(ue, "checkDoseList"):
        logger.info("[UserESA] calling checkDoseList()")
        ue.df = ue.checkDoseList()
        called_steps.append("checkDoseList")

    # cond row to dict
    processed_cond = ue.df.iloc[0].to_dict()
    return processed_cond, called_steps, ue.df.copy()


# ----------------------------------------------------------------------
# schedule dry-run
# ----------------------------------------------------------------------
def make_zn(logger: logging.Logger, outdir: Path):
    from ZooNavigator import ZooNavigator
    zn = ZooNavigator.__new__(ZooNavigator)
    zn.logger = logger.getChild("ZooNavigatorDryRun")
    zn.zoo = DummyZoo(zn.logger)
    zn.lm = DummyLM(outdir, zn.logger)
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
    zn.num_pins = 0
    return zn


def make_hebi(logger: logging.Logger, outdir: Path):
    from HEBI import HEBI
    zoo = DummyZoo(logger)
    lm = DummyLM(outdir, logger)
    sw = DummyStopWatch()
    hebi = HEBI(zoo, lm, sw, phosec=1.23e12)
    return hebi, zoo, lm


def simulate_single(logger: logging.Logger, outdir: Path, cond: Dict[str, Any]):
    zn = make_zn(logger, outdir)
    dc_list = zn._build_dc_condition_list(cond)
    logger.info(f"[single] expanded conditions = {dc_list}")
    zn._run_single_dc_loop(cond, sphi=30.0, glist=[(0.0, 0.0, 0.0)], flux=1.23e12, data_prefix="single")
    return {
        "mode": "single",
        "expanded_conditions": dc_list,
        "multi_calls": zn.lm.multi_calls,
        "schedule_files": [str((outdir / f"{call['prefix']}.multi.json")) for call in zn.lm.multi_calls],
    }


def simulate_helical(logger: logging.Logger, outdir: Path, cond: Dict[str, Any], crystal_size_um: float, mode_label: str):
    hebi, _, lm = make_hebi(logger, outdir)
    delta_mm = crystal_size_um / 1000.0
    hebi.getSortedCryList = lambda *a, **k: [DummyCrystal((0.0, 0.000, 0.0), (0.0, delta_mm, 0.0))]
    hebi.edgeCentering = lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz
    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)
    return {
        "mode": mode_label,
        "crystal_size_um": crystal_size_um,
        "n_crystals_processed": n,
        "single_calls": lm.single_calls,
        "helical_calls": lm.helical_calls,
        "schedule_files": [str((outdir / f"{call['prefix']}.single.json")) for call in lm.single_calls] +
                          [str((outdir / f"{call['prefix']}.helical.json")) for call in lm.helical_calls],
    }


def simulate_other_mode(logger: logging.Logger, outdir: Path, cond: Dict[str, Any]):
    zn = make_zn(logger, outdir)
    summary = {
        "mode": cond["mode"],
        "note": "offline dry-run では cond summary のみ出力",
        "cond_summary": {
            "mode": cond.get("mode"),
            "dose_ds": cond.get("dose_ds"),
            "dist_ds": cond.get("dist_ds"),
            "dose_list": cond.get("dose_list"),
            "dist_list": cond.get("dist_list"),
            "raster_vbeam": cond.get("raster_vbeam"),
            "raster_hbeam": cond.get("raster_hbeam"),
            "ds_vbeam": cond.get("ds_vbeam"),
            "ds_hbeam": cond.get("ds_hbeam"),
        }
    }
    try:
        dc_list = zn._build_dc_condition_list(cond)
        summary["dc_condition_list"] = dc_list
    except Exception as e:
        summary["dc_condition_error"] = str(e)
    path = outdir / f"{cond['mode']}.plan.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return summary


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ECHA -> UserESA/KUMA -> dry-run schedule")
    parser.add_argument("exid", help="ECHA exid")
    parser.add_argument("--pin-id", type=int, default=None, help="use specific zoo_samplepin_id instead of next pin")
    parser.add_argument("--modes", default="single,helical,helical-small,ssrox,multi,mixed,quick,screening")
    parser.add_argument("--outdir", default="dryrun_useresa_kuma_out")
    parser.add_argument("--esa-path", default=None, help="directory containing ESAloaderAPI.py / UserESA.py / ZooNavigator.py / HEBI.py")
    parser.add_argument("--dose-list", default=None)
    parser.add_argument("--dist-list", default=None)
    parser.add_argument("--dose-ds", type=float, default=None)
    parser.add_argument("--dist-ds", type=float, default=None)
    parser.add_argument("--small-crystal-um", type=float, default=5.0)
    parser.add_argument("--large-crystal-um", type=float, default=50.0)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("dryrun-useresa-kuma")

    if args.esa_path:
        sys.path.insert(0, args.esa_path)

    ensure_external_stubs()

    from ECHA.ESAloaderAPI import ESAloaderAPI

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) ECHA から cond を取得
    esa = ESAloaderAPI(args.exid)
    esa.prep()
    logger.info(f"ECHA owner username = {esa.get_username()}")

    if args.pin_id is None:
        pin = esa.getNextPin()
        if pin is None:
            raise RuntimeError("No next pin found.")
        zoo_samplepin_id = pin["zoo_samplepin_id"]
        logger.info(f"Using next pin: {pin}")
    else:
        zoo_samplepin_id = args.pin_id
        logger.info(f"Using explicit pin id: {zoo_samplepin_id}")

    fetched_cond = esa.getCond(zoo_samplepin_id)
    if args.dose_list is not None:
        fetched_cond["dose_list"] = args.dose_list
    if args.dist_list is not None:
        fetched_cond["dist_list"] = args.dist_list
    if args.dose_ds is not None:
        fetched_cond["dose_ds"] = args.dose_ds
    if args.dist_ds is not None:
        fetched_cond["dist_ds"] = args.dist_ds

    (outdir / "fetched_cond.json").write_text(
        json.dumps(fetched_cond, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )

    # 2) UserESA/KUMA 前処理
    processed_cond, called_steps, processed_df = preprocess_with_useresa(logger, fetched_cond)
    (outdir / "processed_cond.json").write_text(
        json.dumps(processed_cond, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    processed_df.to_csv(outdir / "processed_df.csv", index=False)

    # 3) mode ごとの schedule dry-run
    results = []
    mode_list = [x.strip() for x in args.modes.split(",") if x.strip()]

    for mode in mode_list:
        logger.info("=" * 80)
        logger.info(f"simulate mode = {mode}")

        cond_local = copy.deepcopy(processed_cond)
        cond_local["mode"] = "helical" if mode.startswith("helical") else mode

        try:
            if mode == "single":
                res = simulate_single(logger, outdir, cond_local)
            elif mode == "helical":
                res = simulate_helical(logger, outdir, cond_local, args.large_crystal_um, "helical")
            elif mode == "helical-small":
                res = simulate_helical(logger, outdir, cond_local, args.small_crystal_um, "helical-small")
            else:
                res = simulate_other_mode(logger, outdir, cond_local)
            results.append(res)
        except Exception as e:
            logger.exception(f"simulation failed for mode={mode}")
            results.append({"mode": mode, "error": str(e)})

    summary = {
        "exid": args.exid,
        "zoo_samplepin_id": zoo_samplepin_id,
        "owner_username": esa.get_username(),
        "called_useresa_steps": called_steps,
        "results": results,
        "files": {
            "fetched_cond": str(outdir / "fetched_cond.json"),
            "processed_cond": str(outdir / "processed_cond.json"),
            "processed_df": str(outdir / "processed_df.csv"),
        }
    }

    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print(f"\nsummary written to: {summary_path}")


if __name__ == "__main__":
    main()
