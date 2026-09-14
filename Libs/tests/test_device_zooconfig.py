import importlib.util
import sys
import types
from pathlib import Path


DEVICE_PATH = Path(__file__).parents[1] / "Device.py"


class _Config:
    def getint(self, section, option):
        assert (section, option) == ("experiment", "pin_channel")
        return 7

    def get(self, section, option):
        values = {
            ("inocc", "zoom_pintx"): "1234",
            ("beamline", "beamline"): "BLTEST",
        }
        return values[(section, option)]


def _load_device(monkeypatch, calls):
    config_module = types.ModuleType("ZooConfig")
    config_module.load_config = lambda: calls.append("load") or _Config()
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    singleton_module = types.ModuleType("Singleton")
    singleton_module.Singleton = type("Singleton", (), {})
    monkeypatch.setitem(sys.modules, "Singleton", singleton_module)

    module_names = [
        "File", "Capture", "Count", "Mono", "ConfigFile", "Zoom", "ExSlit1",
        "ID", "AnalyzePeak", "Colli", "Cover", "CCDlen", "CoaxPint", "MBS",
        "DSS", "BeamsizeConfig", "Flux", "PreColli",
    ]
    for name in module_names:
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    websocket_module = types.ModuleType("WebSocketBSS")
    websocket_module.WebSocketBSS = lambda: object()
    monkeypatch.setitem(sys.modules, "WebSocketBSS", websocket_module)

    exception_module = types.ModuleType("ZooMyException")
    exception_module.MyException = Exception
    monkeypatch.setitem(sys.modules, "ZooMyException", exception_module)

    spec = importlib.util.spec_from_file_location("Device_under_test", DEVICE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_device_uses_shared_loader_and_preserves_constructor_values(monkeypatch):
    calls = []
    module = _load_device(monkeypatch, calls)
    ms_port = object()

    device = module.Device(ms_port)

    assert calls == ["load"]
    assert device.s is ms_port
    assert device.config.getint("experiment", "pin_channel") == 7
    assert device.coax_pintx_pulse == 1234
    assert device.beamline == "BLTEST"
