import logging
from unittest.mock import patch
from UserESA import UserESA


class DummyBeamsizeConfig:
    def __init__(self):
        pass


def fake_config_get(self, section, option, *args, **kwargs):
    if section == "beamline" and option == "beamline":
        return "BL32XU"
    raise AssertionError(f"unexpected get({section!r}, {option!r})")


def test_useresa_does_not_duplicate_logger_handlers():
    logger = logging.getLogger("ZOO")
    logger.handlers.clear()

    with patch.dict("os.environ", {"ZOOCONFIGPATH": "/tmp"}):
        with patch("configparser.ConfigParser.read", return_value=None):
            with patch("configparser.ConfigParser.get", new=fake_config_get):
                with patch("BeamsizeConfig.BeamsizeConfig", DummyBeamsizeConfig):
                    u1 = UserESA(fname="a.xlsx", root_dir=".")
                    n1 = len(logger.handlers)

                    u2 = UserESA(fname="b.xlsx", root_dir=".")
                    n2 = len(logger.handlers)

    assert n1 == 2
    assert n2 == 2
