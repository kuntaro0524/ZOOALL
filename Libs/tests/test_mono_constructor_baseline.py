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
mono_dtheta1_axis = mono_dtheta1
mono_dtheta1_unit = pulse
mono_theta_axis = mono_theta
mono_theta_unit = degree
mono_energy_axis = mono_energy
mono_energy_unit = keV
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during Mono constructor")


def _install_mono_dependencies(monkeypatch):
    for name in ("AnalyzePeak", "AxesInfo", "ZooMyException"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    motor = types.ModuleType("Motor")
    motor.Motor = _FakeMotor
    monkeypatch.setitem(sys.modules, "Motor", motor)

    tcs = types.ModuleType("TCS")
    tcs.os = os
    monkeypatch.setitem(sys.modules, "TCS", tcs)

    bssconfig = types.ModuleType("BSSconfig")

    class FakeBSSconfig:
        def __init__(self):
            pass

        def getBLobject(self):
            return "BL32XU"

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/Mono.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during Mono constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during Mono constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during Mono constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_mono_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee Mono construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of all three axis
    names/units and the server reference before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during Mono constructor")
    ))
    _install_mono_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("Mono_baseline_under_test")
    server = _FailFastServer()
    mono = module.Mono(server)

    assert mono.s is server
    assert mono.m_dtheta1.motor == "mono_dtheta1"
    assert mono.m_dtheta1.unit == "pulse"
    assert mono.m_theta.motor == "mono_theta"
    assert mono.m_theta.unit == "degree"
    assert mono.m_energy.motor == "mono_energy"
    assert mono.m_energy.unit == "keV"


def test_mono_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee Mono migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_mono_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def get_config_path():
        calls.append("path")
        return str(tmp_path / "beamline.ini")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.get_config_path = get_config_path
    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("Mono_loader_under_test")
    mono = module.Mono(_FailFastServer())

    assert calls == ["path", "load"]
    assert mono.m_energy.motor == "mono_energy"
