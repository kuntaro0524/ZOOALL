import importlib.util
import os
import socket
import sys
import types
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path


ROOT = Path(__file__).parents[2]


class _FakeCapture:
    def __init__(self):
        self.disconnected = False

    def disconnect(self):
        self.disconnected = True


class _FailFastSocket:
    def __init__(self, *args, **kwargs):
        raise AssertionError("socket creation during CoaxImage constructor")


class _FailFastMessageServer:
    def sendall(self, *args, **kwargs):
        raise AssertionError("hardware command during CoaxImage constructor")

    def recv(self, *args, **kwargs):
        raise AssertionError("socket receive during CoaxImage constructor")


def _write_fixture(config_dir):
    camera_inf = config_dir / "camera.inf"
    camera_inf.write_text(
        "ZoomOptions1: 1.0 2.0\n"
        "OriginShiftXOptions1: 10.0 20.0\n"
        "OriginShiftYOptions1: 30.0 40.0\n"
    )
    bss_config = config_dir / "bss.config"
    bss_config.write_text("Microscope_Zoom_Options: 100 200\n")
    config_dir.joinpath("beamline.ini").write_text(
        f"""\
[beamline]
beamline = BL32XU

[files]
camera_inf = {camera_inf}
bssconfig_file = {bss_config}

[experiment]
gonio_direction = horizontal

[coaximage]
width = 100.0
height = 200.0
pix_size = 1.5
image_size = 640.0

[inocc]
zoom_pintx = 123

[special_setting]
isDark = false
"""
    )


def _fixture_config(config_dir):
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_dir / "beamline.ini")
    return config


def _install_coaximage_dependencies(monkeypatch):
    capture = types.ModuleType("Capture")
    capture.Capture = _FakeCapture
    monkeypatch.setitem(sys.modules, "Capture", capture)


def _load_module(name):
    path = ROOT / "Libs/CoaxImage.py"
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


def _fake_blf(config):
    device = types.SimpleNamespace(
        isInit=True,
        coax_pint=types.SimpleNamespace(),
        gonio=types.SimpleNamespace(),
        zoom=types.SimpleNamespace(),
    )
    return types.SimpleNamespace(
        ms=_FailFastMessageServer(),
        device=device,
        config=config,
    )


def test_coaximage_constructor_baseline_is_offline_and_preserves_observable_state(
    monkeypatch, tmp_path
):
    """Guarantee CoaxImage construction is offline and behaviorally observable.

    The test guarantees constructor completion, no socket communication, no
    hardware command, no external process, and preservation of config-derived
    image/beamline values, auxiliary-file mappings, and Capture construction.
    """
    _write_fixture(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    monkeypatch.setattr(socket, "socket", _FailFastSocket)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("external process during CoaxImage constructor")
    ))
    _install_coaximage_dependencies(monkeypatch)
    _install_real_zooconfig(monkeypatch)

    module = _load_module("CoaxImage_baseline_under_test")
    image = module.CoaxImage(_fake_blf(_fixture_config(tmp_path)))

    assert image.beamline == "BL32XU"
    assert image.gonio_direction == "horizontal"
    assert image.camera_inf["zoom_opts"] == [1.0, 2.0]
    assert image.bss_config["zoom_pulses"] == [100, 200]
    assert image.coax_pintx_pulse == 123
    assert image.width == 100.0
    assert image.height == 200.0
    assert image.pix_size == 1.5
    assert image.image_size == 640.0
    assert image.isDark is False
    assert isinstance(image.capture, _FakeCapture)

