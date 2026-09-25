import importlib.util
import sys
import types
from pathlib import Path


ZOO_PATH = Path(__file__).parents[2] / "Zoo.py"


class _Config:
    def get(self, section, option):
        assert (section, option) == ("server", "bss_server")
        return "bss-test"

    def getint(self, section, option):
        assert (section, option) == ("server", "bss_port")
        return 12345


def _load_zoo(monkeypatch, calls):
    config_module = types.ModuleType("ZooConfig")
    config_module.get_config_path = lambda: calls.append("path") or \
        "/tmp/zoo-test/beamline.ini"
    config_module.load_config = lambda: calls.append("load") or _Config()
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    exception_module = types.ModuleType("ZooMyException")
    exception_module.ZooMyException = Exception
    monkeypatch.setitem(sys.modules, "ZooMyException", exception_module)

    spec = importlib.util.spec_from_file_location("Zoo_under_test", ZOO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_zoo_uses_shared_loader_and_preserves_constructor_values(monkeypatch):
    calls = []
    module = _load_zoo(monkeypatch, calls)

    zoo = module.Zoo()

    assert calls == ["load"]
    assert zoo.bss_srv == "bss-test"
    assert zoo.bss_port == 12345
    assert zoo.isConnect is False
    assert zoo.isEmu is True
