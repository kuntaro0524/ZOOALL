import pandas as pd
from configparser import ConfigParser
from UserESA import UserESA


def make_useresa_for_setdefaults():
    u = UserESA.__new__(UserESA)
    u.config = ConfigParser()
    u.config.add_section("experiment")
    u.config.set("experiment", "score_min", "10")
    u.config.set("experiment", "score_max", "200")
    u.config.set("experiment", "raster_dose", "0.1")
    u.config.set("experiment", "dose_ds", "5.0")
    u.config.set("experiment", "raster_roi", "1")
    u.config.set("experiment", "exp_ds", "0.02")
    u.config.set("experiment", "exp_raster", "0.01")
    u.config.set("experiment", "att_raster", "50.0")
    u.config.set("experiment", "cover_flag", "1")

    u.root_dir = "."
    u.fname = "dummy.xlsx"
    return u


def test_setdefaults_scan_only_sets_both_score_min_and_score_max_to_9999():
    u = make_useresa_for_setdefaults()

    u.df = pd.DataFrame([
        {"desired_exp": "scan_only", "mode": "single", "score_max": 321, "max_crystal_size": 20.0},
        {"desired_exp": "scan_only", "mode": "multi",  "score_max": 654, "max_crystal_size": 20.0},
        {"desired_exp": "normal",    "mode": "single", "score_max": 777, "max_crystal_size": 20.0},
    ])

    u.setDefaults()

    assert u.df.loc[0, "score_min"] == 9999
    assert u.df.loc[0, "score_max"] == 9999
    assert u.df.loc[1, "score_min"] == 9999
    assert u.df.loc[1, "score_max"] == 9999
    assert u.df.loc[2, "score_max"] == 777
