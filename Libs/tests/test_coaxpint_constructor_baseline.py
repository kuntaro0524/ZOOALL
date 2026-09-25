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
coax_x_axis = coax_x
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during CoaxPint constructor")


def _install_coaxpint_dependencies(monkeypatch):
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
            assert axis_name == "coax_x"
            return 2.0, -1, 100.0

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/CoaxPint.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during CoaxPint constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during CoaxPint constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during CoaxPint constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_coaxpint_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee CoaxPint construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of the axis,
    server, unit, and BSS pulse values before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during CoaxPint constructor")
    ))
    _install_coaxpint_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("CoaxPint_baseline_under_test")
    server = _FailFastServer()
    coax = module.CoaxPint(server)

    assert coax.s is server
    assert coax.coax_name == "coax_x"
    assert coax.coaxx.motor == "bl_BL32XU_coax_x"
    assert coax.coaxx.unit == "pulse"
    assert coax.v2p == 2.0
    assert coax.sense == -1
    assert coax.home == 100.0


def test_coaxpint_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee CoaxPint migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_coaxpint_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("CoaxPint_loader_under_test")
    coax = module.CoaxPint(_FailFastServer())

    assert calls == ["load"]
    assert coax.coax_name == "coax_x"
