import logging
import pandas as pd
import pytest

import UserESA as UEModule


class DummyBeamSizeConf:
    def getFluxAtWavelength(self, hbeam, vbeam, wavelength):
        return 1.0e12


@pytest.fixture
def bare_useresa(tmp_path, monkeypatch):
    ue = UEModule.UserESA.__new__(UEModule.UserESA)

    ue.debug = True
    ue.isDoseError = False
    ue.root_dir = str(tmp_path)
    ue.fname = "dummy.xlsx"
    ue.csv_prefix = "dummy"
    ue.logger = logging.getLogger("test.useresa")
    ue.bsconf = DummyBeamSizeConf()
    ue.dose_distance_handler = UEModule.DoseDistanceHandler(ue.logger, debug=True)

    class DummyConfig:
        def getfloat(self, section, option):
            table = {
                ("experiment", "score_min"): 10.0,
                ("experiment", "score_max"): 100.0,
                ("experiment", "raster_dose"): 0.1,
                ("experiment", "dose_ds"): 10.0,
                ("experiment", "exp_ds"): 0.02,
                ("experiment", "exp_raster"): 0.02,
                ("experiment", "att_raster"): 10.0,
                ("experiment", "hebi_att"): 10.0,
                ("experiment", "resol_raster"): 3.0,
                ("experiment", "max_hori_scan_speed"): 1000.0,
                ("detector", "min_camera_len"): 100.0,
                ("detector", "min_camera_dim"): 100.0,
                ("experiment", "raster_roi_edge_mm"): 25.0,
            }
            return table[(section, option)]

        def getint(self, section, option):
            table = {
                ("experiment", "raster_roi"): 0,
                ("experiment", "cover_flag"): 0,
            }
            return table[(section, option)]

        def get(self, section, option):
            table = {
                ("beamline", "beamline"): "BL32XU",
            }
            return table[(section, option)]

    ue.config = DummyConfig()
    ue.beamline = "BL32XU"

    return ue


def test_defineScanCondition_normal_path(bare_useresa):
    ue = bare_useresa

    ue.df = pd.DataFrame([
        {
            "puckid": "PK1",
            "pinid": 1,
            "sample_name": "SAMPLE1",
            "desired_exp": "normal",
            "mode": "single",
            "wavelength": 1.0,
            "resolution_limit": 2.0,
            "beamsize": "10x10",
            "max_crystal_size": 30.0,
            "maxhits": 10,
            "total_osc": 10.0,
            "osc_width": 0.1,
            "ln2_flag": 0,
            "pin_flag": "spine",
            "zoomcap_flag": 0,
            "confirmation_require": 0,
            "dose_list": "",
            "dist_list": "",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "raster_hbeam": 10.0,
            "raster_vbeam": 10.0,
            "flux": 1.0e12,
            "exp_raster": 0.02,
            "exp_ds": 0.02,
            "dose_ds": 10.0,
            "reduced_fact": 1.0,
            "ntimes": 1,
        }
    ])

    ue.defineScanCondition()

    assert "att_raster" in ue.df.columns
    assert "hebi_att" in ue.df.columns
    assert "ppf_raster" in ue.df.columns
    assert "dose_per_frame" in ue.df.columns
    assert "dose_ds" in ue.df.columns

    row = ue.df.iloc[0]
    assert row["att_raster"] > 0
    assert row["dose_per_frame"] > 0
    assert row["dose_ds"] >= 0


def test_defineScanCondition_extended_dose_list_path(bare_useresa):
    ue = bare_useresa

    ue.df = pd.DataFrame([
        {
            "puckid": "PK2",
            "pinid": 2,
            "sample_name": "SAMPLE2",
            "desired_exp": "normal",
            "mode": "single",
            "wavelength": 1.0,
            "resolution_limit": 2.0,
            "beamsize": "10x10",
            "max_crystal_size": 30.0,
            "maxhits": 10,
            "total_osc": 10.0,
            "osc_width": 0.1,
            "ln2_flag": 0,
            "pin_flag": "spine",
            "zoomcap_flag": 0,
            "confirmation_require": 0,
            "dose_list": "[1, 2, 3]",
            "dist_list": "",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "raster_hbeam": 10.0,
            "raster_vbeam": 10.0,
            "flux": 1.0e12,
            "exp_raster": 0.02,
            "exp_ds": 0.02,
            "dose_ds": 10.0,
            "reduced_fact": 1.0,
            "ntimes": 1,
        }
    ])

    ue.defineScanCondition()

    row = ue.df.iloc[0]
    assert row["att_raster"] > 0
    assert row["dose_per_frame"] == pytest.approx(0.001)
