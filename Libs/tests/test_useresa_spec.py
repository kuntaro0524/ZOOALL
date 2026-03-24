import configparser
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import UserESA as useresa_module


class FakeKUMA:
    """Deterministic KUMA stub.

    Returns 0.2 MGy for any scalar input and a vector of 0.2 for vector input.
    This makes the expected dose/frame math easy to verify:
      - normal/scan_only/phasing/rapid: 0.2 MGy
      - high_dose_scan: 0.3 MGy
      - ultra_high_dose_scan: 0.6 MGy
      - dose_list active: 0.001 MGy
    """

    def getDose(self, hbeam, vbeam, flux, energy, exp_raster):
        if hasattr(hbeam, "__len__") and not isinstance(hbeam, (str, bytes)):
            return np.full(len(hbeam), 0.2, dtype=float)
        return 0.2


@pytest.fixture()
def user(monkeypatch):
    monkeypatch.setattr(useresa_module.KUMA, "KUMA", FakeKUMA)

    logger = logging.getLogger("useresa-test")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.INFO)

    inst = useresa_module.UserESA.__new__(useresa_module.UserESA)
    inst.logger = logger
    inst.debug = False
    inst.isDoseError = False
    inst.root_dir = "."
    inst.fname = "dummy.xlsx"
    inst.csv_prefix = "dummy"
    inst.beamline = "BL32XU"
    inst.dose_distance_handler = useresa_module.DoseDistanceHandler(logger, debug=False)

    cfg = configparser.ConfigParser()
    cfg.read_dict(
        {
            "beamline": {"beamline": "BL32XU"},
            "experiment": {
                "score_min": "10",
                "score_max": "100",
                "raster_dose": "0.1",
                "dose_ds": "10.0",
                "raster_roi": "1",
                "exp_ds": "0.02",
                "exp_raster": "0.04",
                "att_raster": "50.0",
                "hebi_att": "50.0",
                "cover_flag": "1",
                "resol_raster": "3.0",
                "raster_roi_edge_mm": "10.0",
                "max_hori_scan_speed": "1000.0",
            },
            "detector": {
                "min_camera_len": "100.0",
                "min_camera_dim": "100.0",
            },
        }
    )
    inst.config = cfg
    return inst


def make_row(**overrides):
    row = {
        "puckid": "PK1",
        "pinid": 1,
        "sample_name": "sample",
        "desired_exp": "normal",
        "mode": "single",
        "wavelength": 1.0,
        "resolution_limit": 2.0,
        "beamsize": "10x10",
        "max_crystal_size": 20.0,
        "maxhits": 5,
        "total_osc": 10.0,
        "osc_width": 0.1,
        "ln2_flag": "No",
        "pin_flag": "spine",
        "zoomcap_flag": "No",
        "dose_list": "",
        "dist_list": "",
        # Fields below are enough to unit-test defineScanCondition directly.
        "ds_hbeam": 10.0,
        "ds_vbeam": 10.0,
        "raster_hbeam": 10.0,
        "raster_vbeam": 10.0,
        "flux": 1.0e12,
        "exp_raster": 0.04,
        "dist_ds": 120.0,
    }
    row.update(overrides)
    return row


def prepare_for_define_scan_condition(user, rows):
    user.df = pd.DataFrame(rows)
    user.setDefaults()
    user.defineScanCondition()
    return user.df


@pytest.mark.parametrize(
    "dose_list,dist_list,expected_dose,expected_dist",
    [
        ("5", "", "5", ""),
        ("5", "120", "5", "120"),
        ("5,10", "120,110,100", "[5, 10, 10]", "[120, 110, 100]"),
        ("[5, 10]", "[120]", "[5, 10]", "[120, 120]"),
    ],
)
def test_check_dose_list_normalization(user, dose_list, dist_list, expected_dose, expected_dist):
    df = pd.DataFrame([make_row(dose_list=dose_list, dist_list=dist_list)])
    out = user.dose_distance_handler.check_dose_list(df)
    assert out.loc[0, "dose_list"] == expected_dose
    assert out.loc[0, "dist_list"] == expected_dist


