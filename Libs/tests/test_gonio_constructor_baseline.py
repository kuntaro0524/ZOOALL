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
gonio_x_name = gonio_x
gonio_y_name = gonio_y
gonio_z_name = gonio_z
gonio_zz_name = gonio_zz
gonio_rot_name = gonio_phi
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during Gonio constructor")


def _install_gonio_dependencies(monkeypatch):
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
            values = {
                "gonio_x": (1.0, 1, 10.0),
                "gonio_y": (2.0, -1, 20.0),
                "gonio_z": (3.0, 1, 30.0),
                "gonio_zz": (4.0, -1, 40.0),
                "gonio_phi": (5.0, 1, 50.0),
            }
            return values[axis_name]

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/Gonio.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during Gonio constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during Gonio constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during Gonio constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_gonio_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee Gonio construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of all five axis
    names, Motor units, pulse values, beamline, and preparation state.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during Gonio constructor")
    ))
    _install_gonio_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("Gonio_baseline_under_test")
    server = _FailFastServer()
    gonio = module.Gonio(server)

    assert gonio.s is server
    assert gonio.beamline == "BL32XU"
    for motor, name, unit in (
        (gonio.goniox, "gonio_x", "pulse"),
        (gonio.gonioy, "gonio_y", "pulse"),
        (gonio.gonioz, "gonio_z", "pulse"),
        (gonio.goniozz, "gonio_zz", "pulse"),
        (gonio.phi, "gonio_phi", "pulse"),
    ):
        assert motor.motor == f"bl_BL32XU_{name}"
        assert motor.unit == unit
    assert (gonio.v2p_x, gonio.sense_x, gonio.home_x) == (1.0, 1, 10.0)
    assert (gonio.v2p_y, gonio.sense_y, gonio.home_y) == (2.0, -1, 20.0)
    assert (gonio.v2p_z, gonio.sense_z, gonio.home_z) == (3.0, 1, 30.0)
    assert (gonio.v2p_zz, gonio.sense_zz, gonio.home_zz) == (4.0, -1, 40.0)
    assert (gonio.v2p_rot, gonio.sense_phi, gonio.home_phi) == (5.0, 1, 50.0)
    assert gonio.isPrep is True


def test_gonio_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee Gonio migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_gonio_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("Gonio_loader_under_test")
    gonio = module.Gonio(_FailFastServer())

    assert calls == ["load"]
    assert gonio.beamline == "BL32XU"
