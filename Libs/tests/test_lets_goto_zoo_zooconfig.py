import importlib.util
import sys
import types
from pathlib import Path


LAUNCHER_PATH = Path(__file__).parents[2] / "lets_goto_zoo.py"


class _Config:
    def get(self, section, option):
        values = {
            ("dirs", "zoologdir"): "/tmp/zoo-logs",
            ("beamline", "beamline"): "BLTEST",
            ("server", "blanc_address"): "blanc-test",
            ("files", "logging_conf"): "/tmp/logging.conf",
        }
        return values[(section, option)]


def _load_launcher(monkeypatch, calls):
    config_module = types.ModuleType("Libs.ZooConfig")
    config_module.get_config_path = lambda: calls.append("path") or \
        "/tmp/zoo-test/beamline.ini"
    config_module.load_config = lambda: calls.append("load") or _Config()
    libs_module = sys.modules["Libs"]
    monkeypatch.setitem(sys.modules, "Libs.ZooConfig", config_module)
    monkeypatch.setattr(libs_module, "ZooConfig", config_module, raising=False)

    module_names = [
        "Zoo", "ZooNavigator", "ZooMyException", "MyDate", "BLFactory",
    ]
    for name in module_names:
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    spec = importlib.util.spec_from_file_location(
        "lets_goto_zoo_under_test", LAUNCHER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launcher_uses_shared_loader_and_preserves_import_time_globals(monkeypatch):
    calls = []
    module = _load_launcher(monkeypatch, calls)

    assert calls == ["path", "load"]
    assert module.config_path == "/tmp/zoo-test/beamline.ini"
    assert module.zoologdir == "/tmp/zoo-logs"
    assert module.beamline == "BLTEST"
    assert module.blanc_address == "blanc-test"
    assert module.logging_conf == "/tmp/logging.conf"
