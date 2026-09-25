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
precol_y_name = precol_y
precol_z_name = precol_z
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during PreColli constructor")


def _install_precolli_dependencies(monkeypatch):
    for name in ("Received", "ZooMyException"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

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
                "precol_y": (1.5, 1, 10.0),
                "precol_z": (2.5, -1, 20.0),
            }
            return values[axis_name]

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)


def _load_module(name):
    path = ROOT / "Libs/PreColli.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during PreColli constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during PreColli constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during PreColli constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_precolli_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee PreColli construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of both conditional
    Motor axes and pulse values before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during PreColli constructor")
    ))
    _install_precolli_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("PreColli_baseline_under_test")
    server = _FailFastServer()
    colli = module.PreColli(server)

    assert colli.s is server
    assert colli.pcoly_axis == "precol_y"
    assert colli.pcolz_axis == "precol_z"
    assert colli.pcoly.motor == "bl_BL32XU_precol_y"
    assert colli.pcolz.motor == "bl_BL32XU_precol_z"
    assert colli.v2p_y == 1.5
    assert colli.sense_y == 1
    assert colli.home_y == 10.0
    assert colli.v2p_z == 2.5
    assert colli.sense_z == -1
    assert colli.home_z == 20.0
    assert colli.isInit is True


def test_precolli_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee PreColli migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_precolli_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("PreColli_loader_under_test")
    colli = module.PreColli(_FailFastServer())

    assert calls == ["load"]
    assert colli.pcoly_axis == "precol_y"
