import argparse
import copy
import importlib
import json
import logging
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

def add_candidate_paths(repo_root: str | None = None) -> List[str]:
    added: List[str] = []
    here = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    candidates = [
        here, here.parent,
        here / "Libs", here / "Libs" / "ECHA",
        here.parent / "Libs", here.parent / "Libs" / "ECHA",
        cwd, cwd / "Libs", cwd / "Libs" / "ECHA",
    ]
    if repo_root:
        rr = Path(repo_root).resolve()
        candidates.extend([rr, rr / "Libs", rr / "Libs" / "ECHA", rr / "tests"])
    for p in candidates:
        if p.exists():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)
                added.append(s)
    return added

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
    if "BeamsizeConfig" in sys.modules and not hasattr(sys.modules["BeamsizeConfig"], "BeamsizeConfig"):
        class _DummyBS:
            def getBeamIndexHV(self, h, v):
                return 1
            def getFluxAtWavelength(self, h, v, wavelength):
                return 1.0e12
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
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        self.logger.info(f"schedule written: {path}")
        return str(path)
    def genSingleSchedule(self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True):
        payload = {"kind":"single","prefix":prefix,"start_phi":start_phi,"end_phi":end_phi,
                   "center_xyz":center_xyz,"dose_ds":cond.get("dose_ds"),"dist_ds":cond.get("dist_ds"),
                   "same_point":same_point,"mode":cond.get("mode")}
        self.single_calls.append(payload)
        return self._write_schedule(f"{prefix}.single.json", payload)
    def genHelical(self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond):
        payload = {"kind":"helical","prefix":prefix,"start_phi":start_phi,"end_phi":end_phi,
                   "left_xyz":left_xyz,"right_xyz":right_xyz,"dose_ds":cond.get("dose_ds"),
                   "dist_ds":cond.get("dist_ds"),"mode":cond.get("mode")}
        self.helical_calls.append(payload)
        return self._write_schedule(f"{prefix}.helical.json", payload)
    def genMultiSchedule(self, sphi, glist, cond, flux, prefix="multi"):
        payload = {"kind":"multi","prefix":prefix,"sphi":sphi,"glist":glist,
                   "dose_ds":cond.get("dose_ds"),"dist_ds":cond.get("dist_ds"),
                   "mode":cond.get("mode"),"flux":flux}
        self.multi_calls.append(payload)
        return self._write_schedule(f"{prefix}.multi.json", payload)
    def rasterMaster(self, scan_id, scan_mode, center, vrange_um, hrange_um, vstep_um, hstep_um, phi, cond, isHEBI=False):
        payload = {"kind":"raster","scan_id":scan_id,"scan_mode":scan_mode,"center":center,
                   "vrange_um":vrange_um,"hrange_um":hrange_um,"vstep_um":vstep_um,
                   "hstep_um":hstep_um,"phi":phi,"mode":cond.get("mode"),"isHEBI":isHEBI}
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

def import_required_modules():
    ESAloaderAPI = importlib.import_module("ESAloaderAPI").ESAloaderAPI
    UserESA = importlib.import_module("UserESA").UserESA
    ZooNavigator = importlib.import_module("ZooNavigator").ZooNavigator
    HEBI = importlib.import_module("HEBI").HEBI
    return ESAloaderAPI, UserESA, ZooNavigator, HEBI

