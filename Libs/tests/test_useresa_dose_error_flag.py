import pandas as pd
from unittest.mock import patch
from UserESA import UserESA


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class BigDoseKUMA:
    def getDose(self, hbeam, vbeam, flux, energy, exp_raster):
        try:
            return pd.Series([50.0] * len(hbeam), index=hbeam.index)
        except TypeError:
            return 50.0

def test_dose_error_flag_is_set_when_negative():
    u = UserESA.__new__(UserESA)
    u.logger = DummyLogger()
    u.isDoseError = False

    u.df = pd.DataFrame([
        {
            "desired_exp": "normal",
            "ds_hbeam": 10.0,
            "ds_vbeam": 10.0,
            "flux": 1.0e13,
            "wavelength": 1.0,
            "exp_raster": 0.01,
            "dose_ds": 5.0,
            "puckid": "PK1",
            "pinid": 1,
        }
    ])

    with patch("KUMA.KUMA", return_value=BigDoseKUMA()):
        u.defineScanCondition()

    assert u.isDoseError is True
    assert u.df.loc[0, "dose_ds"] == 0.0