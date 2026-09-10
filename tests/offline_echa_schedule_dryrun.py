#!/usr/bin/env python3
"""
offline_echa_schedule_dryrun.py

ECHA サーバーには接続するが、装置には接続せずに以下を確認するための dry-run スクリプト。

1. EXID から next pin を取得
2. ECHA に登録された測定条件 (cond) を取得
3. ダミーの LoopMeasurement / Zoo を使って、mode ごとの schedule 生成フローを確認
   - single: ZooNavigator._build_dc_condition_list / _run_single_dc_loop を利用
   - helical: HEBI.mainLoop を利用
   - helical-small: HEBI.mainLoop の small crystal -> single branch を利用
   - multi/mixed/ssrox/quick/screening: 実装依存が強いので plan summary を出力
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
        "Device", "DumpRecover", "AnaHeatmap", "ESA", "KUMA", "CrystalList",
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


def normalize_cond(cond: Dict[str, Any], mode: str) -> Dict[str, Any]:
    out = copy.deepcopy(cond)
    out["mode"] = mode
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


def make_zn(logger: logging.Logger, outdir: Path):
    ensure_external_stubs()
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
    ensure_external_stubs()
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
        "schedule_files": [str((outdir / f"{call['prefix']}.multi.json")) for call in zn.lm.multi_calls],
        "multi_calls": zn.lm.multi_calls,
    }


def simulate_helical(logger: logging.Logger, outdir: Path, cond: Dict[str, Any], crystal_size_um: float):
    hebi, _, lm = make_hebi(logger, outdir)
    delta_mm = crystal_size_um / 1000.0
    hebi.getSortedCryList = lambda *a, **k: [DummyCrystal((0.0, 0.000, 0.0), (0.0, delta_mm, 0.0))]
    hebi.edgeCentering = lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz
    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)
    return {
        "mode": "helical",
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
        "note": "このモードは hardware 依存が強いため、offline dry-run では cond summary のみを出力",
        "cond_summary": {
            "mode": cond["mode"],
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
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="ECHA -> offline schedule dry-run")
    parser.add_argument("exid", help="ECHA exid")
    parser.add_argument("--pin-id", type=int, default=None, help="use specific zoo_samplepin_id instead of next pin")
    parser.add_argument("--modes", default="single,helical,helical-small,ssrox,multi,mixed,quick,screening",
                        help="comma-separated modes to simulate")
    parser.add_argument("--outdir", default="dryrun_out", help="output directory")
    parser.add_argument("--dose-list", default=None, help='override dose_list, e.g. "[1,2]"')
    parser.add_argument("--dist-list", default=None, help='override dist_list, e.g. "[130,140]"')
    parser.add_argument("--dose-ds", type=float, default=None, help="override dose_ds")
    parser.add_argument("--dist-ds", type=float, default=None, help="override dist_ds")
    parser.add_argument("--small-crystal-um", type=float, default=5.0, help="crystal size for helical-small branch")
    parser.add_argument("--large-crystal-um", type=float, default=50.0, help="crystal size for helical branch")
    parser.add_argument("--esa-path", default=None, help="path to directory containing ESAloaderAPI.py if needed")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("dryrun")

    if args.esa_path:
        sys.path.insert(0, args.esa_path)

    from ECHA.ESAloaderAPI import ESAloaderAPI

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

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

    cond = esa.getCond(zoo_samplepin_id)
    logger.info(f"Fetched cond keys = {sorted(cond.keys())}")

    if args.dose_list is not None:
        cond["dose_list"] = args.dose_list
    if args.dist_list is not None:
        cond["dist_list"] = args.dist_list
    if args.dose_ds is not None:
        cond["dose_ds"] = args.dose_ds
    if args.dist_ds is not None:
        cond["dist_ds"] = args.dist_ds

    fetched_cond_path = outdir / "fetched_cond.json"
    fetched_cond_path.write_text(json.dumps(cond, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    results = []
    mode_list = [x.strip() for x in args.modes.split(",") if x.strip()]
    for mode in mode_list:
        logger.info("=" * 80)
        logger.info(f"simulate mode = {mode}")
        cond_local = normalize_cond(cond, "helical" if mode.startswith("helical") else mode)
        try:
            if mode == "single":
                res = simulate_single(logger, outdir, cond_local)
            elif mode == "helical":
                res = simulate_helical(logger, outdir, cond_local, crystal_size_um=args.large_crystal_um)
            elif mode == "helical-small":
                res = simulate_helical(logger, outdir, cond_local, crystal_size_um=args.small_crystal_um)
                res["mode"] = "helical-small"
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
        "fetched_cond_file": str(fetched_cond_path),
        "results": results,
    }
    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print(f"\nsummary written to: {summary_path}")


if __name__ == "__main__":
    main()
