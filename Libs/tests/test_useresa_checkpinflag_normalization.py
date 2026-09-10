import pandas as pd
from UserESA import UserESA


def test_checkpinflag_accepts_spaces_and_case():
    u = UserESA.__new__(UserESA)

    u.df = pd.DataFrame([
        {"pin_flag": " Spine "},
        {"pin_flag": "Copper "},
        {"pin_flag": " no-wait "},
        {"pin_flag": " ALS + SSRL "},
    ])

    u.checkPinFlag()

    assert u.df.loc[0, "warm_time"] == 10.0
    assert u.df.loc[1, "warm_time"] == 60.0
    assert u.df.loc[2, "warm_time"] == 0.0
    assert u.df.loc[3, "warm_time"] == 20.0
