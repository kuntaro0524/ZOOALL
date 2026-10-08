import importlib.util
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALLER_PATH = REPO_ROOT / "docs" / "operations" / "configure-local-runtime.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("configure_local_runtime", INSTALLER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install(monkeypatch, destination, *extra_args):
    installer = load_installer()
    monkeypatch.setattr(
        "sys.argv",
        [str(INSTALLER_PATH), *extra_args, str(destination)],
    )
    installer.main()


def write_profile(destination, name, python_path, kunpy_root, zoo_root):
    profile = destination / "profiles" / "{}.conf".format(name)
    profile.write_text(
        "ZOO_BASE_PYTHON={}\nKUNPY_ROOT={}\nZOO_ROOT={}\n".format(
            python_path, kunpy_root, zoo_root
        )
    )


def make_fake_runtime(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\"\nprintf 'QB=%s\\n' \"$QB_PYTHONPATH\"\nprintf 'CFG=%s\\n' \"${ZOOCONFIGPATH:-}\"\n")
    fake_python.chmod(0o755)
    kunpy_root = tmp_path / "kunpy"
    zoo_root = tmp_path / "zoo"
    (kunpy_root / "Libs").mkdir(parents=True)
    (zoo_root / "Libs").mkdir(parents=True)
    return fake_python, kunpy_root, zoo_root


def test_installed_bundle_uses_local_profile_after_move(tmp_path, monkeypatch):
    destination = tmp_path / "first-location"
    install(monkeypatch, destination)
    fake_python, kunpy_root, zoo_root = make_fake_runtime(tmp_path)
    write_profile(destination, "test", fake_python, kunpy_root, zoo_root)

    moved = tmp_path / "moved-location"
    destination.rename(moved)
    result = subprocess.run(
        [str(moved / "bin" / "zpython"), "--profile", "test", "-c", "pass"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "-c\npass\n" in result.stdout
    assert "{}:{}:{}:{}".format(zoo_root, zoo_root / "Libs", kunpy_root, kunpy_root / "Libs") in result.stdout


def test_config_is_explicit_and_must_contain_beamline_ini(tmp_path, monkeypatch):
    destination = tmp_path / "runtime"
    install(monkeypatch, destination)
    fake_python, kunpy_root, zoo_root = make_fake_runtime(tmp_path)
    write_profile(destination, "test", fake_python, kunpy_root, zoo_root)

    missing = subprocess.run(
        [str(destination / "bin" / "zpython"), "--profile", "test", "--config", str(tmp_path / "missing"), "-c", "pass"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 2
    assert "beamline.ini does not exist" in missing.stderr

    config = tmp_path / "config"
    config.mkdir()
    (config / "beamline.ini").write_text("[beamline]\nbeamline = TEST\n")
    accepted = subprocess.run(
        [str(destination / "bin" / "zpython"), "--profile", "test", "--config", str(config), "-c", "pass"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert accepted.returncode == 0
    assert "CFG={}\n".format(config) in accepted.stdout


def test_reinstall_refuses_before_replacing_any_launcher(tmp_path, monkeypatch):
    destination = tmp_path / "runtime"
    install(monkeypatch, destination)
    marker = destination / "bin" / "zpython"
    marker.write_text("local change\n")

    try:
        install(monkeypatch, destination)
    except SystemExit as error:
        assert "Refusing to replace existing launcher" in str(error)
    else:
        raise AssertionError("installer unexpectedly replaced existing launchers")

    assert marker.read_text() == "local change\n"


def test_replace_launchers_preserves_profiles(tmp_path, monkeypatch):
    destination = tmp_path / "runtime"
    install(monkeypatch, destination)
    local_profile = destination / "profiles" / "local.conf"
    local_profile.write_text("LOCAL_ONLY=yes\n")
    (destination / "bin" / "zpython").write_text("old launcher\n")

    install(monkeypatch, destination, "--replace-launchers")

    assert local_profile.read_text() == "LOCAL_ONLY=yes\n"
    assert (destination / "bin" / "zpython").read_text().startswith("#!/bin/bash")
