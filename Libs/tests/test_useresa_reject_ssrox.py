from configparser import ConfigParser
import pytest
from UserESA import UserESA


def make_useresa():
    u = UserESA.__new__(UserESA)
    u.config = ConfigParser()
    u.config.add_section("experiment")
    u.config.set("experiment", "score_min", "10")
    u.config.set("experiment", "score_max", "200")
    u.config.set("experiment", "raster_dose", "0.1")
    u.config.set("experiment", "dose_ds", "5.0")
    u.config.set("experiment", "raster_roi", "1")
    u.config.set("experiment", "exp_raster", "0.01")
    u.config.set("experiment", "att_raster", "50.0")
    u.config.set("experiment", "hebi_att", "50.0")
    u.config.set("experiment", "cover_flag", "1")
    return u


def test_ssrox_is_rejected():
    u = make_useresa()

    with pytest.raises(ValueError):
        u.getParams("normal", "ssrox")
