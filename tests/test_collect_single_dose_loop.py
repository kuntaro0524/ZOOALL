

import sys
import types
import pytest


def _install_stub_modules():
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

    # html_log_maker
    sys.modules["html_log_maker"].ZooHtmlLog = object

    # ErrorCode
    if "ErrorCode" not in sys.modules:
        error_mod = types.ModuleType("ErrorCode")

        class _DummyErrorCode:
            UNKNOWN_MODE = 9999

            @staticmethod
            def to_db_value():
                return 9999

        error_mod.ErrorCode = _DummyErrorCode
        sys.modules["ErrorCode"] = error_mod

    # ZooMyException
    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod

    # from Libs import BSSconfig
    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")

    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")

    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])


_install_stub_modules()

from ZooNavigator import ZooNavigator


import sys
import types
import pytest


def _install_stub_modules():
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

    # html_log_maker
    sys.modules["html_log_maker"].ZooHtmlLog = object

    # ErrorCode
    if "ErrorCode" not in sys.modules:
        error_mod = types.ModuleType("ErrorCode")

        class _DummyErrorCode:
            UNKNOWN_MODE = 9999

            @staticmethod
            def to_db_value():
                return 9999

        error_mod.ErrorCode = _DummyErrorCode
        sys.modules["ErrorCode"] = error_mod

    # ZooMyException
    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod

    # from Libs import BSSconfig
    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")

    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")

    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])


_install_stub_modules()

from ZooNavigator import ZooNavigator


import sys
import types
import pytest


def _install_stub_modules():
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

    # html_log_maker
    sys.modules["html_log_maker"].ZooHtmlLog = object

    # ErrorCode
    if "ErrorCode" not in sys.modules:
        error_mod = types.ModuleType("ErrorCode")

        class _DummyErrorCode:
            UNKNOWN_MODE = 9999

            @staticmethod
            def to_db_value():
                return 9999

        error_mod.ErrorCode = _DummyErrorCode
        sys.modules["ErrorCode"] = error_mod

    # ZooMyException
    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod

    # from Libs import BSSconfig
    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")

    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")

    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])


_install_stub_modules()

from ZooNavigator import ZooNavigator


class DummyNavigator(ZooNavigator):
    def __init__(self):
        pass


@pytest.fixture
def zn(monkeypatch):
    zn = DummyNavigator()

    calls = []

    def fake_do_data_collection(cond, *args, **kwargs):
        # 呼ばれたときの dose / dist を記録
        calls.append((cond["dose_ds"], cond["dist_ds"]))

    monkeypatch.setattr(zn, "doDataCollection", fake_do_data_collection)

    zn._calls = calls
    return zn


def make_cond(dose_list="", dist_list=""):
    return {
        "mode": "single",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "dose_list": dose_list,
        "dist_list": dist_list,
    }


# -------------------------
# テスト本体
# -------------------------

def test_single_no_dose_list_runs_once(zn):
    cond = make_cond("", "")

    zn.collectSingle(cond, sphi=0)

    assert zn._calls == [(10.0, 120.0)]


def test_single_with_dose_list_runs_multiple(zn):
    cond = make_cond("[1,5,10]", "")

    zn.collectSingle(cond, sphi=0)

    assert zn._calls == [
        (1.0, 120.0),
        (5.0, 120.0),
        (10.0, 120.0),
    ]


def test_single_with_dose_and_dist_list(zn):
    cond = make_cond("[1,5,10]", "[100,110,120]")

    zn.collectSingle(cond, sphi=0)

    assert zn._calls == [
        (1.0, 100.0),
        (5.0, 110.0),
        (10.0, 120.0),
    ]


def test_single_dose_list_overrides_dose_ds(zn):
    cond = make_cond("[2,4]", "")

    zn.collectSingle(cond, sphi=0)

    # 元の dose_ds=10 は使われない
    assert all(d != 10.0 for d, _ in zn._calls)