def normalize_base_cond(cond: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(cond)
    defaults = {
        "dose_ds": 10.0, "dist_ds": 125.0, "dose_list": "", "dist_list": "",
        "total_osc": 10.0, "ds_hbeam": 10.0, "ds_vbeam": 10.0, "raster_hbeam": 10.0,
        "raster_vbeam": 10.0, "score_min": 10, "score_max": 200, "maxhits": 3,
        "cry_min_size_um": 5.0, "cry_max_size_um": 30.0, "wavelength": 1.0,
        "hebi_att": 10.0, "exp_raster": 0.02, "o_index": 0,
        "sample_name": "dummy_sample", "root_dir": str(Path.cwd()),
        "desired_exp": "normal", "resolution_limit": 2.0, "loopsize": 30.0,
        "osc_width": 0.1, "ln2_flag": 0, "pin_flag": "-", "zoomcap_flag": 0,
        "confirmation_require": 0,
    }
    for k, v in defaults.items():
        out.setdefault(k, v)
    return out

def convert_echa_cond_to_useresa_row(raw_cond: Dict[str, Any]) -> Dict[str, Any]:
    cond = normalize_base_cond(raw_cond)
    ds_hbeam = float(cond.get("ds_hbeam", cond.get("raster_hbeam", 10.0)))
    ds_vbeam = float(cond.get("ds_vbeam", cond.get("raster_vbeam", 10.0)))
    beamsize_str = cond.get("beamsize")
    if beamsize_str is None or str(beamsize_str).strip() == "":
        beamsize_str = f"{ds_hbeam}x{ds_vbeam}"
    max_crystal_size = cond.get("cry_max_size_um", 30.0)
    if max_crystal_size in (None, ""):
        max_crystal_size = 30.0
    loopsize = cond.get("loopsize")
    if loopsize in (None, ""):
        loopsize = max_crystal_size
    return {
        "puckid": cond.get("puckid", cond.get("puck_id", "UNKNOWN")),
        "pinid": cond.get("pinid", cond.get("pin_id", 0)),
        "sample_name": cond.get("sample_name", "dummy_sample"),
        "desired_exp": cond.get("desired_exp", "normal"),
        "mode": cond.get("mode", "single"),
        "wavelength": float(cond.get("wavelength", 1.0)),
        "loopsize": float(loopsize),
        "resolution_limit": float(cond.get("resolution_limit", 2.0)),
        "beamsize": beamsize_str,
        "max_crystal_size": float(max_crystal_size),
        "maxhits": int(cond.get("maxhits", 3)),
        "total_osc": float(cond.get("total_osc", 10.0)),
        "osc_width": float(cond.get("osc_width", 0.1)),
        "ln2_flag": cond.get("ln2_flag", 0),
        "pin_flag": cond.get("pin_flag", "-"),
        "zoomcap_flag": cond.get("zoomcap_flag", 0),
        "confirmation_require": cond.get("confirmation_require", 0),
        "dose_list": cond.get("dose_list", ""),
        "dist_list": cond.get("dist_list", ""),
    }

def preprocess_with_useresa(logger: logging.Logger, UserESA, raw_cond: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], pd.DataFrame]:
    cond = normalize_base_cond(raw_cond)
    useresa_row = convert_echa_cond_to_useresa_row(cond)
    logger.info(f"[dryrun] UserESA input row keys = {sorted(useresa_row.keys())}")
    df = pd.DataFrame([useresa_row])
    ue = UserESA(fname="echa_dummy.xlsx", root_dir=cond.get("root_dir", "."))
    ue.df = df.copy()
    called_steps: List[str] = []
    steps = ["setDefaults", "addDistance", "splitBeamsizeInfo", "fillFlux",
             "checkScanSpeed", "defineScanCondition", "modifyExposureConditions", "sizeWarning"]
    for step in steps:
        if hasattr(ue, step):
            logger.info(f"[UserESA] calling {step}()")
            getattr(ue, step)()
            called_steps.append(step)
    if hasattr(ue, "validateDoseDist"):
        logger.info("[UserESA] calling validateDoseDist(row)")
        ue.validateDoseDist(ue.df.iloc[0])
        called_steps.append("validateDoseDist")
    if hasattr(ue, "checkDoseList"):
        logger.info("[UserESA] calling checkDoseList()")
        ue.checkDoseList()
        called_steps.append("checkDoseList")
    processed_cond = ue.df.iloc[0].to_dict()
    return processed_cond, called_steps, ue.df.copy()

def make_zn(logger: logging.Logger, outdir: Path, ZooNavigator):
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

def make_hebi(logger: logging.Logger, outdir: Path, HEBI):
    zoo = DummyZoo(logger)
    lm = DummyLM(outdir, logger)
    sw = DummyStopWatch()
    hebi = HEBI(zoo, lm, sw, phosec=1.23e12)
    return hebi, zoo, lm

def simulate_single(logger: logging.Logger, outdir: Path, cond: Dict[str, Any], ZooNavigator):
    zn = make_zn(logger, outdir, ZooNavigator)
    dc_list = zn._build_dc_condition_list(cond)
    logger.info(f"[single] expanded conditions = {dc_list}")
    zn._run_single_dc_loop(cond, sphi=30.0, glist=[(0.0, 0.0, 0.0)], flux=1.23e12, data_prefix="single")
    return {"mode":"single","expanded_conditions":dc_list,"multi_calls":zn.lm.multi_calls,
            "schedule_files":[str((outdir / f"{call['prefix']}.multi.json")) for call in zn.lm.multi_calls]}

def simulate_helical(logger: logging.Logger, outdir: Path, cond: Dict[str, Any], crystal_size_um: float, HEBI, mode_label: str):
    hebi, _, lm = make_hebi(logger, outdir, HEBI)
    delta_mm = crystal_size_um / 1000.0
    hebi.getSortedCryList = lambda *a, **k: [DummyCrystal((0.0, 0.000, 0.0), (0.0, delta_mm, 0.0))]
    hebi.edgeCentering = lambda cond, phi_face, center_xyz, LorR="Left", cry_index=0: center_xyz
    n = hebi.mainLoop("dummy_path", "dummy_prefix", 30.0, cond, precise_face_scan=False)
    return {"mode":mode_label,"crystal_size_um":crystal_size_um,"n_crystals_processed":n,
            "single_calls":lm.single_calls,"helical_calls":lm.helical_calls,
            "schedule_files":[str((outdir / f"{call['prefix']}.single.json")) for call in lm.single_calls] +
                             [str((outdir / f"{call['prefix']}.helical.json")) for call in lm.helical_calls]}

