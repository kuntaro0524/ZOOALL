import importlib.util
import sys
import types
from pathlib import Path


ZOONAVIGATOR_PATH = Path(__file__).parents[2] / "ZooNavigator.py"


class _Config:
    def get(self, section, option):
        values = {
            ("files", "bssconfig_file"): "/tmp/bss.config",
            ("dirs", "backimage_dir"): "/tmp/back-images",
            ("beamline", "beamline"): "BLTEST",
        }
        return values[(section, option)]

    def getboolean(self, section, option):
        values = {
            ("ECHA", "isECHA"): False,
            ("special_setting", "isDark"): False,
        }
        return values[(section, option)]

    def getint(self, section, option):
        assert (section, option) == ("capture", "back_mean_thresh")
        return 12


def _load_zoonavigator(monkeypatch, calls):
    config_module = types.ModuleType("Libs.ZooConfig")
    config_module.load_config = lambda: calls.append("load") or _Config()
    libs_module = sys.modules["Libs"]
    monkeypatch.setitem(sys.modules, "Libs.ZooConfig", config_module)
    monkeypatch.setattr(libs_module, "ZooConfig", config_module, raising=False)

    bss_module = types.ModuleType("Libs.BSSconfig")
    monkeypatch.setitem(sys.modules, "Libs.BSSconfig", bss_module)
    monkeypatch.setattr(libs_module, "BSSconfig", bss_module, raising=False)

    module_names = [
        "Zoo", "AttFactor", "LoopMeasurement", "BeamsizeConfig", "StopWatch",
        "Device", "HEBI", "DumpRecover", "AnaHeatmap", "ESA", "KUMA",
        "CrystalList", "MyDate", "DiffscanMaster", "cv2",
    ]
    for name in module_names:
        module = types.ModuleType(name)
        monkeypatch.setitem(sys.modules, name, module)

    att_module = sys.modules["AttFactor"]
    att_module.AttFactor = lambda *args: object()
    dump_module = sys.modules["DumpRecover"]
    dump_module.DumpRecover = lambda *args: object()
    stopwatch_module = sys.modules["StopWatch"]
    stopwatch_module.StopWatch = lambda *args: object()

    exception_module = types.ModuleType("ZooMyException")
    monkeypatch.setitem(sys.modules, "ZooMyException", exception_module)
    html_module = types.ModuleType("html_log_maker")
    html_module.ZooHtmlLog = type("ZooHtmlLog", (), {})
    monkeypatch.setitem(sys.modules, "html_log_maker", html_module)
    error_module = types.ModuleType("ErrorCode")
    error_module.ErrorCode = type("ErrorCode", (), {})
    monkeypatch.setitem(sys.modules, "ErrorCode", error_module)

    spec = importlib.util.spec_from_file_location(
        "ZooNavigator_under_test", ZOONAVIGATOR_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_zoonavigator_uses_shared_loader_and_preserves_config_values(monkeypatch):
    calls = []
    module = _load_zoonavigator(monkeypatch, calls)
    blf = types.SimpleNamespace(
        zoo=object(), ms=object(), device=object()
    )

    navigator = module.ZooNavigator(blf)

    assert calls == ["load"]
    assert navigator.config_file == "/tmp/bss.config"
    assert navigator.backimage_dir == "/tmp/back-images"
    assert navigator.beamline == "BLTEST"
    assert navigator.back_mean_thresh == 12
    assert navigator.isECHA is False
