# test_zoo_navigator_echa.py
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

    # html_log_maker.ZooHtmlLog
    sys.modules["html_log_maker"].ZooHtmlLog = object

    # Libs.BSSconfig
    if "Libs" not in sys.modules:
        sys.modules["Libs"] = types.ModuleType("Libs")
    if "Libs.BSSconfig" not in sys.modules:
        sys.modules["Libs.BSSconfig"] = types.ModuleType("Libs.BSSconfig")
    setattr(sys.modules["Libs"], "BSSconfig", sys.modules["Libs.BSSconfig"])

    # ZooMyException
    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod

    # ErrorCode
    if "ErrorCode" not in sys.modules:
        err_mod = types.ModuleType("ErrorCode")

        class _ECItem:
            def __init__(self, v):
                self.v = v

            def to_db_value(self):
                return self.v

        class ErrorCode:
            UNKNOWN_MODE = _ECItem(8001)
            SUCCESS = _ECItem(1)

        err_mod.ErrorCode = ErrorCode
        sys.modules["ErrorCode"] = err_mod


_install_stub_modules()

from ZooNavigator import ZooNavigator
from ZooMyException import ZooMyException


def _dummy_logger():
    return types.SimpleNamespace(
        info=lambda *a, **k: None,
        debug=lambda *a, **k: None,
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )


@pytest.fixture
def zn():
    z = object.__new__(ZooNavigator)
    z.logger = _dummy_logger()
    z.isECHA = True
    return z


def test_updateDBinfo_echa_isDone_calls_setDone(zn):
    calls = []

    class DummyECHA:
        def setDone(self, p_index, zoo_samplepin_id, value):
            calls.append(("setDone", p_index, zoo_samplepin_id, value))

        def postResult(self, zoo_samplepin_id, payload):
            calls.append(("postResult", zoo_samplepin_id, payload))

    zn.echa_esa = DummyECHA()

    cond = {
        "p_index": 17,
        "zoo_samplepin_id": 310,
    }

    zn.updateDBinfo(cond, "isDone", 1)

    assert calls == [("setDone", 17, 310, 1)]


def test_updateDBinfo_echa_result_posts_json(zn):
    calls = []

    class DummyECHA:
        def setDone(self, p_index, zoo_samplepin_id, value):
            calls.append(("setDone", p_index, zoo_samplepin_id, value))

        def postResult(self, zoo_samplepin_id, payload):
            calls.append(("postResult", zoo_samplepin_id, payload))

    zn.echa_esa = DummyECHA()

    cond = {"zoo_samplepin_id": 310}
    zn.updateDBinfo(cond, "flux", 1.23e12)

    assert calls == [
        (
            "postResult",
            310,
            {"data": [{"flux": 1.23e12}]},
        )
    ]


def test_updateTime_echa_posts_t_event(zn):
    calls = []

    class DummyECHA:
        def postResult(self, zoo_samplepin_id, payload):
            calls.append((zoo_samplepin_id, payload))

    zn.echa_esa = DummyECHA()

    cond = {"zoo_samplepin_id": 999}
    zn.updateTime(cond, "meas_start")

    assert len(calls) == 1
    zoo_samplepin_id, payload = calls[0]
    assert zoo_samplepin_id == 999
    assert "data" in payload
    assert "t_meas_start" in payload["data"][0]
    assert isinstance(payload["data"][0]["t_meas_start"], str)
    assert payload["data"][0]["t_meas_start"] != ""


def test_parse_series_like_text_basic(zn):
    assert zn._parse_series_like_text("") == []
    assert zn._parse_series_like_text("5") == [5.0]
    assert zn._parse_series_like_text("[1, 5, 10]") == [1.0, 5.0, 10.0]


def test_build_dc_condition_list_normal(zn):
    cond = {
        "mode": "single",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "dose_list": "",
        "dist_list": "",
    }
    got = zn._build_dc_condition_list(cond)
    assert got == [{"dose": 10.0, "dist": 120.0}]


def test_build_dc_condition_list_dose_list_only(zn):
    cond = {
        "mode": "single",
        "dose_ds": 999.0,
        "dist_ds": 130.0,
        "dose_list": "[1, 5, 10]",
        "dist_list": "",
    }
    got = zn._build_dc_condition_list(cond)
    assert got == [
        {"dose": 1.0, "dist": 130.0},
        {"dose": 5.0, "dist": 130.0},
        {"dose": 10.0, "dist": 130.0},
    ]


def test_build_dc_condition_list_dose_and_dist_list(zn):
    cond = {
        "mode": "helical",
        "dose_ds": 999.0,
        "dist_ds": 999.0,
        "dose_list": "[1, 5, 10]",
        "dist_list": "[120, 110, 100]",
    }
    got = zn._build_dc_condition_list(cond)
    assert got == [
        {"dose": 1.0, "dist": 120.0},
        {"dose": 5.0, "dist": 110.0},
        {"dose": 10.0, "dist": 100.0},
    ]


def test_build_dc_condition_list_dist_list_only_error(zn):
    cond = {
        "mode": "single",
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "dose_list": "",
        "dist_list": "[120, 110]",
    }
    with pytest.raises(ZooMyException):
        zn._build_dc_condition_list(cond)


@pytest.mark.parametrize("mode", ["multi", "mixed"])
def test_build_dc_condition_list_multi_mixed_multiple_error(zn, mode):
    cond = {
        "mode": mode,
        "dose_ds": 10.0,
        "dist_ds": 120.0,
        "dose_list": "[1, 5]",
        "dist_list": "",
    }
    with pytest.raises(ZooMyException):
        zn._build_dc_condition_list(cond)