def simulate_other_mode(logger: logging.Logger, outdir: Path, cond: Dict[str, Any], ZooNavigator):
    zn = make_zn(logger, outdir, ZooNavigator)
    summary = {"mode":cond["mode"],"note":"offline dry-run では cond summary のみ出力",
               "cond_summary":{"mode":cond.get("mode"),"dose_ds":cond.get("dose_ds"),"dist_ds":cond.get("dist_ds"),
                               "dose_list":cond.get("dose_list"),"dist_list":cond.get("dist_list"),
                               "raster_vbeam":cond.get("raster_vbeam"),"raster_hbeam":cond.get("raster_hbeam"),
                               "ds_vbeam":cond.get("ds_vbeam"),"ds_hbeam":cond.get("ds_hbeam"),
                               "cry_min_size_um":cond.get("cry_min_size_um"),"cry_max_size_um":cond.get("cry_max_size_um")}}
    try:
        dc_list = zn._build_dc_condition_list(cond)
        summary["dc_condition_list"] = dc_list
    except Exception as e:
        summary["dc_condition_error"] = str(e)
    path = outdir / f"{cond['mode']}.plan.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return summary

def main():
    parser = argparse.ArgumentParser(description="ECHA -> UserESA/KUMA -> dry-run schedule")
    parser.add_argument("exid")
    parser.add_argument("--pin-id", type=int, default=None)
    parser.add_argument("--modes", default="single,helical,helical-small,ssrox,multi,mixed,quick,screening")
    parser.add_argument("--outdir", default="dryrun_useresa_kuma_out")
    parser.add_argument("--repo-root", default=None, help="e.g. /user/target/JunkZoo")
    parser.add_argument("--dose-list", default=None)
    parser.add_argument("--dist-list", default=None)
    parser.add_argument("--dose-ds", type=float, default=None)
    parser.add_argument("--dist-ds", type=float, default=None)
    parser.add_argument("--small-crystal-um", type=float, default=5.0)
    parser.add_argument("--large-crystal-um", type=float, default=50.0)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("dryrun-useresa-kuma")
    added = add_candidate_paths(args.repo_root)
    logger.info(f"added import paths: {added}")

    ensure_external_stubs()
    try:
        ESAloaderAPI, UserESA, ZooNavigator, HEBI = import_required_modules()
    except ModuleNotFoundError as e:
        logger.error(f"import failed: {e}")
        logger.error("Hint: specify --repo-root /user/target/JunkZoo")
        raise

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

    fetched_cond = esa.getCond(zoo_samplepin_id)
    if args.dose_list is not None:
        fetched_cond["dose_list"] = args.dose_list
        fetched_cond["mode"] = "single"
    if args.dist_list is not None:
        fetched_cond["dist_list"] = args.dist_list
    if args.dose_ds is not None:
        fetched_cond["dose_ds"] = args.dose_ds
    if args.dist_ds is not None:
        fetched_cond["dist_ds"] = args.dist_ds

    (outdir / "fetched_cond.json").write_text(json.dumps(fetched_cond, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    processed_cond, called_steps, processed_df = preprocess_with_useresa(logger, UserESA, fetched_cond)
    (outdir / "processed_cond.json").write_text(json.dumps(processed_cond, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    processed_df.to_csv(outdir / "processed_df.csv", index=False)

    results = []
    mode_list = [x.strip() for x in args.modes.split(",") if x.strip()]
    for mode in mode_list:
        logger.info("=" * 80)
        logger.info(f"simulate mode = {mode}")
        cond_local = copy.deepcopy(processed_cond)
        cond_local["mode"] = "helical" if mode.startswith("helical") else mode
        try:
            if mode == "single":
                res = simulate_single(logger, outdir, cond_local, ZooNavigator)
            elif mode == "helical":
                res = simulate_helical(logger, outdir, cond_local, args.large_crystal_um, HEBI, "helical")
            elif mode == "helical-small":
                res = simulate_helical(logger, outdir, cond_local, args.small_crystal_um, HEBI, "helical-small")
            else:
                res = simulate_other_mode(logger, outdir, cond_local, ZooNavigator)
            results.append(res)
        except Exception as e:
            logger.exception(f"simulation failed for mode={mode}")
            results.append({"mode": mode, "error": str(e)})

    summary = {"exid":args.exid,"zoo_samplepin_id":zoo_samplepin_id,"owner_username":esa.get_username(),
               "called_useresa_steps":called_steps,
               "files":{"fetched_cond":str(outdir / "fetched_cond.json"),
                        "processed_cond":str(outdir / "processed_cond.json"),
                        "processed_df":str(outdir / "processed_df.csv")},
               "results":results}
    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print(f"\\nsummary written to: {summary_path}")

if __name__ == "__main__":
    main()

