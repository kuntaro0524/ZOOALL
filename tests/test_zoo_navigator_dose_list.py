import sys
import types
import pytest


def _install_stub_modules():
    """
    ZooNavigator import 時に必要になる重い依存を stub で差し替える。
    今回のテスト対象は _parse_series_like_text / _build_dc_condition_list だけなので、
    実装詳細は不要。
    """
    stub_names = [
        "Zoo",
        "AttFactor",
        "LoopMeasurement",
        "BeamsizeConfig",
        "StopWatch",
        "Device",
        "HEBI",
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

    # from Libs import BSSconfig 対応
    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")
    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")
    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])

    # from html_log_maker import ZooHtmlLog 対応
    sys.modules["html_log_maker"].ZooHtmlLog = object

    # from ErrorCode import ErrorCode 対応
    if "ErrorCode" not in sys.modules:
        error_mod = types.ModuleType("ErrorCode")

        class _DummyErrorCode:
            UNKNOWN_MODE = 9999

            @staticmethod
            def to_db_value():
                return 9999

        error_mod.ErrorCode = _DummyErrorCode
        sys.modules["ErrorCode"] = error_mod

    # from ZooMyException import * 対応
    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod


_install_stub_modules()

from ZooNavigator import ZooNavigator
from ZooMyException import ZooMyException


class DummyNavigator(ZooNavigator):
    def __init__(self):
        # 実機初期化を避ける
        pass


@pytest.fixture
def zn():
    return DummyNavigator()


def make_cond(
    mode="single",
    dose_ds=10.0,
    dist_ds=120.0,
    dose_list="",
    dist_list="",
):
    return {
        "mode": mode,
        "dose_ds": dose_ds,
        "dist_ds": dist_ds,
        "dose_list": dose_list,
        "dist_list": dist_list,
    }


def test_parse_series_like_text_empty_string(zn):
    assert zn._parse_series_like_text("") == []


def test_parse_series_like_text_none(zn):
    assert zn._parse_series_like_text(None) == []


def test_parse_series_like_text_nan_text(zn):
    assert zn._parse_series_like_text("nan") == []


def test_parse_series_like_text_single_value(zn):
    assert zn._parse_series_like_text("5") == [5.0]


def test_parse_series_like_text_bracket_list(zn):
    assert zn._parse_series_like_text("[5, 10, 20]") == [5.0, 10.0, 20.0]


def test_parse_series_like_text_plain_csv(zn):
    assert zn._parse_series_like_text("5,10,20") == [5.0, 10.0, 20.0]


def test_build_dc_condition_list_normal_operation_uses_dose_ds_and_dist_ds(zn):
    cond = make_cond(
        mode="single",
        dose_ds=7.5,
        dist_ds=130.0,
        dose_list="",
        dist_list="",
    )
    got = zn._build_dc_condition_list(cond)
    assert got == [{"dose": 7.5, "dist": 130.0}]


def test_build_dc_condition_list_dose_list_only_uses_dist_ds_as_fallback(zn):
    cond = make_cond(
        mode="single",
        dose_ds=999.0,
        dist_ds=140.0,
        dose_list="[1, 5, 10]",
        dist_list="",
    )
    got = zn._build_dc_condition_list(cond)
    assert got == [
        {"dose": 1.0, "dist": 140.0},
        {"dose": 5.0, "dist": 140.0},
        {"dose": 10.0, "dist": 140.0},
    ]


def test_build_dc_condition_list_dose_and_dist_list_zip_together(zn):
    cond = make_cond(
        mode="single",
        dose_ds=999.0,
        dist_ds=999.0,
        dose_list="[1, 5, 10]",
        dist_list="[120, 110, 100]",
    )
    got = zn._build_dc_condition_list(cond)
    assert got == [
        {"dose": 1.0, "dist": 120.0},
        {"dose": 5.0, "dist": 110.0},
        {"dose": 10.0, "dist": 100.0},
    ]


def test_build_dc_condition_list_dist_list_only_is_invalid(zn):
    cond = make_cond(
        mode="single",
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="",
        dist_list="[120, 110]",
    )
    with pytest.raises(ZooMyException):
        zn._build_dc_condition_list(cond)


def test_build_dc_condition_list_length_mismatch_is_invalid_in_zoo(zn):
    cond = make_cond(
        mode="single",
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="[1, 5]",
        dist_list="[120, 110, 100]",
    )
    with pytest.raises(ZooMyException):
        zn._build_dc_condition_list(cond)


@pytest.mark.parametrize("mode", ["multi", "mixed"])
def test_build_dc_condition_list_multi_and_mixed_do_not_allow_multiple_values(zn, mode):
    cond = make_cond(
        mode=mode,
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="[1, 5]",
        dist_list="",
    )
    with pytest.raises(ZooMyException):
        zn._build_dc_condition_list(cond)


@pytest.mark.parametrize("mode", ["multi", "mixed"])
def test_build_dc_condition_list_multi_and_mixed_allow_single_value(zn, mode):
    cond = make_cond(
        mode=mode,
        dose_ds=10.0,
        dist_ds=120.0,
        dose_list="5",
        dist_list="110",
    )
    got = zn._build_dc_condition_list(cond)
    assert got == [{"dose": 5.0, "dist": 110.0}]


def test_build_dc_condition_list_when_dose_list_exists_dose_ds_is_not_used(zn):
    cond = make_cond(
        mode="single",
        dose_ds=12345.0,
        dist_ds=150.0,
        dose_list="[2, 4]",
        dist_list="",
    )
    got = zn._build_dc_condition_list(cond)
    assert got == [
        {"dose": 2.0, "dist": 150.0},
        {"dose": 4.0, "dist": 150.0},
    ]
    assert all(x["dose"] != 12345.0 for x in got)