def test_run_single_dc_loop_uses_dose_list_and_dist_fallback(zn):
    calls = []

    class DummyLM:
        def genMultiSchedule(self, sphi, glist, cond_local, flux, prefix="single"):
            return {
                "prefix": prefix,
                "dose_ds": cond_local["dose_ds"],
                "dist_ds": cond_local["dist_ds"],
                "flux": flux,
                "glist": glist,
                "sphi": sphi,
            }

    class DummyZoo:
        def doDataCollection(self, schedule):
            calls.append(schedule)

        def waitTillReady(self):
            pass

    zn.lm = DummyLM()
    zn.zoo = DummyZoo()
    zn.logger = _dummy_logger()

    cond = {
        "mode": "single",
        "dose_ds": 999.0,
        "dist_ds": 135.0,
        "dose_list": "[1, 5, 10]",
        "dist_list": "",
    }

    zn._run_single_dc_loop(
        cond=cond,
        sphi=0.0,
        glist=[[1.0, 2.0, 3.0]],
        flux=1.0e12,
        data_prefix="single",
    )

    assert len(calls) == 3
    assert [(c["dose_ds"], c["dist_ds"]) for c in calls] == [
        (1.0, 135.0),
        (5.0, 135.0),
        (10.0, 135.0),
    ]


def test_run_single_dc_loop_uses_dist_list_when_present(zn):
    calls = []

    class DummyLM:
        def genMultiSchedule(self, sphi, glist, cond_local, flux, prefix="single"):
            return {
                "prefix": prefix,
                "dose_ds": cond_local["dose_ds"],
                "dist_ds": cond_local["dist_ds"],
            }

    class DummyZoo:
        def doDataCollection(self, schedule):
            calls.append(schedule)

        def waitTillReady(self):
            pass

    zn.lm = DummyLM()
    zn.zoo = DummyZoo()
    zn.logger = _dummy_logger()

    cond = {
        "mode": "single",
        "dose_ds": 999.0,
        "dist_ds": 999.0,
        "dose_list": "[1, 5]",
        "dist_list": "[120, 110]",
    }

    zn._run_single_dc_loop(
        cond=cond,
        sphi=0.0,
        glist=[[1.0, 2.0, 3.0]],
        flux=1.0e12,
        data_prefix="single",
    )

    assert len(calls) == 2
    assert [(c["dose_ds"], c["dist_ds"]) for c in calls] == [
        (1.0, 120.0),
        (5.0, 110.0),
    ]


def test_goAroundECHA_fetches_pin_and_calls_processLoop(monkeypatch):
    # ECHA package stub
    if "ECHA" not in sys.modules:
        sys.modules["ECHA"] = types.ModuleType("ECHA")

    records = {
        "prep": 0,
        "username": None,
        "context": {},
        "process": [],
    }

    class DummyESAloaderAPI:
        def __init__(self, exid):
            self.exid = exid
            self.calls = 0

        def prep(self):
            records["prep"] += 1

        def get_username(self):
            return "tester"

        def getNextPin(self):
            self.calls += 1
            if self.calls == 1:
                return {
                    "o_index": 11,
                    "p_index": 22,
                    "zoo_samplepin_id": 310,
                }
            return None

        def getCond(self, zoo_samplepin_id):
            assert zoo_samplepin_id == 310
            return {
                "root_dir": "/tmp/test",
                "mode": "single",
                "puckid": "CPS4474",
                "pinid": 7,
                "zoo_samplepin_id": 310,
            }

    esa_mod = types.ModuleType("ECHA.ESAloaderAPI")
    esa_mod.ESAloaderAPI = DummyESAloaderAPI
    sys.modules["ECHA.ESAloaderAPI"] = esa_mod

    class DummyContext:
        def set_zoo_exid(self, exid):
            records["context"]["exid"] = exid

        def set_username(self, username):
            records["context"]["username"] = username

    zc_mod = types.ModuleType("ECHA.ZooContext")
    zc_mod.ZooContext = DummyContext
    sys.modules["ECHA.ZooContext"] = zc_mod

    z = object.__new__(ZooNavigator)
    z.logger = _dummy_logger()
    z.num_pins = 0
    z.time_limit_ds = 9999.0
    z.cleaning_interval_hours = 9999.0
    z.dev = types.SimpleNamespace(zoom=types.SimpleNamespace(zoomOut=lambda: None))
    z.stopwatch = types.SimpleNamespace(
        setTime=lambda *a, **k: None,
        calcTimeFrom=lambda *a, **k: 0.0,
    )
    z.zoo = types.SimpleNamespace(
        cleaning=lambda: None,
        waitSPACE=lambda: None,
    )

    def fake_processLoop(cond, checkEnergyFlag=False, measFlux=False):
        records["process"].append((cond.copy(), checkEnergyFlag))
        z.num_pins += 1

    z.processLoop = fake_processLoop

    got = z.goAroundECHA("EXID-001")

    assert records["prep"] == 1
    assert records["context"] == {
        "exid": "EXID-001",
        "username": "tester",
    }
    assert len(records["process"]) == 1

    cond, flag = records["process"][0]
    assert flag is True
    assert cond["o_index"] == 11
    assert cond["p_index"] == 22
    assert cond["zoo_samplepin_id"] == 310
    assert cond["mode"] == "single"
    assert got == 1
