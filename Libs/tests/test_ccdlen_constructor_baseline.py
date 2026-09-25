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
[axes]
ccdlen = ccdlen_axis
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during CCDlen constructor")


def _install_ccdlen_dependencies(monkeypatch):
    monkeypatch.setitem(sys.modules, "Received", types.ModuleType("Received"))

    motor = types.ModuleType("Motor")
    motor.Motor = _FakeMotor
    monkeypatch.setitem(sys.modules, "Motor", motor)

    bssconfig = types.ModuleType("BSSconfig")

    class FakeBSSconfig:
        def __init__(self):
            pass

        def getBLobject(self):
            return "BL32XU"

        def getPulseInfo(self, axis_name):
            assert axis_name == "ccdlen_axis"
            return 4.0, -1, 120.0

        def getLimit(self, axis_name):
            assert axis_name == "ccdlen_axis"
            return 110.0, 600.0

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/CCDlen.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during CCDlen constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during CCDlen constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during CCDlen constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_ccdlen_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee CCDlen construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of the axis,
    Motor, pulse, and limit state before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during CCDlen constructor")
    ))
    _install_ccdlen_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("CCDlen_baseline_under_test")
    server = _FailFastServer()
    ccdlen = module.CCDlen(server)

    assert ccdlen.s is server
    assert ccdlen.ccdlen_name == "ccdlen_axis"
    assert ccdlen.ccdlen.motor == "bl_BL32XU_ccdlen_axis"
    assert ccdlen.ccdlen.unit == "pulse"
    assert ccdlen.ccdlen_v2p == 4.0
    assert ccdlen.ccdlen_sense == -1
    assert ccdlen.ccdlen_home == 120.0
    assert ccdlen.low_limit == 110.0
    assert ccdlen.upper_limit == 600.0
    assert ccdlen.isInit is False


def test_ccdlen_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee CCDlen migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_ccdlen_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("CCDlen_loader_under_test")
    ccdlen = module.CCDlen(_FailFastServer())

    assert calls == ["load"]
    assert ccdlen.ccdlen_name == "ccdlen_axis"