def test_check_dose_list_rejects_dist_without_dose(user):
    df = pd.DataFrame([make_row(dose_list="", dist_list="120")])
    with pytest.raises(ValueError, match="dist_list cannot be specified without dose_list"):
        user.dose_distance_handler.check_dose_list(df)


@pytest.mark.parametrize("mode", ["multi", "mixed"])
def test_check_dose_list_rejects_multi_values_for_multi_and_mixed(user, mode):
    df = pd.DataFrame([make_row(mode=mode, dose_list="5,10", dist_list="")])
    with pytest.raises(ValueError, match="prohibits multiple values"):
        user.dose_distance_handler.check_dose_list(df)

    df2 = pd.DataFrame([make_row(mode=mode, dose_list="5", dist_list="120,110")])
    with pytest.raises(ValueError, match="prohibits multiple values"):
        user.dose_distance_handler.check_dose_list(df2)


@pytest.mark.parametrize("mode", ["single", "helical", "multi", "mixed"])
def test_validate_dose_dist_accepts_expected_patterns(user, mode):
    # dose only: allowed for every mode as long as value count is valid
    user.validateDoseDist({"mode": mode, "dose_list": "5", "dist_list": ""})
    # dose + dist singletons: allowed for every mode
    user.validateDoseDist({"mode": mode, "dose_list": "5", "dist_list": "120"})


def test_validate_dose_dist_rejects_dist_only(user):
    with pytest.raises(ValueError, match="dist_list cannot be specified without dose_list"):
        user.validateDoseDist({"mode": "single", "dose_list": "", "dist_list": "120"})


@pytest.mark.parametrize("mode", ["multi", "mixed"])
def test_validate_dose_dist_rejects_multiple_values_in_multi_and_mixed(user, mode):
    with pytest.raises(ValueError, match="does not allow multiple values"):
        user.validateDoseDist({"mode": mode, "dose_list": "5,10", "dist_list": ""})
    with pytest.raises(ValueError, match="does not allow multiple values"):
        user.validateDoseDist({"mode": mode, "dose_list": "5", "dist_list": "120,110"})


def test_define_scan_condition_expected_dose_math(user):
    rows = [
        make_row(puckid="P1", pinid=1, desired_exp="normal"),
        make_row(puckid="P1", pinid=2, desired_exp="high_dose_scan"),
        make_row(puckid="P1", pinid=3, desired_exp="ultra_high_dose_scan"),
        make_row(puckid="P1", pinid=4, desired_exp="scan_only"),
        make_row(puckid="P1", pinid=5, desired_exp="phasing"),
        make_row(puckid="P1", pinid=6, desired_exp="rapid"),
        make_row(puckid="P1", pinid=7, desired_exp="normal", dose_list="5,10", dist_list=""),
    ]
    df = prepare_for_define_scan_condition(user, rows)

    expected = {
        1: (0.2, 9.8),
        2: (0.3, 9.7),
        3: (0.6, 9.4),
        4: (0.2, 9.8),
        5: (0.2, 9.8),
        6: (0.2, 9.8),
        # dose_list active: scan dose fixed to 1 kGy/frame and dose_ds not budget-recomputed.
        7: (0.001, 10.0),
    }
    for pinid, (dose_pf, dose_ds) in expected.items():
        row = df[df["pinid"] == pinid].iloc[0]
        assert row["dose_per_frame"] == pytest.approx(dose_pf)
        assert row["dose_ds"] == pytest.approx(dose_ds)

    # Photon-based raster conditions for the three main scan families.
    normal = df[df["pinid"] == 1].iloc[0]
    high = df[df["pinid"] == 2].iloc[0]
    ultra = df[df["pinid"] == 3].iloc[0]
    ext = df[df["pinid"] == 7].iloc[0]

    assert normal["att_raster"] == pytest.approx(100.0)
    assert high["att_raster"] == pytest.approx(150.0)
    assert ultra["att_raster"] == pytest.approx(300.0)
    assert ext["att_raster"] == pytest.approx(0.5)

    assert normal["ppf_raster"] == pytest.approx(4.0e10)
    assert high["ppf_raster"] == pytest.approx(6.0e10)
    assert ultra["ppf_raster"] == pytest.approx(1.2e11)
    assert ext["ppf_raster"] == pytest.approx(2.0e8)

    assert user.isDoseError is False


