import numpy as np
import pandas as pd
from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")
u.df = pd.DataFrame([
    {
        "mode": "single",
        "dose_ds": "9",
        "dist_ds": "150",
        "dose_list": np.nan,
        "dist_list": np.nan,
    }
])

u.checkDoseList()
print(u.df.loc[0, "dose_list"], u.df.loc[0, "dist_list"])
print(u.df.loc[0, "dose_ds"], u.df.loc[0, "dist_ds"])