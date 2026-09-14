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
sample_axis = sample_y
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during BaseAxis constructor")


def _install_baseaxis_dependencies(monkeypatch):
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
            assert axis_name == "sample_y"
            return 3.0, 1, 10.0

        def getLightEvacuateInfo(self, axis_name):
            assert axis_name == "sample_y"
            return 20, 30

        def getEvacuateInfo(self, axis_name):
            assert axis_name == "sample_y"
            return 40, 50

        def getEvacuateAxis(self, axis_config):
            raise AssertionError("unexpected evacuate-axis branch in baseline")

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/BaseAxis.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during BaseAxis constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during BaseAxis constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during BaseAxis constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_baseaxis_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee BaseAxis pulse/plc construction is offline and observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of axis naming,
    Motor state, pulse values, and PLC state before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during BaseAxis constructor")
    ))
    _install_baseaxis_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("BaseAxis_baseline_under_test")
    server = _FailFastServer()

    pulse_axis = module.BaseAxis(server, "sample_axis")
    plc_axis = module.BaseAxis(server, "sample_axis", axis_type="plc")

    assert pulse_axis.s is server
    assert pulse_axis.axis_name == "sample_y"
    assert pulse_axis.full_axis_name == "bl_BL32XU_sample_y"
    assert pulse_axis.motor.motor == "bl_BL32XU_sample_y"
    assert pulse_axis.v2p == 3.0
    assert pulse_axis.sense == 1
    assert pulse_axis.home == 10.0
    assert pulse_axis.on_pulse == 20
    assert pulse_axis.off_pulse == 30
    assert plc_axis.axis_name == "sample_y"
    assert plc_axis.full_axis_name == "bl_BL32XU_sample_y"
    assert not hasattr(plc_axis, "motor")


def test_baseaxis_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee BaseAxis migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_baseaxis_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("BaseAxis_loader_under_test")
    axis = module.BaseAxis(_FailFastServer(), "sample_axis")

    assert calls == ["load"]
    assert axis.axis_name == "sample_y"