@pytest.mark.parametrize("mode", ["single", "helical", "multi", "mixed"])
def test_mode_does_not_change_define_scan_condition_numeric_result_without_lists(user, mode):
    rows = [
        make_row(puckid="PM", pinid=1, desired_exp="normal", mode=mode),
        make_row(puckid="PM", pinid=2, desired_exp="high_dose_scan", mode=mode),
        make_row(puckid="PM", pinid=3, desired_exp="ultra_high_dose_scan", mode=mode),
    ]
    df = prepare_for_define_scan_condition(user, rows)

    expected = {
        1: 0.2,
        2: 0.3,
        3: 0.6,
    }
    for pinid, dose_pf in expected.items():
        row = df[df["pinid"] == pinid].iloc[0]
        assert row["dose_per_frame"] == pytest.approx(dose_pf)


@pytest.mark.parametrize("mode,expected_score_max", [("single", 100), ("multi", 100), ("helical", 9999), ("mixed", 9999)])
def test_set_defaults_normal_score_max_depends_on_mode(user, mode, expected_score_max):
    user.df = pd.DataFrame([make_row(mode=mode, desired_exp="normal")])
    user.setDefaults()
    assert int(user.df.loc[0, "score_max"]) == expected_score_max


def test_make_condlist_order_is_spec_compatible(user, monkeypatch, tmp_path):
    call_order = []

    def record(name):
        def _wrapped(*args, **kwargs):
            call_order.append(name)
            return None
        return _wrapped

    # Patch file-producing tail so the test stays isolated.
    monkeypatch.setattr(useresa_module.UserESA, "read_new", record("read_new"))
    monkeypatch.setattr(useresa_module.UserESA, "expandCompressedPinInfo", record("expandCompressedPinInfo"))
    monkeypatch.setattr(useresa_module.UserESA, "checkLN2flag", record("checkLN2flag"))
    monkeypatch.setattr(useresa_module.UserESA, "checkZoomFlag", record("checkZoomFlag"))
    monkeypatch.setattr(useresa_module.UserESA, "checkPinFlag", record("checkPinFlag"))
    monkeypatch.setattr(useresa_module.UserESA, "splitBeamsizeInfo", record("splitBeamsizeInfo"))
    monkeypatch.setattr(useresa_module.UserESA, "fillFlux", record("fillFlux"))
    monkeypatch.setattr(useresa_module.UserESA, "setDefaults", record("setDefaults"))
    monkeypatch.setattr(useresa_module.UserESA, "addDistance", record("addDistance"))
    monkeypatch.setattr(useresa_module.UserESA, "checkScanSpeed", record("checkScanSpeed"))
    monkeypatch.setattr(useresa_module.UserESA, "defineScanCondition", record("defineScanCondition"))
    monkeypatch.setattr(useresa_module.UserESA, "modifyExposureConditions", record("modifyExposureConditions"))
    monkeypatch.setattr(useresa_module.UserESA, "sizeWarning", record("sizeWarning"))
    monkeypatch.setattr(useresa_module.UserESA, "checkDoseList", record("checkDoseList"))

    user.df = pd.DataFrame([make_row()])
    user.columns = []
    user.csv_prefix = str(tmp_path / "dummy")

    # Avoid the final astype/to_csv section from failing by stubbing it minimally.
    class DummyDF(pd.DataFrame):
        @property
        def _constructor(self):
            return DummyDF

        def astype(self, *args, **kwargs):
            return self

        def to_csv(self, *args, **kwargs):
            call_order.append("to_csv")

    user.df = DummyDF([make_row()])

    user.makeCondList()

    assert call_order.index("setDefaults") < call_order.index("addDistance") < call_order.index("checkDoseList")
