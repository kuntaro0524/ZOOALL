import importlib.util
import sys
import types
from pathlib import Path


BLFACTORY_PATH = Path(__file__).parents[1] / "BLFactory.py"


class _Config:
    def get(self, section, option):
        values = {
            ("beamline", "beamline"): "BLTEST",
            ("server", "bss_server"): "bss-test",
            ("server", "blanc_address"): "blanc-test",
        }
        return values[(section, option)]


def _load_blfactory(monkeypatch, calls):
    config_module = types.ModuleType("ZooConfig")
    config_module.get_config_path = lambda: calls.append("path") or \
        "/tmp/zoo-test/beamline.ini"
    config_module.load_config = lambda: calls.append("load") or _Config()

    bss_module = types.ModuleType("BSSconfig")
    bss_module.BSSconfig = lambda: calls.append("bss") or object()

    stubs = {
        "Zoo": types.ModuleType("Zoo"),
        "Device": types.ModuleType("Device"),
        "Gonio44": types.ModuleType("Gonio44"),
        "Gonio": types.ModuleType("Gonio"),
        "BSSconfig": bss_module,
        "ZooConfig": config_module,
    }
    for name, module in stubs.items():
        monkeypatch.setitem(sys.modules, name, module)

    spec = importlib.util.spec_from_file_location("BLFactory_under_test", BLFACTORY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blfactory_uses_shared_loader_without_changing_constructor_config(
    monkeypatch,
):
    calls = []
    module = _load_blfactory(monkeypatch, calls)

    factory = module.BLFactory()

    assert calls == ["path", "load", "bss"]
    assert factory.config.get("beamline", "beamline") == "BLTEST"
    assert factory.beamline == "BLTEST"
    assert factory.bss_server == "bss-test"
    assert factory.blanc_address == "blanc-test"
