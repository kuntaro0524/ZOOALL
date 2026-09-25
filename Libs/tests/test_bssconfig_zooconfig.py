import importlib.util
import sys
import types
from pathlib import Path


BSSCONFIG_PATH = Path(__file__).parents[1] / "BSSconfig.py"


class _Config:
    def get(self, section, option):
        values = {
            ("files", "bssconfig_file"): "/tmp/bss.config",
            ("files", "camera_inf"): "/tmp/camera.inf",
        }
        return values[(section, option)]


def _load_bssconfig(monkeypatch, calls):
    config_module = types.ModuleType("ZooConfig")
    config_module.get_config_path = lambda: calls.append("path") or \
        "/tmp/zoo-test/beamline.ini"
    config_module.load_config = lambda: calls.append("load") or _Config()
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    spec = importlib.util.spec_from_file_location(
        "BSSconfig_under_test", BSSCONFIG_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bssconfig_uses_shared_loader_and_preserves_config_attributes(monkeypatch):
    calls = []
    module = _load_bssconfig(monkeypatch, calls)

    config = module.BSSconfig()

    assert calls == ["path", "load"]
    assert config.inifile_path == "/tmp/zoo-test/beamline.ini"
    assert config.confile == "/tmp/bss.config"
    assert config.camerainf_path == "/tmp/camera.inf"
