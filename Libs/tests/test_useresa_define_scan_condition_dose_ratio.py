import pandas as pd
from unittest.mock import patch
from UserESA import UserESA


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


class DummyKUMA:
    def getDose(self, hbeam, vbeam, flux, energy, exp_raster):
        try:
            return pd.Series([2.0] * len(hbeam), index=hbeam.index)
        except TypeError:
            return 2.0


def test_high_and_ultra_follow_normal_dose_ratio():
    u = UserESA.__new__(UserESA)
    u.logger = DummyLogger()

    u.df = pd.DataFrame([
        {
            "desired_exp": "normal",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "flux": 1.0e13,
            "wavelength": 1.0,
            "exp_raster": 0.01,
            "puckid": "PK1",
            "pinid": 1,
        },
        {
            "desired_exp": "high_dose_scan",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "flux": 1.0e13,
            "wavelength": 1.0,
            "exp_raster": 0.01,
            "puckid": "PK1",
            "pinid": 2,
        },
        {
            "desired_exp": "ultra_high_dose_scan",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "flux": 1.0e13,
            "wavelength": 1.0,
            "exp_raster": 0.01,
            "puckid": "PK1",
            "pinid": 3,
        },
    ])

    with patch("KUMA.KUMA", return_value=DummyKUMA()):
        u.defineScanCondition()

    normal_dose = u.df.loc[0, "dose_per_frame"]
    high_dose = u.df.loc[1, "dose_per_frame"]
    ultra_dose = u.df.loc[2, "dose_per_frame"]

    assert abs(high_dose - normal_dose * 1.5) < 1e-9
    assert abs(ultra_dose - normal_dose * 3.0) < 1e-9
