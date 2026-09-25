import importlib.util
import os
import socket
import sys
import types
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path


ROOT = Path(__file__).parents[2]


def _write_beamline_ini(config_dir):
    config_dir.joinpath("beamline.ini").write_text(
        """\
[beamline]
beamline = BL32XU

[axes]
counter_pin = counter_pin
"""
    )


def _install_count_dependencies(monkeypatch):
    for name in ("Received", "File", "AnalyzePeak"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    bssconfig = types.ModuleType("BSSconfig")

    class FakeBSSconfig:
        def __init__(self):
            pass

        def getBLobject(self):
            return "BL32XU"

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/Count.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during Count constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during Count constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during Count constructor")


def test_count_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee Count construction reads the fixture only.

    This explicitly checks offline completion, no socket communication, no hardware
    command, no external process, and the observable axis/channel state produced by
    the pre-ZooConfig implementation.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during Count constructor")
    ))
    _install_count_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("Count_baseline_under_test")
    count = module.Count(_FailFastServer(), 1, 2)

    assert count.ch1 == 2
    assert count.ch2 == 3
    assert count.ax_name == "bl_BL32XU_counter_pin"
    assert count.is_count == 0


def test_count_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee migration changes only the config-loading delegation."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_count_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("Count_loader_under_test")
    count = module.Count(_FailFastServer(), 1, 2)

    assert calls == ["load"]
    assert count.ax_name == "bl_BL32XU_counter_pin"
