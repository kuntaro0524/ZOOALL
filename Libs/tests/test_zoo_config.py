import configparser

import pytest

from Libs import ZooConfig


def _write_fixture_config(config_dir):
    config_path = config_dir / "beamline.ini"
    config_path.write_text(
        "[beamline]\n"
        "beamline = BLTEST\n"
        "[dirs]\n"
        "zooroot = /tmp/zoo-test\n"
        "logdir = ${dirs:zooroot}/Logs\n"
        "[server]\n"
        "bss_port = 5555\n",
        encoding="utf-8",
    )
    return config_path


def _legacy_load_config(config_path):
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    read_result = config.read(str(config_path))
    return config, read_result


def test_get_config_path_uses_zooconfigpath(tmp_path, monkeypatch):
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))

    assert ZooConfig.get_config_path() == str(tmp_path / "beamline.ini")


def test_load_config_reads_beamline_ini_and_expands_interpolation(
    tmp_path, monkeypatch
):
    _write_fixture_config(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))

    config = ZooConfig.load_config()

    assert config.get("beamline", "beamline") == "BLTEST"
    assert config.get("dirs", "logdir") == "/tmp/zoo-test/Logs"
    assert config.getint("server", "bss_port") == 5555


def test_load_config_matches_legacy_loading(tmp_path, monkeypatch):
    config_path = _write_fixture_config(tmp_path)
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))

    legacy, legacy_read_result = _legacy_load_config(config_path)
    current = ZooConfig.load_config()

    assert legacy_read_result == [str(config_path)]
    assert current.sections() == legacy.sections()
    assert current.get("beamline", "beamline") == legacy.get(
        "beamline", "beamline"
    )
    assert current.get("dirs", "logdir") == legacy.get("dirs", "logdir")
    assert current.getint("server", "bss_port") == legacy.getint(
        "server", "bss_port"
    )


def test_unset_zooconfigpath_keeps_keyerror(monkeypatch):
    monkeypatch.delenv("ZOOCONFIGPATH", raising=False)

    with pytest.raises(KeyError, match="ZOOCONFIGPATH"):
        ZooConfig.get_config_path()

    with pytest.raises(KeyError, match="ZOOCONFIGPATH"):
        ZooConfig.load_config()


def test_missing_beamline_ini_matches_configparser_read(tmp_path, monkeypatch):
    monkeypatch.setenv("ZOOCONFIGPATH", str(tmp_path))
    missing_path = tmp_path / "beamline.ini"

    legacy, legacy_read_result = _legacy_load_config(missing_path)
    current = ZooConfig.load_config()

    assert legacy_read_result == []
    assert legacy.sections() == []
    assert current.sections() == legacy.sections()
