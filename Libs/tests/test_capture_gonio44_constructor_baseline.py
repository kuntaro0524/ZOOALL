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

[capture]
contrast_default = 11
bright_default = 22
gain_default = 33
bright_default_dark = 44
gain_default_dark = 55

[special_setting]
isDark = false
"""
    )


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_real_zooconfig(monkeypatch):
    module = _load_module(ROOT / "Libs/ZooConfig.py", "ZooConfig_for_test")
    monkeypatch.setitem(sys.modules, "ZooConfig", module)


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during constructor")


class _FailFastServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("sendall during constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("recv during constructor")


def test_capture_constructor_has_no_socket_or_process_side_effects(
    monkeypatch, tmp_path
):
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setenv("USER", "offline-test")
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during constructor")
    ))
    _install_real_zooconfig(monkeypatch)

    module = _load_module(ROOT / "Libs/Capture.py", "Capture_baseline_under_test")
    capture = module.Capture()

    assert capture.user == "offline-test"
    assert capture.open_sig is False
    assert capture.isPrep is False
    assert capture.contrast_default == 11
    assert capture.bright_default == 22
    assert capture.gain_default == 33
    assert capture.isDark is False


def test_capture_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setenv("USER", "offline-test")

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module(ROOT / "Libs/Capture.py", "Capture_loader_under_test")
    capture = module.Capture()

    assert calls == ["load"]
    assert capture.contrast_default == 11


def test_gonio44_constructor_has_no_socket_or_hardware_side_effects(
    monkeypatch, tmp_path
):
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)

    for name in ("Motor", "BSSconfig", "Zoo"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    _install_real_zooconfig(monkeypatch)

    module = _load_module(ROOT / "Libs/Gonio44.py", "Gonio44_baseline_under_test")
    server = _FailFastServer()
    gonio = module.Gonio44(server)

    assert gonio.s is server
    assert gonio.beamline == "BL32XU"
    assert gonio.debug is False


def test_gonio44_constructor_uses_zooconfig_loader(monkeypatch, tmp_path):
    _write_beamline_ini(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))

    for name in ("Motor", "BSSconfig", "Zoo"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    calls = []
    config_module = types.ModuleType("ZooConfig")

    def load_config():
        calls.append("load")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(tmp_path / "beamline.ini")
        return config

    config_module.load_config = load_config
    monkeypatch.setitem(sys.modules, "ZooConfig", config_module)

    module = _load_module(ROOT / "Libs/Gonio44.py", "Gonio44_loader_under_test")
    gonio = module.Gonio44(_FailFastServer())

    assert calls == ["load"]
    assert gonio.beamline == "BL32XU"
