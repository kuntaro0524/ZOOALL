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
zoom_x_axis = zoom_x
"""
    )


class _FakeMotor:
    def __init__(self, server, motor, unit):
        self.server = server
        self.motor = motor
        self.unit = unit

    def __getattr__(self, name):
        raise AssertionError(f"hardware method {name} during Zoom constructor")


def _install_zoom_dependencies(monkeypatch):
    bssconfig = types.ModuleType("BSSconfig")

    class FakeBSSconfig:
        def __init__(self):
            pass

        def getBLobject(self):
            return "BL32XU"

        def getPulse4MinZoomRatio(self):
            return -1234

    bssconfig.BSSconfig = FakeBSSconfig
    monkeypatch.setitem(sys.modules, "BSSconfig", bssconfig)

    motor = types.ModuleType("Motor")
    motor.Motor = _FakeMotor
    monkeypatch.setitem(sys.modules, "Motor", motor)


def _load_module(name):
    path = ROOT / "Libs/Zoom.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during Zoom constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during Zoom constructor")


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during Zoom constructor")


def _install_real_zooconfig(monkeypatch):
    path = ROOT / "Libs/ZooConfig.py"
    spec = importlib.util.spec_from_file_location("ZooConfig_for_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


def test_zoom_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee Zoom construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of the axis name,
    server reference, pulse minimum, and initial limits before migration.
    """
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during Zoom constructor")
    ))
    _install_zoom_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("Zoom_baseline_under_test")
    server = _FailFastServer()
    zoom = module.Zoom(server)

    assert zoom.s is server
    assert zoom.axis_name == "bl_BL32XU_zoom_x"
    assert zoom.zoom.motor == "bl_BL32XU_zoom_x"
    assert zoom.zoom.unit == "pulse"
    assert zoom.pulse_minzoom == -1234
    assert zoom.in_lim == "0"


def test_zoom_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    """Guarantee Zoom migration delegates only configuration loading."""
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    _install_zoom_dependencies(monkeypatch)

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module("Zoom_loader_under_test")
    zoom = module.Zoom(_FailFastServer())

    assert calls == ["load"]
    assert zoom.axis_name == "bl_BL32XU_zoom_x"
